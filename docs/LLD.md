# Low-level design

Companion docs: [ARCHITECTURE](ARCHITECTURE.md), [HLD](HLD.md), [USAGE](USAGE.md).

## Models and main classes

```mermaid
classDiagram
    class Document {
        +str id
        +str path
        +str title
        +str text
        +to_dict()
        +from_dict(d)
    }
    class Chunk {
        +str id
        +str doc_id
        +str text
        +int start
        +int end
        +to_dict()
        +from_dict(d)
    }
    class Entity {
        +str id
        +str name
        +str type
        +tuple aliases
        +tuple mentions
        +to_dict()
        +from_dict(d)
    }
    class Relation {
        +str source_id
        +str target_id
        +str type
        +tuple evidence_chunk_ids
        +to_dict()
        +from_dict(d)
    }
    class KnowledgeGraph {
        +dict entities
        +list relations
        +dict chunks
        +dict documents
        +add_document(doc)
        +add_chunk(chunk)
        +add_entity(e)
        +add_relation(r)
        +add_extraction(entities, relations)
        +merge(other)
        +resolve(name_or_id)
        +find_entity(name)
        +neighbors(entity_id, depth)
        +chunks_for_entity(entity_id)
        +degrees()
        +top_entities_by_degree(n)
        +stats(top_n)
        +dangling_evidence()
        +save(directory)
        +load(directory)
    }
    class BM25Index {
        +dict chunks
        +dict doc_paths
        +build(chunks, doc_paths)
        +search(query, k)
        +save(path)
        +load(path)
    }
    class RetrievedChunk {
        +Chunk chunk
        +float score
        +str source_path
        +tuple via
    }
    class HybridRetriever {
        +BM25Index index
        +KnowledgeGraph graph
        +dict last_stats
        +retrieve(query, k, lexical_k)
    }
    class Extractor {
        <<protocol>>
        +extract(chunks)
    }
    class HeuristicExtractor {
        +extract(chunks)
    }
    class LLMExtractor {
        +extract(chunks)
    }
    class LLMClient {
        <<protocol>>
        +complete(system, messages)
    }
    class OfflineLLM {
        +complete(system, messages)
    }
    class AnthropicLLM {
        +complete(system, messages)
    }
    class Agent {
        +run(question)
        +search(st, query)
        +lookup_entity(st, name)
        +expand(st, entity, depth)
    }
    class AgentResult {
        +str answer
        +list citations
        +list trace
        +bool truncated
    }

    Chunk --> Document : doc_id
    Relation --> Entity : source_id, target_id
    KnowledgeGraph o-- Document
    KnowledgeGraph o-- Chunk
    KnowledgeGraph o-- Entity
    KnowledgeGraph o-- Relation
    BM25Index o-- Chunk
    HybridRetriever --> BM25Index
    HybridRetriever --> KnowledgeGraph
    HybridRetriever ..> RetrievedChunk
    Extractor <|.. HeuristicExtractor
    Extractor <|.. LLMExtractor
    LLMExtractor --> LLMClient
    LLMExtractor --> HeuristicExtractor : fallback
    LLMClient <|.. OfflineLLM
    LLMClient <|.. AnthropicLLM
    Agent --> HybridRetriever
    Agent --> KnowledgeGraph
    Agent --> LLMClient
    Agent ..> AgentResult
```

All four models are frozen dataclasses with tuple list-fields, so they are hashable and round-trip through `to_dict`/`from_dict`.

## Agent loop

With a real LLM (`AnthropicLLM`), the model picks tools. With `OfflineLLM`, `Agent.run` goes straight to the deterministic policy `_offline`. `_next_action` allows one retry on malformed output; after that, or on an `LLMError`, the agent records a `fallback` step in the trace and runs `_offline`.

```mermaid
sequenceDiagram
    participant U as cmd_ask
    participant A as Agent
    participant L as LLM client
    participant R as HybridRetriever
    participant G as KnowledgeGraph

    U->>A: run(question)
    alt llm is OfflineLLM
        A->>A: _offline(state)
    else API mode: _llm_loop
        loop until finish or max_steps
            A->>L: complete(system, messages)
            L-->>A: JSON {"tool", "args"}
            alt malformed (after one retry) or LLMError
                A->>A: trace "fallback", then _offline(state)
            else tool = search
                A->>R: retrieve(query, k)
                R-->>A: RetrievedChunk list
            else tool = lookup_entity
                A->>G: find_entity(name), chunks_for_entity(id)
            else tool = expand
                A->>G: find_entity(entity), neighbors(id, depth 1..2)
            else tool = finish
                A->>A: _finish_from_llm: keep only verbatim quotes
                Note over A: no verifiable citation means trace "fallback" and _offline
            end
        end
        Note over A: max_steps exhausted: _compose, truncated = True
    end
    Note over A: _offline plan = search(question), then with 2+ entity mentions: search per name, lookup_entity per name, expand(depth 1) per name. Last step reserved for finish.
    A->>A: _compose: score evidence sentences, relevance gate, pick up to 3
    A-->>U: AgentResult(answer, citations, trace, truncated)
```

`_compose` returns `NOT_FOUND` with empty citations when no sentence passes the relevance gate. Offline answers cite each picked sentence as `[n]` with `{doc_path, chunk_id, quote}`.

## Id hashing scheme

Defined in `kgrag/ingest.py` (`_stable_id`) and `kgrag/graph.py` (`entity_id`).

| Object | Id |
|---|---|
| Document | first 16 hex chars of SHA-1 over the POSIX path relative to the corpus root |
| Chunk | first 16 hex chars of SHA-1 over `doc.id`, `start`, `end` (parts joined with `\x1f`) |
| Entity | `ent-` plus the normalized name (`norm_key`: lowercase, whitespace/hyphen/underscore folded to one space, last token singularized) with spaces as `-` |

Files are read as bytes and decoded as UTF-8, so `Chunk.text == Document.text[start:end]` holds exactly. The same corpus therefore always yields the same ids and the same store.

## Store file layout

```
.kgrag/                  (default; set with --store; gitignored)
├── graph.json           KnowledgeGraph.to_dict()
│     schema_version     currently 1
│     documents[]        id, path, title, text
│     chunks[]           id, doc_id, text, start, end
│     entities[]         id, name, type, aliases[], mentions[] (chunk ids)
│     relations[]        source_id, target_id, type, evidence_chunk_ids[]
└── bm25.json            BM25Index.save()
      chunks, doc_paths (doc id -> relative path), k1, b
```

Entries are sorted by id when written, so output is stable between runs.
