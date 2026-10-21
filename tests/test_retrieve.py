from kgrag.models import Chunk, Entity
from kgrag.retrieve import BM25Index, HybridRetriever, tokenize

CHUNKS = [
    Chunk("c1", "d1", "Neo4j is a graph database used for storing property graphs.", 0, 10),
    Chunk("c2", "d1", "Bananas are yellow fruit grown in tropical climates.", 10, 20),
    Chunk("c3", "d2", "Cypher lets analysts traverse relationships efficiently.", 0, 10),
    Chunk("c4", "d2", "Vector embeddings capture semantic similarity.", 10, 20),
]
PATHS = {"d1": "research/a.md", "d2": "research/b.md"}


class FakeGraph:
    ents = {"neo4j": Entity("e1", "Neo4j", "tool", mentions=("c1",)),
            "cypher": Entity("e2", "Cypher", "language", mentions=("c3",))}

    def find_entity(self, name):
        e = self.ents.get(name.lower())
        return [e] if e else []

    def neighbors(self, entity_id):
        return [self.ents["cypher"]] if entity_id == "e1" else []

    def chunks_for_entity(self, entity_id):
        return [c for e in self.ents.values() if e.id == entity_id for c in e.mentions]


def make(graph=None):
    idx = BM25Index.build(CHUNKS, doc_paths=PATHS)
    return idx, HybridRetriever(idx, graph or FakeGraph())


def test_tokenize_drops_stopwords():
    assert tokenize("The Graph of the DB") == ["graph", "db"]


def test_bm25_ranks_relevant_first():
    idx, _ = make()
    assert idx.search("graph database", 3)[0][0] == "c1"


def test_bm25_save_load(tmp_path):
    idx, _ = make()
    idx.save(tmp_path / "i.json")
    again = BM25Index.load(tmp_path / "i.json")
    assert again.search("graph database") == idx.search("graph database")
    assert again.doc_paths == PATHS


def test_graph_expansion_surfaces_unrelated_chunk():
    _, r = make()
    res = {x.chunk.id: x for x in r.retrieve("neo4j")}
    assert "c3" in res and res["c3"].via == ("graph",)
    assert res["c1"].via == ("lexical", "graph")
    assert res["c3"].source_path == "research/b.md"


def test_dedup_and_ordering():
    _, r = make()
    res = r.retrieve("neo4j graph database", k=10)
    ids = [x.chunk.id for x in res]
    assert len(ids) == len(set(ids))
    assert ids[0] == "c1"


def test_empty_and_stopword_queries():
    _, r = make()
    assert r.retrieve("") == []
    assert r.retrieve("the of and") == []
    assert r.retrieve("zzzunknown") == []
