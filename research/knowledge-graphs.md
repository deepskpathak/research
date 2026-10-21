# Knowledge Graphs

A knowledge graph stores facts as entities (nodes) and typed relations (edges). Neo4j is a popular property graph database, and RDF triple stores are another common choice. Entities in a knowledge graph are often extracted from text by an LLM.

Knowledge graphs make multi-hop questions tractable: following edges from one entity to the next answers questions that no single passage can. GraphRAG builds on this idea by combining a knowledge graph with retrieval augmented generation.
