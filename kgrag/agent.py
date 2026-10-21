"""Agentic RAG loop: an LLM (or a deterministic offline policy) drives retrieval tools
and returns an extractive, cited answer.

Action protocol (LLM -> agent), one JSON object per reply:
    {"tool": "search", "args": {"query": "..."}}
    {"tool": "lookup_entity", "args": {"name": "..."}}
    {"tool": "expand", "args": {"entity": "...", "depth": 1}}
    {"tool": "finish", "args": {"answer": "...", "citations": [{"chunk_id": "...", "quote": "..."}]}}

Step accounting: every tool call (including finish) is one step and at most ``max_steps``
are taken. Trace entries with tool == "fallback" are bookkeeping, not steps.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from .llm import LLMClient, LLMError, OfflineLLM
from .models import Chunk
from .retrieve import STOPWORDS, tokenize

NOT_FOUND = "The corpus does not contain the information needed to answer this question."
TOOLS = ("search", "lookup_entity", "expand", "finish")
MAX_EVIDENCE_SENTENCES = 3
_SENT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-_'][A-Za-z0-9]+)*")

_SYSTEM = (
    "You answer questions using ONLY a knowledge graph and document corpus, via tools. "
    "Reply with exactly one JSON object per turn: {\"tool\": NAME, \"args\": {...}}. Tools: "
    "search(query), lookup_entity(name), expand(entity, depth), "
    "finish(answer, citations). citations is a list of {\"chunk_id\", \"quote\"} where quote is "
    "copied verbatim from a retrieved chunk. If the corpus lacks the answer, finish with an "
    "answer saying so and no citations."
)


@dataclass
class AgentResult:
    answer: str
    citations: list[dict[str, str]] = field(default_factory=list)  # doc_path, chunk_id, quote
    trace: list[dict[str, Any]] = field(default_factory=list)
    truncated: bool = False  # True when max_steps ran out before the policy finished


class _Malformed(ValueError):
    pass


def parse_action(text: str) -> tuple[str, dict[str, Any]]:
    """Parse the first JSON object in `text` into (tool, args); raise _Malformed otherwise."""
    s = text.strip()
    start = s.find("{")
    if start < 0:
        raise _Malformed("no JSON object in reply")
    try:
        obj, _ = json.JSONDecoder().raw_decode(s[start:])
    except json.JSONDecodeError as e:
        raise _Malformed(f"invalid JSON: {e.msg}") from None
    if not isinstance(obj, dict):
        raise _Malformed("action must be a JSON object")
    tool = obj.get("tool", obj.get("action"))
    args = obj.get("args", {})
    if tool not in TOOLS:
        raise _Malformed(f"unknown tool {tool!r}")
    if not isinstance(args, dict):
        raise _Malformed("args must be an object")
    required = {"search": ("query",), "lookup_entity": ("name",), "expand": ("entity",),
                "finish": ("answer",)}[tool]
    missing = [k for k in required if not isinstance(args.get(k), str)]
    if missing:
        raise _Malformed(f"missing/invalid args for {tool}: {', '.join(missing)}")
    return tool, args


def _squash(s: str) -> str:
    return " ".join(s.split())


class Agent:
    def __init__(self, graph: Any, retriever: Any, llm: LLMClient, max_steps: int = 5,
                 k: int = 5) -> None:
        self.graph, self.retriever, self.llm = graph, retriever, llm
        self.max_steps = max(1, max_steps)
        self.k = k

    # -- public ------------------------------------------------------------
    def run(self, question: str) -> AgentResult:
        st = _State(question)
        if isinstance(self.llm, OfflineLLM):
            return self._offline(st)
        return self._llm_loop(st)

    ask = run

    # -- tools (each returns a JSON-able observation) ------------------------
    def _path(self, chunk: Chunk) -> str:
        doc = getattr(self.graph, "documents", {}).get(chunk.doc_id)
        if doc is not None:
            return doc.path
        return self.retriever.index.doc_paths.get(chunk.doc_id, chunk.doc_id)

    def _remember(self, st: "_State", chunk: Chunk, path: str | None = None) -> None:
        st.evidence.setdefault(chunk.id, (chunk, path or self._path(chunk)))

    def search(self, st: "_State", query: str) -> dict[str, Any]:
        hits = self.retriever.retrieve(query, k=self.k)
        for h in hits:
            self._remember(st, h.chunk, h.source_path)
        return {"results": [{"chunk_id": h.chunk.id, "doc_path": h.source_path,
                             "score": round(h.score, 4), "text": h.chunk.text[:400]}
                            for h in hits]}

    def lookup_entity(self, st: "_State", name: str) -> dict[str, Any]:
        e = self.graph.find_entity(name)
        if e is None:
            return {"found": False, "name": name}
        rels = []
        for r in self.graph.relations:
            if r.source_id == e.id or r.target_id == e.id:
                out = r.source_id == e.id
                other = self.graph.entities.get(r.target_id if out else r.source_id)
                if other is not None:
                    rels.append({"type": r.type, "direction": "out" if out else "in",
                                 "entity": other.name})
        chunks = self.graph.chunks_for_entity(e.id)
        for c in chunks:
            self._remember(st, c)
        st.entities.setdefault(e.id, e.name)
        return {"found": True, "name": e.name, "type": e.type, "aliases": list(e.aliases),
                "relations": rels[:20], "chunk_ids": [c.id for c in chunks]}

    def expand(self, st: "_State", entity: str, depth: int = 1) -> dict[str, Any]:
        e = self.graph.find_entity(entity)
        if e is None:
            return {"found": False, "entity": entity}
        try:
            depth = max(1, min(int(depth), 2))
        except (TypeError, ValueError):
            depth = 1
        nbrs = self.graph.neighbors(e.id, depth)
        for n in nbrs:
            for c in self.graph.chunks_for_entity(n.id):
                self._remember(st, c)
        return {"found": True, "entity": e.name, "neighbors": [n.name for n in nbrs[:20]]}

    def _call(self, st: "_State", tool: str, args: dict[str, Any]) -> dict[str, Any]:
        if tool == "search":
            return self.search(st, args["query"])
        if tool == "lookup_entity":
            return self.lookup_entity(st, args["name"])
        return self.expand(st, args["entity"], args.get("depth", 1))

    def _step(self, st: "_State", tool: str, args: dict[str, Any]) -> dict[str, Any]:
        obs = self._call(st, tool, args)
        st.trace.append({"step": st.steps + 1, "tool": tool, "args": args,
                         "observation": _summarise(obs)})
        st.steps += 1
        return obs

    # -- LLM-driven loop -----------------------------------------------------
    def _llm_loop(self, st: "_State") -> AgentResult:
        messages: list[dict[str, str]] = [{"role": "user", "content": f"Question: {st.question}"}]
        while st.steps < self.max_steps:
            parsed = self._next_action(st, messages)
            if parsed is None:  # malformed twice or LLM failure
                return self._offline(st)
            tool, args = parsed
            if tool == "finish":
                res = self._finish_from_llm(st, args)
                if res is not None:
                    return res
                st.trace.append({"step": st.steps + 1, "tool": "fallback",
                                 "reason": "finish had no verifiable citations"})
                return self._offline(st)
            obs = self._step(st, tool, args)
            messages.append({"role": "assistant", "content": json.dumps({"tool": tool, "args": args})})
            messages.append({"role": "user", "content": "Observation: " + json.dumps(obs)[:4000]})
        res = self._compose(st)
        res.truncated = True
        return res

    def _next_action(self, st: "_State", messages: list[dict[str, str]]):
        msgs = list(messages)
        reason = ""
        for attempt in range(2):  # one retry on malformed output
            try:
                reply = self.llm.complete(_SYSTEM, msgs)
                return parse_action(reply)
            except _Malformed as e:
                reason = str(e)
                msgs = msgs + [{"role": "assistant", "content": str(reply)[:500]},
                               {"role": "user", "content": f"Invalid action ({reason}). "
                                "Reply with ONLY a JSON object {\"tool\":..., \"args\":{...}}."}]
            except LLMError as e:
                reason = f"LLM error: {e}"
                break
        st.trace.append({"step": st.steps + 1, "tool": "fallback",
                         "reason": f"{reason}; using offline policy"})
        return None

    def _finish_from_llm(self, st: "_State", args: dict[str, Any]) -> AgentResult | None:
        cites = []
        for c in args.get("citations") or []:
            if not isinstance(c, dict):
                continue
            hit = st.evidence.get(str(c.get("chunk_id")))
            quote = str(c.get("quote", "")).strip()
            if hit and quote and _squash(quote) in _squash(hit[0].text):
                cites.append({"doc_path": hit[1], "chunk_id": hit[0].id, "quote": quote})
        if not cites:
            return None
        st.trace.append({"step": st.steps + 1, "tool": "finish",
                         "args": {"answer": args["answer"], "citations": len(cites)}})
        return AgentResult(args["answer"], cites, st.trace)

    # -- deterministic offline policy ----------------------------------------
    def _mentions(self, question: str) -> list[str]:
        """Entity names mentioned in the question (longest n-grams first, exact alias match)."""
        words = _WORD_RE.findall(question)
        found: list[str] = []
        used: set[int] = set()
        for n in (4, 3, 2, 1):
            for i in range(len(words) - n + 1):
                span = range(i, i + n)
                gram = words[i:i + n]
                if used.intersection(span):
                    continue
                if gram[0].lower() in STOPWORDS or gram[-1].lower() in STOPWORDS:
                    continue
                eid = self.graph.resolve(" ".join(gram))
                if eid is not None and eid not in found:
                    found.append(eid)
                    used.update(span)
        return [self.graph.entities[e].name for e in found]

    def _offline(self, st: "_State") -> AgentResult:
        names = self._mentions(st.question)
        plan: list[tuple[str, dict[str, Any]]] = [("search", {"query": st.question})]
        if len(names) >= 2:
            plan += [("search", {"query": n}) for n in names]
        plan += [("lookup_entity", {"name": n}) for n in names]
        if len(names) >= 2:  # follow one hop for multi-entity questions
            plan += [("expand", {"entity": n, "depth": 1}) for n in names]
        for tool, args in plan:
            if st.steps >= self.max_steps - 1:  # keep one step for finish
                break
            self._step(st, tool, args)
        res = self._compose(st)
        st.trace.append({"step": st.steps + 1, "tool": "finish",
                         "args": {"citations": len(res.citations)}})
        st.steps += 1
        return res

    def _compose(self, st: "_State") -> AgentResult:
        q = set(tokenize(st.question))
        scored = []  # (overlap, order, chunk, path, sentence)
        order = 0
        for chunk, path in st.evidence.values():
            for raw in _SENT_RE.split(chunk.text):
                sent = raw.strip()
                if not sent or sent.startswith("#"):
                    continue
                overlap = q & set(tokenize(sent))
                if overlap:
                    scored.append((overlap, order, chunk, path, sent))
                order += 1
        scored.sort(key=lambda t: (-len(t[0]), t[1]))
        if not scored or not _relevant(scored[0][0], q):
            return AgentResult(NOT_FOUND, [], st.trace)
        picked = [scored[0]]
        covered = set(scored[0][0])
        while len(picked) < MAX_EVIDENCE_SENTENCES:
            docs = {p[2].doc_id for p in picked}
            best = None
            for t in scored:
                new = t[0] - covered
                if not new or t in picked:
                    continue
                key = (t[2].doc_id not in docs, len(new), len(t[0]), -t[1])
                if best is None or key > best[0]:
                    best = (key, t)
            if best is None:
                break
            picked.append(best[1])
            covered |= best[1][0]
        cites = [{"doc_path": p[3], "chunk_id": p[2].id, "quote": p[4]} for p in picked]
        answer = " ".join(f"{p[4]} [{i}]" for i, p in enumerate(picked, 1))
        return AgentResult(answer, cites, st.trace)


def _relevant(overlap: set[str], q: set[str]) -> bool:
    """Relevance gate: at least two query terms, or half of them, in the best sentence."""
    return len(overlap) >= 2 or (bool(q) and len(overlap) / len(q) >= 0.5)


@dataclass
class _State:
    question: str
    evidence: dict[str, tuple[Chunk, str]] = field(default_factory=dict)
    entities: dict[str, str] = field(default_factory=dict)
    trace: list[dict[str, Any]] = field(default_factory=list)
    steps: int = 0


def _summarise(obs: dict[str, Any]) -> str:
    s = json.dumps(obs, ensure_ascii=False)
    return s if len(s) <= 300 else s[:297] + "..."
