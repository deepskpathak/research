import json

import pytest

from kgrag.agent import NOT_FOUND, Agent
from kgrag.extract import HeuristicExtractor
from kgrag.graph import KnowledgeGraph
from kgrag.ingest import chunk_document, load_corpus
from kgrag.llm import OfflineLLM
from kgrag.retrieve import BM25Index, HybridRetriever


@pytest.fixture
def stack(mini_corpus):
    docs = load_corpus(mini_corpus)
    chunks = [c for d in docs for c in chunk_document(d)]
    g = KnowledgeGraph()
    for d in docs:
        g.add_document(d)
    for c in chunks:
        g.add_chunk(c)
    g.add_extraction(*HeuristicExtractor().extract(chunks))
    idx = BM25Index.build(chunks, doc_paths={d.id: d.path for d in docs})
    return g, HybridRetriever(idx, g)


class Stub:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), 0

    def complete(self, system, messages):
        self.calls += 1
        return self.replies.pop(0) if self.replies else self.replies_default

    replies_default = json.dumps({"tool": "search", "args": {"query": "babbage"}})


def agent(stack, llm=None, **kw):
    g, r = stack
    return Agent(g, r, llm or OfflineLLM(), **kw)


def steps(res):
    return [t for t in res.trace if t["tool"] != "fallback"]


def test_answerable_quotes_are_verbatim(stack):
    g, _ = stack
    res = agent(stack).run("Where was Charles Babbage born?")
    assert "London" in res.answer and res.citations
    for c in res.citations:
        assert c["quote"] in g.chunks[c["chunk_id"]].text
        assert c["doc_path"].endswith("beta.txt")


def test_two_hop_cites_both_docs(stack):
    res = agent(stack).run("What did Ada Lovelace write about, and where was Charles Babbage born?")
    paths = {c["doc_path"].rsplit("/", 1)[-1] for c in res.citations}
    assert paths == {"alpha.md", "beta.txt"}


def test_off_topic_not_found(stack):
    res = agent(stack).run("What is the capital of France?")
    assert res.answer == NOT_FOUND and res.citations == []


def test_malformed_json_falls_back(stack):
    llm = Stub(["not json", "{still bad"])
    res = agent(stack, llm).run("Where was Charles Babbage born?")
    assert llm.calls == 2  # one retry, then fallback
    assert any(t["tool"] == "fallback" for t in res.trace)
    assert "London" in res.answer and res.citations


def test_llm_happy_path_and_citation_validation(stack):
    g, r = stack
    cid = next(c.id for c in g.chunks.values() if "born in London" in c.text)
    good = json.dumps({"tool": "finish", "args": {"answer": "London.", "citations": [
        {"chunk_id": cid, "quote": "Charles Babbage was born in London."}]}})
    llm = Stub([json.dumps({"tool": "search", "args": {"query": "babbage born"}}), good])
    res = Agent(g, r, llm).run("Where was Babbage born?")
    assert res.answer == "London." and res.citations[0]["chunk_id"] == cid
    # fabricated quote -> rejected -> offline fallback with real citations
    bad = json.dumps({"tool": "finish", "args": {"answer": "Paris.", "citations": [
        {"chunk_id": cid, "quote": "invented"}]}})
    res = Agent(g, r, Stub([bad])).run("Where was Charles Babbage born?")
    assert "Paris" not in res.answer
    assert any(t["tool"] == "fallback" for t in res.trace)
    assert all(c["quote"] in g.chunks[c["chunk_id"]].text for c in res.citations)


def test_max_steps_enforced(stack):
    llm = Stub([])  # always searches, never finishes
    res = agent(stack, llm, max_steps=3).run("Where was Charles Babbage born?")
    assert len(steps(res)) == 3 and llm.calls == 3 and res.truncated
    res = agent(stack, max_steps=2).run("What did Ada Lovelace write about, and where was Charles Babbage born?")
    assert len(steps(res)) == 2  # budget is used, never exceeded
