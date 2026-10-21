import logging

from kgrag.extract import HeuristicExtractor, LLMExtractor
from kgrag.graph import KnowledgeGraph, entity_id
from kgrag.models import Chunk, Document, Entity, Relation


def _chunks():
    return [
        Chunk("d1:0", "d1", "# Knowledge Graph\n\nA Knowledge Graph stores Entity Nodes. "
              "Retrieval-Augmented Generation (RAG) uses Knowledge Graph data.", 0, 100),
        Chunk("d2:0", "d2", "knowledge graph basics. Vector Search is part of RAG pipelines. "
              "Leiden Algorithm is a Community Detection method.", 0, 100),
        Chunk("d2:1", "d2", "The Knowledge Graph helps RAG.", 100, 130),
    ]


def build(extractor=None):
    chunks = _chunks()
    g = KnowledgeGraph()
    for d in ("d1", "d2"):
        g.add_document(Document(d, f"{d}.md", d, ""))
    for c in chunks:
        g.add_chunk(c)
    g.add_extraction(*(extractor or HeuristicExtractor()).extract(chunks))
    return g


def test_entity_merges_across_docs():
    g = build()
    e = g.find_entity("Knowledge Graph")
    docs = {g.chunks[c].doc_id for c in e.mentions}
    assert docs == {"d1", "d2"}
    assert sum(1 for x in g.entities.values() if x.name.lower() == "knowledge graph") == 1


def test_acronym_alias_and_relations():
    g = build()
    rag = g.find_entity("rag")
    assert rag.name == "Retrieval-Augmented Generation" and "RAG" in rag.aliases
    types = {(g.entities[r.source_id].name, r.type, g.entities[r.target_id].name) for r in g.relations}
    assert ("Retrieval-Augmented Generation", "uses", "Knowledge Graph") in types
    assert ("Leiden Algorithm", "is_a", "Community Detection") in types
    assert ("Vector Search", "part_of", "Retrieval-Augmented Generation") in types
    assert any(r.type == "related_to" for r in g.relations)


def test_evidence_exists():
    g = build()
    assert g.relations
    assert g.dangling_evidence() == []
    assert all(r.evidence_chunk_ids for r in g.relations)


def test_save_load_roundtrip(tmp_path):
    import json
    g = build()
    path = g.save(tmp_path)
    assert json.loads(path.read_text())["schema_version"] == 1
    assert KnowledgeGraph.load(tmp_path) == g


def test_find_and_neighbors():
    g = build()
    assert g.find_entity("KNOWLEDGE GRAPH") is g.find_entity("knowledge graph")
    assert g.find_entity("Leiden Alg").name == "Leiden Algorithm"
    assert g.find_entity("zzz") is None
    kg = g.find_entity("Knowledge Graph")
    n1 = {e.name for e in g.neighbors(kg.id)}
    n2 = {e.name for e in g.neighbors(kg.id, depth=2)}
    assert n1 == {"Entity Nodes", "Retrieval-Augmented Generation"}
    assert n2 - n1 == {"Community Detection", "Leiden Algorithm", "Vector Search"}
    assert "Knowledge Graph" not in n2
    assert g.chunks_for_entity(kg.id)
    assert g.stats()["entities"] == len(g.entities)


def test_neighbors_depth2_reaches_further():
    g = build()
    leiden = g.find_entity("Leiden Algorithm")
    d1 = {e.name for e in g.neighbors(leiden.id, 1)}
    d2 = {e.name for e in g.neighbors(leiden.id, 2)}
    assert d1 == {"Community Detection", "Vector Search", "Retrieval-Augmented Generation"}
    assert d2 - d1 == {"Entity Nodes", "Knowledge Graph"}


def test_top_entities_by_degree_exact_order():
    g = KnowledgeGraph()
    for name in ("Hub", "Alpha", "Beta", "Gamma", "Lonely"):
        g.add_entity(Entity(entity_id(name), name, "concept"))
    for a, b in (("Hub", "Alpha"), ("Hub", "Beta"), ("Hub", "Gamma"), ("Gamma", "Beta")):
        g.add_relation(Relation(entity_id(a), entity_id(b), "related_to"))
    # Hub=3, Beta=2, Gamma=2 (name tie-break), Alpha=1, Lonely=0
    expected = [("Hub", 3), ("Beta", 2), ("Gamma", 2), ("Alpha", 1), ("Lonely", 0)]
    assert g.top_entities_by_degree() == expected
    assert g.top_entities_by_degree(2) == expected[:2]
    top = g.stats()["top_entities"]
    assert [(t["name"], t["degree"]) for t in top] == expected
    assert top[0]["id"] == "ent-hub"
    assert len(g.stats(top_n=3)["top_entities"]) == 3


class StubLLM:
    def __init__(self, reply):
        self.reply = reply

    def complete(self, system, messages):
        return self.reply


def test_llm_fallback_on_malformed_json(caplog):
    with caplog.at_level(logging.WARNING):
        g = build(LLMExtractor(StubLLM("not json {")))
    assert "heuristic fallback" in caplog.text
    assert g.find_entity("Knowledge Graph")


def test_llm_valid_json():
    reply = ('{"entities":[{"name":"Foo","type":"tool","aliases":["F"]},{"name":"Bar","type":"tool"}],'
             '"relations":[{"source":"Foo","target":"Bar","type":"uses"}]}')
    ents, rels = LLMExtractor(StubLLM(reply)).extract([Chunk("c1", "d", "x", 0, 1)])
    assert {e.name for e in ents} == {"Foo", "Bar"}
    assert rels[0].type == "uses" and rels[0].evidence_chunk_ids == ("c1",)
