"""Command line entry point: ingest, ask, stats, entity."""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .agent import Agent
from .config import DEFAULT_CORPUS_DIR, DEFAULT_STORE_DIR, Config
from .extract import HeuristicExtractor, LLMExtractor
from .graph import GRAPH_FILE, KnowledgeGraph
from .ingest import SUPPORTED_SUFFIXES, chunk_document, load_corpus
from .llm import OfflineLLM, get_llm
from .retrieve import BM25Index, HybridRetriever

INDEX_FILE = "bm25.json"
TOP_ENTITIES = 10


class CLIError(Exception):
    """A user-facing failure; main() prints the message and returns exit code 1."""


def _count_skipped(root: Path) -> int:
    return sum(1 for p in root.rglob("*")
               if p.is_file() and p.suffix.lower() not in SUPPORTED_SUFFIXES
               and not any(part.startswith(".") for part in p.relative_to(root).parts))


def _load_store(store: Path) -> tuple[KnowledgeGraph, BM25Index]:
    if not (store / GRAPH_FILE).is_file() or not (store / INDEX_FILE).is_file():
        raise CLIError(f"No knowledge graph store found at '{store}'. Run `kgrag ingest` first.")
    try:
        return KnowledgeGraph.load(store), BM25Index.load(store / INDEX_FILE)
    except (ValueError, KeyError, OSError) as e:
        raise CLIError(f"Store at '{store}' is unreadable ({e}). Re-run `kgrag ingest`.") from None


def cmd_ingest(args: argparse.Namespace) -> int:
    cfg = Config(corpus_dir=args.path, store_dir=args.store)
    try:
        docs = load_corpus(cfg.corpus_dir)
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        raise CLIError(str(e)) from None
    if args.extractor == "llm":
        llm = get_llm()
        if isinstance(llm, OfflineLLM):
            print("note: ANTHROPIC_API_KEY not set; using the heuristic extractor.", file=sys.stderr)
            extractor = HeuristicExtractor()
        else:
            extractor = LLMExtractor(llm)
    else:
        extractor = HeuristicExtractor()

    # Always rebuild from scratch so re-running is idempotent.
    graph = KnowledgeGraph()
    chunks = []
    for doc in docs:
        graph.add_document(doc)
        for ch in chunk_document(doc, cfg.chunk_size, cfg.chunk_overlap):
            graph.add_chunk(ch)
            chunks.append(ch)
    graph.add_extraction(*extractor.extract(chunks))
    graph.save(cfg.store_dir)
    BM25Index.build(chunks, doc_paths={d.id: d.path for d in docs}).save(cfg.store_dir / INDEX_FILE)

    s = graph.stats()
    print(f"documents: {s['documents']}")
    print(f"chunks: {s['chunks']}")
    print(f"entities: {s['entities']}")
    print(f"relations: {s['relations']}")
    print(f"skipped files: {_count_skipped(cfg.corpus_dir)}")
    print(f"store: {cfg.store_dir}")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    graph, index = _load_store(Path(args.store))
    agent = Agent(graph, HybridRetriever(index, graph), get_llm())
    result = agent.run(args.question)
    if args.json:
        print(json.dumps(dataclasses.asdict(result), indent=2, ensure_ascii=False))
        return 0
    if args.trace:
        print("Trace:")
        for i, step in enumerate(result.trace, 1):
            print(f"  {i}. {json.dumps(step, ensure_ascii=False, default=str)}")
        print()
    print(result.answer)
    if result.citations:
        print("\nCitations:")
        for i, c in enumerate(result.citations, 1):
            print(f"[{i}] {c.get('doc_path', '?')}: \"{c.get('quote', '')}\"")
    if result.truncated:
        print("\n(note: step limit reached before the agent finished)", file=sys.stderr)
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    graph, _ = _load_store(Path(args.store))
    s = graph.stats(TOP_ENTITIES)
    top = s.pop("top_entities")
    for k, v in s.items():
        print(f"{k}: {v}")
    print("\nTop entities by degree:")
    for e in top:
        print(f"  {e['degree']:>3}  {e['name']}")
    return 0


def cmd_entity(args: argparse.Namespace) -> int:
    graph, _ = _load_store(Path(args.store))
    ent = graph.find_entity(args.name)
    if ent is None:
        raise CLIError(f"Entity not found: {args.name}")
    print(f"{ent.name} ({ent.type})")
    if ent.aliases:
        print(f"aliases: {', '.join(ent.aliases)}")
    print(f"mentions: {len(ent.mentions)} chunks")
    rels = [r for r in graph.relations if ent.id in (r.source_id, r.target_id)]
    print("relations:" if rels else "relations: none")
    for r in rels:
        src, dst = graph.entities[r.source_id], graph.entities[r.target_id]
        print(f"  {src.name} --{r.type}--> {dst.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kgrag", description="Knowledge graph and agentic RAG over a research corpus.")
    p.add_argument("-V", "--version", action="version", version=f"kgrag {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    def add_store(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--store", default=str(DEFAULT_STORE_DIR), help="store directory (default: .kgrag)")

    sp = sub.add_parser("ingest", help="load, chunk, extract and index a corpus folder")
    sp.add_argument("path", nargs="?", default=str(DEFAULT_CORPUS_DIR), help="corpus folder (default: research/)")
    add_store(sp)
    sp.add_argument("--extractor", choices=("heuristic", "llm"), default="heuristic")
    sp.set_defaults(func=cmd_ingest)

    sp = sub.add_parser("ask", help="answer a question with citations")
    sp.add_argument("question")
    add_store(sp)
    sp.add_argument("--trace", action="store_true", help="print the agent's tool steps")
    sp.add_argument("--json", action="store_true", help="emit the AgentResult as JSON")
    sp.set_defaults(func=cmd_ask)

    sp = sub.add_parser("stats", help="graph statistics and top entities by degree")
    add_store(sp)
    sp.set_defaults(func=cmd_stats)

    sp = sub.add_parser("entity", help="show an entity and its relations")
    sp.add_argument("name")
    add_store(sp)
    sp.set_defaults(func=cmd_entity)
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except CLIError as e:
        print(f"kgrag: error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
