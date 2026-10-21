# research
Research Docs, plus `kgrag`, a knowledge graph and agentic RAG system over `research/`.

## Setup
```
pip install -e .[dev]
pytest
```

## Dependencies
- Runtime: Python 3.10+ standard library only. No runtime dependencies are declared.
- Dev: `pytest` (optional extra `dev`).
- Graph storage: no graph database is required (no Neo4j, no Cypher). The graph is an in-memory `KnowledgeGraph` persisted as JSON in `<store>/graph.json`.
- Network: none by default. `AnthropicLLM` calls api.anthropic.com **only** when `ANTHROPIC_API_KEY` is set (model `claude-sonnet-5-5`, override with `KGRAG_MODEL`). Otherwise the deterministic `OfflineLLM` is used. Flag for approval before enabling in a regulated environment.

## Layout
- `kgrag/` package (models, config, llm; more modules arrive in later tasks)
- `research/` sample corpus (see `research/README.md`)
- `tests/fixtures/` tiny test corpus

## Quickstart
```
pip install -e .[dev]
kgrag ingest research/            # or: python -m kgrag ingest research/
kgrag ask "Which university created the algorithm GraphRAG uses?"
kgrag ask "..." --trace           # show tool steps
kgrag ask "..." --json            # AgentResult as JSON
kgrag stats                       # graph counts and top entities by degree
kgrag entity "GraphRAG"           # entity, aliases and relations
```
All commands accept `--store DIR` (default `.kgrag`). `ingest` takes `[PATH]` (default `research/`) and `--extractor heuristic|llm`, and prints documents, chunks, entities, relations and skipped (unsupported) files. Ingest rebuilds the store from scratch, so re-running it gives identical counts and no duplicate entities. Exit code is 0 on success; nonzero with a message if the store is missing (`run kgrag ingest first`) or the corpus folder is missing or empty.

## Architecture
1. **Ingest** (`ingest.py`): recursively loads `.md`/`.markdown`/`.txt`, splits into paragraph-packed chunks with exact character offsets.
2. **Graph** (`extract.py`, `graph.py`): an extractor (deterministic heuristic, or LLM with per-chunk heuristic fallback) yields entities and relations with chunk-level evidence; `KnowledgeGraph` merges by name/alias and persists to `<store>/graph.json`.
3. **Hybrid retrieval** (`retrieve.py`): BM25 over chunks (`<store>/bm25.json`) fused with graph expansion from entities linked in the query (up to 2 hops).
4. **Agent loop** (`agent.py`): tools `search`, `lookup_entity`, `expand`, `finish`; answers are grounded in retrieved chunks and carry citations (file path, chunk id, verbatim quote).

## Offline vs Anthropic mode
- **Offline (default):** no network, no key. A deterministic policy drives the tools and returns an extractive, cited answer.
- **Anthropic:** set `ANTHROPIC_API_KEY` in your environment (never commit it) to let the model drive the agent loop; `--extractor llm` then also uses it for entity extraction. Override the model with `KGRAG_MODEL`. Without a key, `--extractor llm` falls back to the heuristic extractor with a note.

## Adding docs to `research/`
Drop `.md`, `.markdown` or `.txt` files anywhere under `research/` (hidden paths are ignored; other file types are counted as skipped), then re-run `kgrag ingest research/`.
