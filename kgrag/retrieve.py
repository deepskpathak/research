"""Hybrid retrieval: BM25 lexical search fused with knowledge-graph expansion.

Fusion: Reciprocal Rank Fusion (RRF). Each ranked list (lexical, graph) contributes
``1 / (RRF_K + rank)`` per chunk (rank starts at 1); contributions are summed, so
chunks found by both channels outrank those found by one. The graph list is ordered
by hop distance from the linked query entities (closer first), then discovery order.

The graph is duck-typed against the T3 KnowledgeGraph interface:
``find_entity(name)``, ``neighbors(entity_id)``, ``chunks_for_entity(entity_id)``.
Each may return objects (Entity / Chunk) or plain id strings; both are accepted.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kgrag.models import Chunk

RRF_K = 60
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-_'][a-z0-9]+)*")
STOPWORDS = frozenset("""
a an and are as at be but by for from has have he her his i if in into is it its of on or
our she so than that the their them then there these they this to was we were what when
where which who whom why will with you your do does did how can could should would about
not no
""".split())


def tokenize(text: str) -> list[str]:
    """Lowercase, split on word characters, drop stopwords."""
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75,
                 doc_paths: dict[str, str] | None = None) -> None:
        self.k1, self.b = k1, b
        self.doc_paths: dict[str, str] = dict(doc_paths or {})  # doc_id -> source path
        self.chunks: dict[str, Chunk] = {}
        self._tf: dict[str, Counter] = {}
        self._len: dict[str, int] = {}
        self._df: Counter = Counter()
        self._avgdl = 0.0

    @classmethod
    def build(cls, chunks: list[Chunk], doc_paths: dict[str, str] | None = None,
              **kw: Any) -> "BM25Index":
        idx = cls(doc_paths=doc_paths, **kw)
        for c in chunks:
            idx.chunks[c.id] = c  # duplicate ids collapse to the last one
        idx._rebuild()
        return idx

    def _rebuild(self) -> None:
        self._tf, self._len, self._df = {}, {}, Counter()
        for cid, c in self.chunks.items():
            toks = tokenize(c.text)
            self._tf[cid] = Counter(toks)
            self._len[cid] = len(toks)
            self._df.update(self._tf[cid].keys())
        self._avgdl = sum(self._len.values()) / len(self._len) if self._len else 0.0

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        terms = set(tokenize(query))
        if not terms or not self.chunks or k <= 0:
            return []
        n = len(self.chunks)
        scores: dict[str, float] = {}
        for t in terms:
            df = self._df.get(t, 0)
            if not df:
                continue
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            for cid, tf in self._tf.items():
                f = tf.get(t, 0)
                if not f:
                    continue
                norm = 1 - self.b + self.b * self._len[cid] / (self._avgdl or 1.0)
                scores[cid] = scores.get(cid, 0.0) + idf * f * (self.k1 + 1) / (f + self.k1 * norm)
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:k]

    def save(self, path: str | Path) -> None:
        data = {"k1": self.k1, "b": self.b, "doc_paths": self.doc_paths,
                "chunks": [c.to_dict() for c in self.chunks.values()]}
        Path(path).write_text(json.dumps(data), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "BM25Index":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.build([Chunk.from_dict(d) for d in data["chunks"]],
                         doc_paths=data.get("doc_paths"), k1=data["k1"], b=data["b"])


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float
    source_path: str
    via: tuple[str, ...]  # subset of ("lexical", "graph"), in that order


def _as_list(x: Any) -> list:
    if x is None:
        return []
    if isinstance(x, (list, tuple, set, frozenset)):
        return list(x)
    return [x]


def _id(x: Any) -> str:
    return x if isinstance(x, str) else x.id


class HybridRetriever:
    def __init__(self, index: BM25Index, graph: Any, hops: int = 2,
                 max_graph_chunks: int = 50) -> None:
        self.index, self.graph = index, graph
        self.hops = max(0, min(hops, 2))
        self.max_graph_chunks = max_graph_chunks

    def _link_entities(self, query: str) -> list[str]:
        words = _TOKEN_RE.findall(query.lower())
        seen: dict[str, None] = {}
        for n in (3, 2, 1):  # longest phrases first
            for i in range(len(words) - n + 1):
                gram = words[i:i + n]
                if all(w in STOPWORDS for w in gram):
                    continue
                for e in _as_list(self.graph.find_entity(" ".join(gram))):
                    seen.setdefault(_id(e))
        return list(seen)

    def _graph_ranking(self, query: str) -> list[str]:
        """Chunk ids ordered by hop distance from entities linked to the query."""
        frontier = self._link_entities(query)
        visited = set(frontier)
        ordered: dict[str, None] = {}
        for hop in range(self.hops + 1):
            for eid in frontier:
                for c in _as_list(self.graph.chunks_for_entity(eid)):
                    ordered.setdefault(_id(c))
            if hop == self.hops:
                break
            nxt = []
            for eid in frontier:
                for nb in _as_list(self.graph.neighbors(eid)):
                    nid = _id(nb)
                    if nid not in visited:
                        visited.add(nid)
                        nxt.append(nid)
            frontier = nxt
        return list(ordered)[:self.max_graph_chunks]

    def retrieve(self, query: str, k: int = 5, lexical_k: int = 20) -> list[RetrievedChunk]:
        if not tokenize(query):
            return []
        lexical = [cid for cid, _ in self.index.search(query, lexical_k)]
        graph = [cid for cid in self._graph_ranking(query) if cid in self.index.chunks]
        fused: dict[str, float] = {}
        via: dict[str, set[str]] = {}
        for name, ranking in (("lexical", lexical), ("graph", graph)):
            for rank, cid in enumerate(ranking, start=1):
                fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + rank)
                via.setdefault(cid, set()).add(name)
        top = sorted(fused.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
        out = []
        for cid, score in top:
            chunk = self.index.chunks[cid]
            out.append(RetrievedChunk(
                chunk=chunk, score=score,
                source_path=self.index.doc_paths.get(chunk.doc_id, chunk.doc_id),
                via=tuple(v for v in ("lexical", "graph") if v in via[cid])))
        return out
