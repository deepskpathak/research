"""In-memory knowledge graph with JSON persistence."""
from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path
from typing import Any, Iterable

from .models import Chunk, Document, Entity, Relation

SCHEMA_VERSION = 1
GRAPH_FILE = "graph.json"


def norm_key(name: str) -> str:
    """Case/whitespace/hyphen-insensitive key used to merge entity names."""
    return re.sub(r"[\s_\-]+", " ", name.strip().lower())


def entity_id(name: str) -> str:
    return "ent-" + norm_key(name).replace(" ", "-")


class KnowledgeGraph:
    def __init__(self) -> None:
        self.entities: dict[str, Entity] = {}
        self.relations: list[Relation] = []
        self.chunks: dict[str, Chunk] = {}
        self.documents: dict[str, Document] = {}
        self._rel_index: dict[tuple[str, str, str], int] = {}
        self._alias_index: dict[str, str] = {}  # norm_key -> entity id
        self._redirect: dict[str, str] = {}  # id of a merged-away entity -> surviving id

    # -- building ---------------------------------------------------------
    def add_document(self, doc: Document) -> None:
        self.documents[doc.id] = doc

    def add_chunk(self, chunk: Chunk) -> None:
        self.chunks[chunk.id] = chunk

    def resolve(self, name_or_id: str) -> str | None:
        """Exact (normalized) lookup of an entity id by id, name or alias."""
        if name_or_id in self.entities:
            return name_or_id
        if name_or_id in self._redirect:
            return self._redirect[name_or_id]
        return self._alias_index.get(norm_key(name_or_id))

    def add_entity(self, e: Entity) -> str:
        """Add an entity, merging into an existing one that shares id, name or alias."""
        target = self.resolve(e.id)
        for n in (e.name, *e.aliases):
            target = target or self._alias_index.get(norm_key(n))
        if target is None:
            merged = Entity(e.id, e.name, e.type, _uniq(e.aliases), _uniq(e.mentions))
            target = e.id
        else:
            old = self.entities[target]
            extra = [n for n in (e.name, *e.aliases) if norm_key(n) != norm_key(old.name)]
            merged = Entity(old.id, old.name, old.type,
                            _uniq((*old.aliases, *extra)), _uniq((*old.mentions, *e.mentions)))
        self.entities[target] = merged
        if e.id != target:
            self._redirect[e.id] = target
        for n in (merged.name, *merged.aliases):
            self._alias_index[norm_key(n)] = target
        return target

    def add_relation(self, r: Relation) -> None:
        s, t = self.resolve(r.source_id), self.resolve(r.target_id)
        if s is None or t is None:
            raise ValueError(f"relation references unknown entity: {r.source_id} -> {r.target_id}")
        key = (s, t, r.type)
        if key in self._rel_index:
            i = self._rel_index[key]
            old = self.relations[i]
            self.relations[i] = Relation(s, t, r.type, _uniq((*old.evidence_chunk_ids, *r.evidence_chunk_ids)))
        else:
            self._rel_index[key] = len(self.relations)
            self.relations.append(Relation(s, t, r.type, _uniq(r.evidence_chunk_ids)))

    def add_extraction(self, entities: Iterable[Entity], relations: Iterable[Relation]) -> None:
        for e in entities:
            self.add_entity(e)
        for r in relations:
            self.add_relation(r)

    def merge(self, other: "KnowledgeGraph") -> None:
        self.documents.update(other.documents)
        self.chunks.update(other.chunks)
        self.add_extraction(other.entities.values(), other.relations)

    # -- queries ----------------------------------------------------------
    def find_entity(self, name: str) -> Entity | None:
        """Case-insensitive, alias-aware lookup; falls back to the shortest prefix match."""
        key = norm_key(name)
        if not key:
            return None
        eid = self._alias_index.get(key)
        if eid:
            return self.entities[eid]
        best: tuple[int, str, str] | None = None
        for k, i in self._alias_index.items():
            if k.startswith(key) and (best is None or (len(k), k) < best[:2]):
                best = (len(k), k, i)
        return self.entities[best[2]] if best else None

    def neighbors(self, entity_id: str, depth: int = 1) -> list[Entity]:
        """Entities within `depth` hops (undirected), excluding the start, nearest first."""
        start = self.resolve(entity_id)
        if start is None:
            return []
        adj: dict[str, set[str]] = {}
        for r in self.relations:
            adj.setdefault(r.source_id, set()).add(r.target_id)
            adj.setdefault(r.target_id, set()).add(r.source_id)
        seen = {start}
        out: list[Entity] = []
        q = deque([(start, 0)])
        while q:
            cur, d = q.popleft()
            if d >= depth:
                continue
            for nxt in sorted(adj.get(cur, ())):
                if nxt not in seen:
                    seen.add(nxt)
                    out.append(self.entities[nxt])
                    q.append((nxt, d + 1))
        return out

    def chunks_for_entity(self, entity_id: str) -> list[Chunk]:
        eid = self.resolve(entity_id)
        if eid is None:
            return []
        return [self.chunks[c] for c in self.entities[eid].mentions if c in self.chunks]

    def stats(self) -> dict[str, int]:
        return {"documents": len(self.documents), "chunks": len(self.chunks),
                "entities": len(self.entities), "relations": len(self.relations)}

    def dangling_evidence(self) -> list[str]:
        """Evidence chunk ids referenced by relations but absent from the graph."""
        return sorted({c for r in self.relations for c in r.evidence_chunk_ids if c not in self.chunks})

    # -- persistence ------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "documents": [d.to_dict() for _, d in sorted(self.documents.items())],
            "chunks": [c.to_dict() for _, c in sorted(self.chunks.items())],
            "entities": [e.to_dict() for _, e in sorted(self.entities.items())],
            "relations": [r.to_dict() for r in self.relations],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "KnowledgeGraph":
        version = d.get("schema_version")
        if version != SCHEMA_VERSION:
            raise ValueError(f"unsupported graph schema_version {version!r}; expected {SCHEMA_VERSION}")
        g = cls()
        for x in d.get("documents", []):
            g.add_document(Document.from_dict(x))
        for x in d.get("chunks", []):
            g.add_chunk(Chunk.from_dict(x))
        g.add_extraction((Entity.from_dict(x) for x in d.get("entities", [])),
                         (Relation.from_dict(x) for x in d.get("relations", [])))
        return g

    def save(self, directory: str | Path) -> Path:
        p = Path(directory)
        p.mkdir(parents=True, exist_ok=True)
        path = p / GRAPH_FILE
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, directory: str | Path) -> "KnowledgeGraph":
        return cls.from_dict(json.loads((Path(directory) / GRAPH_FILE).read_text(encoding="utf-8")))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, KnowledgeGraph) and self.to_dict() == other.to_dict()

    __hash__ = None  # type: ignore[assignment]


def _uniq(items: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))
