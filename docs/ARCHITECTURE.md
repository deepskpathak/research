# Architecture

`kgrag` is a stdlib-only knowledge graph plus agentic RAG over a local folder of Markdown/text files. There is no graph database and no server: everything lives in memory while running and persists as two JSON files under the store directory (`.kgrag/` by default).

See also: [HLD](HLD.md) (data flow and design decisions), [LLD](LLD.md) (classes, agent loop, ids, store layout), [USAGE](USAGE.md).

## System context

```mermaid
flowchart LR
    user([Developer / CLI user])
    corpus[(research/ corpus<br/>.md .markdown .txt)]
    store[(.kgrag/ store<br/>graph.json, bm25.json)]
    api[[Anthropic Messages API<br/>optional]]
    kgrag[kgrag]

    user -- "kgrag ingest / ask / stats / entity" --> kgrag
    corpus -- read as bytes --> kgrag
    kgrag <-- JSON read/write --> store
    kgrag -. "only if ANTHROPIC_API_KEY is set" .-> api
```

The network box is optional. Without a key the deterministic `OfflineLLM` is used and nothing leaves the machine.

## Components

```mermaid
flowchart TD
    CLI["cli.py<br/>main, cmd_ingest, cmd_ask,<br/>cmd_stats, cmd_entity"]
    ING["ingest.py<br/>load_corpus, chunk_document"]
    EXT["extract.py<br/>HeuristicExtractor, LLMExtractor"]
    KG["graph.py<br/>KnowledgeGraph"]
    BM["retrieve.py<br/>BM25Index"]
    HR["retrieve.py<br/>HybridRetriever"]
    AG["agent.py<br/>Agent"]
    LLM["llm.py<br/>get_llm, OfflineLLM, AnthropicLLM"]
    STORE[(".kgrag/<br/>graph.json<br/>bm25.json")]
    CFG["config.py<br/>Config"]
    MOD["models.py<br/>Document, Chunk, Entity, Relation"]

    CLI --> CFG
    CLI --> ING
    CLI --> EXT
    CLI --> KG
    CLI --> BM
    CLI --> AG
    CLI --> LLM
    ING --> MOD
    EXT --> MOD
    EXT -. "LLMExtractor only" .-> LLM
    KG --> MOD
    KG -- save/load --> STORE
    BM -- save/load --> STORE
    HR --> BM
    HR --> KG
    AG --> HR
    AG --> KG
    AG --> LLM
```

| Component | Responsibility |
|---|---|
| CLI (`kgrag/cli.py`) | argparse front end; errors go to stderr with exit code 1, no stack trace. |
| Ingest (`kgrag/ingest.py`) | Recursive load of supported files, paragraph-packed chunks with exact character offsets. |
| Extract (`kgrag/extract.py`) | Entities and relations with chunk-level evidence. Heuristic by default; LLM extractor falls back to heuristic per chunk. |
| KnowledgeGraph (`kgrag/graph.py`) | In-memory graph: merge by normalized name/alias, neighbors, degree stats, JSON persistence. |
| BM25Index (`kgrag/retrieve.py`) | Lexical index over chunks, persisted to `bm25.json` together with the doc id to path map. |
| HybridRetriever (`kgrag/retrieve.py`) | Fuses BM25 ranking with graph-expansion ranking via reciprocal rank fusion. |
| Agent (`kgrag/agent.py`) | Tool loop (`search`, `lookup_entity`, `expand`, `finish`), citation verification, relevance gate, offline policy. |
| LLM client (`kgrag/llm.py`) | `get_llm` returns `AnthropicLLM` when `ANTHROPIC_API_KEY` is non-empty, else `OfflineLLM`. |
| Store (`.kgrag/`) | Rebuilt from scratch on every `ingest`; gitignored. |
