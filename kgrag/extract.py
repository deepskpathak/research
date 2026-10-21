"""Entity/relation extraction: deterministic heuristics plus an LLM extractor with fallback."""
from __future__ import annotations

import json
import logging
import re
from itertools import combinations
from typing import Protocol, Sequence

from .graph import entity_id, norm_key
from .llm import LLMClient, LLMError
from .models import Chunk, Entity, Relation

log = logging.getLogger(__name__)

Extraction = tuple[list[Entity], list[Relation]]


class Extractor(Protocol):
    def extract(self, chunks: Sequence[Chunk]) -> Extraction: ...


_CAP = r"[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*"
_PHRASE_RE = re.compile(rf"\b{_CAP}(?:[ \t]+(?:of[ \t]+)?{_CAP})+\b")
_ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,7}\b")
_ACRONYM_DEF_RE = re.compile(rf"\b({_CAP}(?:[ \t]+(?:of[ \t]+)?{_CAP})+)[ \t]*\(([A-Z][A-Z0-9]{{1,7}})\)")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", re.M)
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_LEADING_STOP = {"The", "A", "An", "This", "That", "These", "Those", "In", "On", "It", "We", "See"}
_REL_PATTERNS = (
    (re.compile(r"^(?:is|are) (?:a|an|the)$", re.I), "is_a"),
    (re.compile(r"^(?:uses|use|used|using)$", re.I), "uses"),
    (re.compile(r"^(?:is |are )?part of$", re.I), "part_of"),
)


def _clean_phrase(p: str) -> str | None:
    words = p.split()
    while words and words[0] in _LEADING_STOP:
        words.pop(0)
    return " ".join(words) if len(words) >= 2 else None


def _acronym_map(chunks: Sequence[Chunk]) -> dict[str, str]:
    """ACRONYM -> expansion, from 'Expansion (ACRONYM)' definitions anywhere in the corpus."""
    out: dict[str, str] = {}
    for c in chunks:
        for m in _ACRONYM_DEF_RE.finditer(c.text):
            phrase = _clean_phrase(m.group(1))
            if phrase:
                out.setdefault(m.group(2), phrase)
    return out


class HeuristicExtractor:
    """Deterministic, offline extractor."""

    def extract(self, chunks: Sequence[Chunk]) -> Extraction:
        acr = _acronym_map(chunks)
        names: dict[str, str] = {}      # key -> display name
        aliases: dict[str, set[str]] = {}
        types: dict[str, str] = {}
        mentions: dict[str, list[str]] = {}
        rels: dict[tuple[str, str, str], list[str]] = {}

        def register(surface: str, kind: str) -> str:
            canonical = acr.get(surface, surface)
            key = norm_key(canonical)
            names.setdefault(key, canonical)
            if surface != canonical:
                aliases.setdefault(key, set()).add(surface)
            if types.get(key) in (None, "acronym"):
                types[key] = kind
            return key

        for ch in chunks:
            keys_in_chunk: dict[str, None] = {}
            for m in _HEADING_RE.finditer(ch.text):
                h = re.sub(r"[*_`]", "", m.group(1)).strip()
                if h:
                    k = register(h, "concept")
                    keys_in_chunk[k] = None
            spans: list[tuple[int, int, str]] = []
            for m in _PHRASE_RE.finditer(ch.text):
                p = _clean_phrase(m.group(0))
                if p:
                    spans.append((m.end() - len(p), m.end(), register(p, "concept")))
            for m in _ACRONYM_RE.finditer(ch.text):
                spans.append((m.start(), m.end(), register(m.group(0), "acronym")))
            spans.sort()
            for s, e, k in spans:
                keys_in_chunk[k] = None
            for k in keys_in_chunk:
                if ch.id not in mentions.setdefault(k, []):
                    mentions[k].append(ch.id)
            # co-occurrence
            for a, b in combinations(sorted(keys_in_chunk), 2):
                rels.setdefault((a, b, "related_to"), []).append(ch.id)
            # verb patterns between adjacent mentions inside one sentence
            sent_start = 0
            bounds = [m.end() for m in _SENT_SPLIT_RE.finditer(ch.text)] + [len(ch.text)]
            for end in bounds:
                sent = [(s, e, k) for s, e, k in spans if s >= sent_start and e <= end]
                for (s1, e1, k1), (s2, e2, k2) in zip(sent, sent[1:]):
                    if k1 == k2:
                        continue
                    between = ch.text[e1:s2].strip(" \t),:")
                    for pat, rtype in _REL_PATTERNS:
                        if pat.match(between):
                            rels.setdefault((k1, k2, rtype), []).append(ch.id)
                            break
                sent_start = end

        entities = [
            Entity(entity_id(names[k]), names[k], types.get(k, "concept"),
                   tuple(sorted(aliases.get(k, ()))), tuple(mentions.get(k, ())))
            for k in sorted(names) if k in mentions
        ]
        relations = [
            Relation(entity_id(names[a]), entity_id(names[b]), t, tuple(dict.fromkeys(ev)))
            for (a, b, t), ev in sorted(rels.items())
        ]
        return entities, relations


_SYSTEM = (
    "You extract a knowledge graph from text. Reply with ONLY JSON of the form "
    '{"entities":[{"name":str,"type":str,"aliases":[str]}],'
    '"relations":[{"source":str,"target":str,"type":str}]}. '
    "Use snake_case relation types such as is_a, uses, part_of, related_to."
)


def _parse_llm(text: str, chunk: Chunk) -> Extraction:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    data = json.loads(s)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON is not an object")
    ents: dict[str, Entity] = {}
    for x in data["entities"]:
        name = str(x["name"]).strip()
        if not name:
            raise ValueError("empty entity name")
        ents[norm_key(name)] = Entity(entity_id(name), name, str(x.get("type") or "concept"),
                                      tuple(str(a) for a in x.get("aliases", ())), (chunk.id,))
    rels: list[Relation] = []
    for x in data["relations"]:
        a, b = ents.get(norm_key(str(x["source"]))), ents.get(norm_key(str(x["target"])))
        if a is None or b is None:
            raise ValueError(f"relation references undeclared entity: {x}")
        rels.append(Relation(a.id, b.id, str(x["type"]), (chunk.id,)))
    return list(ents.values()), rels


class LLMExtractor:
    """Asks an LLM for JSON per chunk; on any failure logs the error and uses heuristics for that chunk."""

    def __init__(self, llm: LLMClient, fallback: Extractor | None = None) -> None:
        self.llm = llm
        self.fallback = fallback or HeuristicExtractor()

    def extract(self, chunks: Sequence[Chunk]) -> Extraction:
        from .graph import KnowledgeGraph  # merge helper; avoids duplicating merge rules

        g = KnowledgeGraph()
        for ch in chunks:
            try:
                raw = self.llm.complete(_SYSTEM, [{"role": "user", "content": ch.text}])
                ents, rels = _parse_llm(raw, ch)
            except (ValueError, KeyError, TypeError, LLMError) as e:
                log.warning("LLM extraction failed for chunk %s (%s: %s); using heuristic fallback",
                            ch.id, type(e).__name__, e)
                ents, rels = self.fallback.extract([ch])
            g.add_extraction(ents, rels)
        return list(g.entities.values()), list(g.relations)
