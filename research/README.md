# Research corpus

Five short documents on one topic: knowledge graphs, RAG, and agents.

| File | Main entities |
|---|---|
| knowledge-graphs.md | Knowledge Graph, Neo4j, GraphRAG |
| rag.md | RAG, Patrick Lewis, GraphRAG, BM25 |
| graphrag.md | GraphRAG, Microsoft Research, Leiden algorithm |
| leiden-algorithm.md | Leiden algorithm, Leiden University, Louvain |
| agentic-rag.md | Agentic RAG, ReAct, GraphRAG |

## Multi-document facts

- **Q: Which university created the community detection algorithm used by GraphRAG?**
  A: Leiden University. `graphrag.md` says GraphRAG uses the Leiden algorithm; `leiden-algorithm.md` says that algorithm was created at Leiden University. Neither document alone answers it.
- **Q: Which organization published the approach that adds community summaries to RAG, and what did RAG's original authors work for?**
  `graphrag.md` (Microsoft Research) plus `rag.md` (Facebook AI Research).
