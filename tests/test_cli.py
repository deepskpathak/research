import json
from pathlib import Path

import pytest

from kgrag.cli import main
from kgrag.graph import KnowledgeGraph


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
    out = capsys.readouterr().out
    assert "Top entities by degree:" in out
    graph = KnowledgeGraph.load(store)
    expected = graph.top_entities_by_degree(10)
    assert expected and expected[0][1] > 0
    section = out.split("Top entities by degree:\n", 1)[1].strip().splitlines()
    assert [(ln.split(None, 1)[1], int(ln.split()[0])) for ln in section] == [(n, d) for n, d in expected]
    assert main(["entity", "zzz-no-such-entity", "--store", store]) != 0


def test_research_corpus_offline(tmp_path, capsys):
    research = Path(__file__).parent.parent / "research"
    store = str(tmp_path / "s")
    assert main(["ingest", str(research), "--store", store]) == 0
    capsys.readouterr()
    assert main(["ask", "Which university created the Leiden algorithm?", "--store", store]) == 0
    out = capsys.readouterr().out
    assert "Leiden" in out and "[1]" in out


# --- T5: skipped files, nested folders, not-found, multi-hop, error exits ---

RESEARCH = Path(__file__).parent.parent / "research"


def _ask_json(question, store, capsys):
    assert main(["ask", question, "--store", store, "--json"]) == 0
    return json.loads(capsys.readouterr().out)


def test_ingest_reports_exact_skipped_count(tmp_path, capsys):
    corpus = tmp_path / "c"
    (corpus / "sub").mkdir(parents=True)
    (corpus / "a.md").write_text("# Alpha\n\nAda Lovelace wrote notes.\n")
    (corpus / "sub" / "b.txt").write_text("Plain text about Charles Babbage.\n")
    for name in ("pic.png", "doc.pdf", "blob.bin", "sub/deep.PNG"):
        (corpus / name).write_bytes(b"\x00\x01")
    (corpus / ".hidden.png").write_bytes(b"\x00")  # hidden files are not counted
    assert main(["ingest", str(corpus), "--store", str(tmp_path / "s")]) == 0
    out = capsys.readouterr().out
    assert "skipped files: 4\n" in out
    assert "documents: 2\n" in out


def test_nested_folders_ingested_with_relative_path_citations(tmp_path, capsys):
    corpus = tmp_path / "c"
    (corpus / "a" / "b").mkdir(parents=True)
    (corpus / "a" / "b" / "c.md").write_text(
        "# Quasar Notes\n\nThe Zephyrian Telescope was designed by Marta Quillon in 1974.\n")
    (corpus / "top.md").write_text("# Top\n\nUnrelated gardening tips about tomatoes.\n")
    store = str(tmp_path / "s")
    assert main(["ingest", str(corpus), "--store", store]) == 0
    assert "documents: 2\n" in capsys.readouterr().out
    data = _ask_json("Who designed the Zephyrian Telescope?", store, capsys)
    paths = {c["doc_path"] for c in data["citations"]}
    assert "a/b/c.md" in paths
    assert not any(str(tmp_path) in p for p in paths)


def test_off_topic_question_is_not_found(tmp_path, capsys):
    store = str(tmp_path / "s")
    assert main(["ingest", str(RESEARCH), "--store", store]) == 0
    capsys.readouterr()
    assert main(["ask", "What is the boiling point of tungsten?", "--store", store]) == 0
    out = capsys.readouterr().out
    assert "Citations:" not in out
    assert out.strip()
    data = _ask_json("What is the boiling point of tungsten?", store, capsys)
    assert data["citations"] == []
    assert data["answer"].strip()


def test_multi_hop_citations_verbatim_from_both_files(tmp_path, capsys):
    store = str(tmp_path / "s")
    assert main(["ingest", str(RESEARCH), "--store", store]) == 0
    capsys.readouterr()
    data = _ask_json("Which university created the Leiden algorithm used by GraphRAG?", store, capsys)
    cites = data["citations"]
    paths = {c["doc_path"] for c in cites}
    assert {"graphrag.md", "leiden-algorithm.md"} <= paths, paths
    for c in cites:
        source = (RESEARCH / c["doc_path"]).read_text(encoding="utf-8")
        assert c["quote"] and c["quote"] in source, c


def test_ask_missing_store_errors_cleanly(tmp_path, capsys):
    assert main(["ask", "hi", "--store", str(tmp_path / "none")]) == 1
    cap = capsys.readouterr()
    assert cap.out == ""
    assert "kgrag: error:" in cap.err and "Traceback" not in cap.err


def test_ingest_nonexistent_path_errors_cleanly(tmp_path, capsys):
    store = tmp_path / "s"
    assert main(["ingest", str(tmp_path / "nope"), "--store", str(store)]) == 1
    cap = capsys.readouterr()
    assert "kgrag: error:" in cap.err and "Traceback" not in cap.err
    assert not store.exists()


def test_root_readme_index_is_not_ingested(tmp_path, capsys):
    corpus = tmp_path / "c"
    (corpus / "sub").mkdir(parents=True)
    (corpus / "README.md").write_text("# Index\n\nSpoiler answers live here.\n")
    (corpus / "a.md").write_text("# A\n\nAda Lovelace wrote notes.\n")
    (corpus / "sub" / "README.md").write_text("# Nested\n\nNested readme is real content.\n")
    assert main(["ingest", str(corpus), "--store", str(tmp_path / "s")]) == 0
    assert "documents: 2\n" in capsys.readouterr().out
