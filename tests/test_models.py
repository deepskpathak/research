import dataclasses

import pytest

from kgrag.models import Chunk, Document, Entity, Relation

SAMPLES = [
    Document("d1", "research/a.md", "A", "text"),
    Chunk("c1", "d1", "text", 0, 4),
    Entity("e1", "GraphRAG", "technique", ("Graph RAG",), ("c1", "c2")),
    Relation("e1", "e2", "uses", ("c1",)),
]


@pytest.mark.parametrize("obj", SAMPLES, ids=lambda o: type(o).__name__)
def test_round_trip(obj):
    assert type(obj).from_dict(obj.to_dict()) == obj


def test_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        SAMPLES[0].title = "x"


def test_list_inputs_normalised():
    e = Entity("e", "n", "t", ["a"], ["c"])
    assert e.aliases == ("a",) and hash(e) is not None
    assert Entity.from_dict({"id": "e", "name": "n", "type": "t"}).mentions == ()
