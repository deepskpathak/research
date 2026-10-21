# High-level design

Companion docs: [ARCHITECTURE](ARCHITECTURE.md), [LLD](LLD.md), [USAGE](USAGE.md).

## Ingest data flow

`kgrag ingest` always rebuilds the store from scratch, so repeated runs give identical output.

```mermaid
flowchart TD
    A[corpus folder] --> B["load_corpus<br/>recursive, sorted, skip hidden paths,<br/>skip root README.md, skip unsupported types"]
    B --> C["Document(id=sha1(relative path))"]
    C --> D["chunk_document<br/>paragraph packing, 800 chars, 100 overlap"]
    D --> E["Chunk(id=sha1(doc id, start, end))"]
    E --> F{"--extractor"}
    F -- heuristic --> G[HeuristicExtractor]
    F -- "llm and key set" --> H["LLMExtractor<br/>per-chunk heuristic fallback"]
    F -- "llm and no key" --> G
    G --> I["KnowledgeGraph.add_extraction<br/>merge by normalized name / alias"]
    H --> I
    I --> J[("graph.json")]
    E --> K["BM25Index.build<br/>chunks plus doc_paths"]
    K --> L[("bm25.json")]
    I --> M["stats printed:<br/>documents, chunks, entities,<br/>relations, skipped files"]
```

## Ask data flow

```mermaid
sequenceDiagram
    actor U as User
    participant C as CLI cmd_ask
    participant S as .kgrag store
    participant A as Agent
    participant R as HybridRetriever
    participant L as LLM client

    U->>C: kgrag ask "question"
    C->>S: load graph.json, bm25.json
    C->>A: Agent(graph, HybridRetriever, get_llm())
    A->>A: run(question)
    loop tool steps (max_steps)
        A->>L: complete(system, messages) [API mode only]
        L-->>A: JSON action
        A->>R: retrieve(query) for search
        R-->>A: RetrievedChunk list with source_path
    end
    A->>A: verify citation quotes against chunk text
    A->>A: relevance gate
    A-->>C: AgentResult(answer, citations, trace)
    C-->>U: answer plus Citations list (or not-found message)
```

## Retrieval

```mermaid
flowchart LR
    Q[query] --> T{"tokenize empty?"}
    T -- yes --> E[empty result]
    T -- no --> L["BM25Index.search<br/>top lexical_k=20"]
    Q --> LK["_link_entities<br/>n-grams 3,2,1 via find_entity"]
    LK --> GR["_graph_ranking<br/>chunks_for_entity + neighbors<br/>up to 2 hops"]
    GR --> F{"chunk in index?"}
    F -- no --> D["count in last_stats<br/>dropped_graph_chunks and log warning"]
    F -- yes --> RRF
    L --> RRF["Reciprocal rank fusion<br/>score = sum 1/(60 + rank)"]
    RRF --> TOP["top k RetrievedChunk<br/>via = lexical and/or graph"]
```

## Design decisions

| Decision | Rationale | Cost |
|---|---|---|
| **Stdlib only** (`dependencies = []`) | Regulated environment, no dependency approvals, easy to audit. | Hand-written BM25 and regex extraction; lower quality than embeddings or NER. |
| **Offline fallback** | `get_llm` returns `OfflineLLM` when the key is missing or blank. A deterministic policy (mentions, search, lookup, one-hop expand) drives the agent. Also used when LLM output is malformed after one retry; the fallback is recorded in the trace. Keeps tests and evals hermetic. | Offline answers are extractive sentences, not synthesized prose. |
| **RRF fusion** | Combines BM25 and graph rankings without tuning score scales. `RRF_K = 60`. | Ignores score magnitudes. |
| **Relevance gate** | The best evidence sentence must share at least two query terms, or half of them. Otherwise the answer is the not-found message with no citations. | Can refuse terse questions whose terms are rare in the corpus. |
| **Verbatim-citation check** | LLM citations are kept only if the quote (whitespace-squashed) is a substring of the cited chunk text. If none survive, the offline policy answers instead. | Paraphrased quotes are dropped. |
| **No graph database** | The corpus is small; an in-memory `KnowledgeGraph` persisted as JSON is enough and needs no service. | No query language and no scale beyond memory. |
| **Deterministic ids** | SHA-1 of relative path and offsets make ingest idempotent. | Moving a file changes its ids. |
| **Real source paths** | Retriever raises `MissingDocPathsError` if the index has no path map, and marks unknown docs `<unknown:DOC_ID>`, so a raw doc id never appears as a citation path. | Indexes must be built with `doc_paths`. |
