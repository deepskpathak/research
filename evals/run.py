"""Offline eval runner: builds the store from research/ with OfflineLLM, scores six categories."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from kgrag.agent import NOT_FOUND, Agent
from kgrag.extract import HeuristicExtractor
from kgrag.graph import KnowledgeGraph, norm_key
from kgrag.ingest import chunk_document, load_corpus
from kgrag.llm import OfflineLLM
from kgrag.retrieve import BM25Index, HybridRetriever

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(__file__).resolve().parent / "data"
DEFAULT_CORPUS = ROOT / "research"
DEFAULT_RESULTS = ROOT / "evals" / "results.json"


def _load(name: str) -> Any:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def build(corpus: Path) -> tuple[KnowledgeGraph, BM25Index, list]:
    """Same pipeline as `kgrag ingest`, in memory."""
    docs = load_corpus(corpus)
    graph, chunks = KnowledgeGraph(), []
    for d in docs:
        graph.add_document(d)
        for c in chunk_document(d):
            graph.add_chunk(c)
            chunks.append(c)
    graph.add_extraction(*HeuristicExtractor().extract(chunks))
    index = BM25Index.build(chunks, doc_paths={d.id: d.path for d in docs})
    return graph, index, chunks


def _stage_corpus(corpus: Path, exclude: list[str], dest: Path) -> Path:
    """Copy the corpus minus excluded files. research/README.md holds the answer key
    (literal Q/A pairs), so indexing it would let questions be answered by the key."""
    for p in corpus.rglob("*"):
        rel = p.relative_to(corpus)
        if p.is_file() and rel.as_posix() not in exclude:
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest / rel)
    return dest


def _ratio(num: float, den: float) -> float:
    return num / den if den else 0.0


def eval_retrieval(retriever: HybridRetriever, items: list[dict], k: int) -> dict[str, Any]:
    hits, rr, per = 0.0, 0.0, []
    for it in items:
        gold = set(it["gold_sources"])
        docs: list[str] = []
        for r in retriever.retrieve(it["question"], k=k):
            if r.source_path not in docs:
                docs.append(r.source_path)
        recall = _ratio(len(gold & set(docs)), len(gold))
        first = next((i for i, d in enumerate(docs, 1) if d in gold), None)
        hits += recall
        rr += 1 / first if first else 0.0
        per.append({"id": it["id"], "recall": recall, "rank": first, "dropped_graph_chunks":
                    retriever.last_stats["dropped_graph_chunks"]})
    n = len(items)
    return {"recall_at_k": hits / n, "mrr": rr / n, "k": k, "n": n, "items": per}


def eval_multi_hop(agent: Agent, items: list[dict]) -> dict[str, Any]:
    cov, hit, per = 0.0, 0.0, []
    for it in items:
        res = agent.run(it["question"])
        cited = {c["doc_path"] for c in res.citations}
        gold = set(it["gold_sources"])
        c = _ratio(len(gold & cited), len(gold))
        h = float(it["answer_contains"].lower() in res.answer.lower())
        cov, hit = cov + c, hit + h
        per.append({"id": it["id"], "coverage": c, "answer_hit": h, "cited": sorted(cited)})
    n = len(items)
    return {"coverage": cov / n, "answer_hit": hit / n, "n": n, "items": per}


def eval_grounded(agent: Agent, items: list[dict], corpus: Path) -> dict[str, Any]:
    """Citation accuracy is checked against the full source file text, not the chunk."""
    total = ok = answered = 0
    per = []
    for it in items:
        res = agent.run(it["question"])
        answered += bool(res.citations)
        bad = []
        for c in res.citations:
            total += 1
            f = corpus / c["doc_path"]
            text = f.read_text(encoding="utf-8") if f.is_file() else ""
            if c["quote"] and c["quote"] in text:
                ok += 1
            else:
                bad.append(c["quote"])
        per.append({"id": it["id"], "citations": len(res.citations), "unverified": bad})
    n = len(items)
    return {"citation_accuracy": _ratio(ok, total), "answers_with_citation": answered / n,
            "citations": total, "n": n, "items": per}


def eval_refusal(agent: Agent, on: list[dict], off: list[dict]) -> dict[str, Any]:
    def refused(q: str) -> bool:
        r = agent.run(q)
        return r.answer == NOT_FOUND and not r.citations
    refusals = [refused(i["question"]) for i in off]
    false_refusals = [refused(i["question"]) for i in on]
    return {"refusal_rate": sum(refusals) / len(off),
            "false_refusal_rate": sum(false_refusals) / len(on),
            "n": len(on) + len(off),
            "missed_refusals": [i["id"] for i, r in zip(off, refusals) if not r],
            "false_refusals": [i["id"] for i, r in zip(on, false_refusals) if r]}


def eval_extraction(gold: dict, corpus: Path) -> dict[str, Any]:
    graph, _, _ = build(corpus)
    got = {norm_key(e.name) for e in graph.entities.values()}
    want = {norm_key(n) for n in gold["entities"]}
    tp = len(got & want)
    pairs = {frozenset((norm_key(graph.entities[r.source_id].name),
                        norm_key(graph.entities[r.target_id].name))) for r in graph.relations}
    want_rel = {frozenset(norm_key(x) for x in p) for p in gold["relations"]}
    rel_tp = len(pairs & want_rel)
    merged = [len({e.id for n in grp if (e := graph.find_entity(n))}) == 1
              and all(graph.find_entity(n) for n in grp) for grp in gold["plural_groups"]]
    return {"entity_precision": _ratio(tp, len(got)), "entity_recall": _ratio(tp, len(want)),
            "relation_precision": _ratio(rel_tp, len(pairs)),
            "relation_recall": _ratio(rel_tp, len(want_rel)),
            "plural_merge": sum(merged) / len(merged),
            "n": len(want) + len(want_rel) + len(merged),
            "missing_entities": sorted(want - got), "extra_entities": sorted(got - want)}


def _fingerprint(corpus: Path, out: Path) -> dict[str, bytes]:
    graph, index, chunks = build(corpus)
    graph.save(out)
    index.save(out / "bm25.json")
    files = {p.name: p.read_bytes() for p in sorted(out.iterdir())}
    files["chunk_ids"] = "\n".join(c.id for c in chunks).encode()
    return files


def eval_idempotency(corpus: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as t:
        a, b = Path(t) / "a", Path(t) / "b"
        a.mkdir(), b.mkdir()
        fa, fb = _fingerprint(corpus, a), _fingerprint(corpus, b)
    same = [k for k in fa if fa[k] == fb.get(k)]
    return {"idempotency": len(same) / len(fa) if fa.keys() == fb.keys() else 0.0,
            "artifacts": sorted(fa), "differing": sorted(set(fa) - set(same)), "n": 1}


def run_all(corpus: Path = DEFAULT_CORPUS) -> dict[str, Any]:
    q, th = _load("questions.json"), _load("thresholds.json")
    with tempfile.TemporaryDirectory() as t:
        staged = _stage_corpus(corpus, q["corpus_exclude"], Path(t))
        graph, index, _ = build(staged)
        # top_entities and last_stats are the T3/T4 interfaces.
        top = graph.stats(5)["top_entities"]
        retriever = HybridRetriever(index, graph)
        agent = Agent(graph, retriever, OfflineLLM())
        k = int(th["retrieval_k"])
        cats = {
            "retrieval": eval_retrieval(retriever, q["retrieval"], k),
            "multi_hop": eval_multi_hop(agent, q["multi_hop"]),
            "grounded": eval_grounded(agent, q["grounded"], staged),
            "refusal": eval_refusal(agent, q["on_topic"], q["off_topic"]),
            "extraction": eval_extraction(_load("extraction_gold.json"),
                                          DATA / "extraction_corpus"),
            "idempotency": eval_idempotency(staged),
        }
    checks = [
        ("retrieval", f"recall@{k}", cats["retrieval"]["recall_at_k"], "retrieval_recall_at_k", ">="),
        ("retrieval", "MRR", cats["retrieval"]["mrr"], "retrieval_mrr", ">="),
        ("multi_hop", "gold doc coverage", cats["multi_hop"]["coverage"], "multi_hop_coverage", ">="),
        ("multi_hop", "answer hit", cats["multi_hop"]["answer_hit"], "multi_hop_answer_hit", ">="),
        ("grounded", "citation accuracy", cats["grounded"]["citation_accuracy"], "citation_accuracy", ">="),
        ("grounded", "answers with citation", cats["grounded"]["answers_with_citation"],
         "answers_with_citation", ">="),
        ("refusal", "refusal rate", cats["refusal"]["refusal_rate"], "refusal_rate", ">="),
        ("refusal", "false refusal rate", cats["refusal"]["false_refusal_rate"],
         "false_refusal_rate_max", "<="),
        ("extraction", "entity precision", cats["extraction"]["entity_precision"],
         "extraction_entity_precision", ">="),
        ("extraction", "entity recall", cats["extraction"]["entity_recall"],
         "extraction_entity_recall", ">="),
        ("extraction", "relation recall", cats["extraction"]["relation_recall"],
         "extraction_relation_recall", ">="),
        ("extraction", "plural merge", cats["extraction"]["plural_merge"],
         "extraction_plural_merge", ">="),
        ("idempotency", "identical artifacts", cats["idempotency"]["idempotency"], "idempotency", ">="),
    ]
    rows = [{"category": c, "metric": m, "value": round(v, 4), "threshold": th[key], "op": op,
             "passed": v >= th[key] if op == ">=" else v <= th[key]} for c, m, v, key, op in checks]
    return {"questions": sum(c["n"] for c in cats.values() if c is not cats["idempotency"]),
            "top_entities": top, "categories": cats, "metrics": rows,
            "passed": all(r["passed"] for r in rows)}


def format_table(result: dict[str, Any]) -> str:
    lines = [f"{'category':<12} {'metric':<24} {'value':>7} {'threshold':>10}  status"]
    for r in result["metrics"]:
        lines.append(f"{r['category']:<12} {r['metric']:<24} {r['value']:>7.3f} "
                     f"{r['op']}{r['threshold']:>8}  {'PASS' if r['passed'] else 'FAIL'}")
    lines.append(f"\n{result['questions']} gold items; overall: {'PASS' if result['passed'] else 'FAIL'}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m evals", description="Run the offline kgrag evals.")
    p.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    p.add_argument("--out", type=Path, default=DEFAULT_RESULTS, help="JSON results path")
    args = p.parse_args(argv)
    result = run_all(args.corpus)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(format_table(result))
    print(f"results: {args.out}", file=sys.stderr)
    return 0 if result["passed"] else 1
