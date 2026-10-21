import json
from pathlib import Path

import pytest

from kgrag.cli import main


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def test_ingest_then_ask(mini_corpus, tmp_path, capsys):
    store = str(tmp_path / "s")
    assert main(["ingest", str(mini_corpus), "--store", store]) == 0
    out = capsys.readouterr().out
    for key in ("documents:", "chunks:", "entities:", "relations:", "skipped files:"):
        assert key in out
    assert main(["ask", "Who designed the Analytical Engine?", "--store", store]) == 0
    assert "[1]" in capsys.readouterr().out


def test_ask_json_and_trace(mini_corpus, tmp_path, capsys):
    store = str(tmp_path / "s")
    main(["ingest", str(mini_corpus), "--store", store])
    capsys.readouterr()
    assert main(["ask", "Who designed the Analytical Engine?", "--store", store, "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert {"answer", "citations", "trace"} <= data.keys()
    assert main(["ask", "Who designed the Analytical Engine?", "--store", store, "--trace"]) == 0
    assert "Trace:" in capsys.readouterr().out


def test_ask_before_ingest(tmp_path, capsys):
    assert main(["ask", "hi", "--store", str(tmp_path / "none")]) != 0
    assert "kgrag ingest" in capsys.readouterr().err


def test_missing_and_empty_corpus(tmp_path, capsys):
    assert main(["ingest", str(tmp_path / "nope"), "--store", str(tmp_path / "s")]) != 0
    assert "not found" in capsys.readouterr().err
    empty = tmp_path / "empty"
    empty.mkdir()
    assert main(["ingest", str(empty), "--store", str(tmp_path / "s")]) != 0
    assert "No supported documents" in capsys.readouterr().err


def test_ingest_idempotent(mini_corpus, tmp_path, capsys):
    store = str(tmp_path / "s")
    main(["ingest", str(mini_corpus), "--store", store])
    first = capsys.readouterr().out
    graph1 = (Path(store) / "graph.json").read_text()
    main(["ingest", str(mini_corpus), "--store", store])
    assert capsys.readouterr().out == first
    assert (Path(store) / "graph.json").read_text() == graph1


def test_stats_and_entity(mini_corpus, tmp_path, capsys):
    store = str(tmp_path / "s")
    main(["ingest", str(mini_corpus), "--store", store])
    capsys.readouterr()
    assert main(["stats", "--store", store]) == 0
    assert "Top entities" in capsys.readouterr().out
    assert main(["entity", "zzz-no-such-entity", "--store", store]) != 0


def test_research_corpus_offline(tmp_path, capsys):
    research = Path(__file__).parent.parent / "research"
    store = str(tmp_path / "s")
    assert main(["ingest", str(research), "--store", store]) == 0
    capsys.readouterr()
    assert main(["ask", "Which university created the Leiden algorithm?", "--store", store]) == 0
    out = capsys.readouterr().out
    assert "Leiden" in out and "[1]" in out
