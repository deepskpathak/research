# Agentic RAG

Agentic RAG puts an LLM agent in a loop. The agent decides which tool to call, such as lexical search or a knowledge graph lookup, reads the results, and decides whether to search again before answering. This lets it handle multi-hop questions that a single retrieval step misses.

ReAct, by Shunyu Yao and colleagues, is the pattern of interleaving reasoning and actions. Agentic RAG systems cite the chunks they used so answers stay grounded. Agents can query a knowledge graph or GraphRAG community summaries as tools.
