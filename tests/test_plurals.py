from pathlib import Path

from kgrag.extract import HeuristicExtractor
from kgrag.graph import KnowledgeGraph, entity_id, norm_key
from kgrag.ingest import chunk_document, load_corpus
from kgrag.models import Chunk

RESEARCH = Path(__file__).parent.parent / "research"


def test_plural_rules():
    assert norm_key("Knowledge Graphs") == norm_key("knowledge graph") == "knowledge graph"
    assert norm_key("entities") == "entity"
    assert norm_key("Queries") == "query"
    assert norm_key("indexes") == "index"
    assert norm_key("LLMs") == "llm"


def test_untouched_words():
    for w in ("analysis", "corpus", "class", "RAG", "GAS", "gas", "Bias", "series"):
        assert norm_key(w) == w.lower()
    assert norm_key("Graph Analysis") == "graph analysis"


def test_entity_id_is_deterministic_and_merged():
    assert entity_id("Knowledge Graphs") == entity_id("Knowledge Graph") == "ent-knowledge-graph"


def test_extract_merges_singular_and_plural():
    chunks = [
        Chunk("c1", "d", "A Knowledge Graph stores facts.", 0, 31),
        Chunk("c2", "d", "so many Knowledge Graphs scale well.", 31, 64),
    ]
    ents, _ = HeuristicExtractor().extract(chunks)
    kg = [e for e in ents if norm_key(e.name) == "knowledge graph"]
    assert len(kg) == 1
    assert kg[0].name == "Knowledge Graph"
    assert set(kg[0].mentions) == {"c1", "c2"}
    # order of appearance must not change the canonical (singular) name
    ents2, _ = HeuristicExtractor().extract(chunks[::-1])
    assert [e.name for e in ents2 if norm_key(e.name) == "knowledge graph"] == ["Knowledge Graph"]


def test_find_entity_plural_and_singular():
    g = KnowledgeGraph()
    g.add_extraction(*HeuristicExtractor().extract(
        [Chunk("c1", "d", "A Knowledge Graph stores facts.", 0, 31)]))
    a, b = g.find_entity("Knowledge Graphs"), g.find_entity("knowledge graph")
    assert a is not None and a.id == b.id


def _build_research() -> KnowledgeGraph:
    g = KnowledgeGraph()
    chunks = []
    for d in load_corpus(RESEARCH):
        g.add_document(d)
        chunks.extend(chunk_document(d))
    for c in chunks:
        g.add_chunk(c)
    g.add_extraction(*HeuristicExtractor().extract(chunks))
    return g


def test_ingest_twice_identical_graph():
    a, b = _build_research(), _build_research()
    assert a == b
    assert a.to_dict() == b.to_dict()
    names = [norm_key(e.name) for e in a.entities.values()]
    assert len(names) == len(set(names))
