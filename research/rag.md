# Retrieval Augmented Generation

Retrieval Augmented Generation (RAG) was introduced by Patrick Lewis and colleagues at Facebook AI Research in 2020. A RAG system retrieves passages relevant to a question and gives them to an LLM so the answer is grounded in sources.

Baseline RAG uses vector search over chunks. It struggles with global questions about a whole corpus and with multi-hop questions. GraphRAG addresses both by adding a knowledge graph. Hybrid retrieval combines lexical search such as BM25 with graph expansion.
