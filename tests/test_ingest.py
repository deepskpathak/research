import logging

import pytest

from kgrag.ingest import chunk_document, load_corpus
from kgrag.models import Document


def test_loads_md_and_txt(mini_corpus):
    docs = {d.path: d for d in load_corpus(mini_corpus)}
    assert set(docs) == {"alpha.md", "beta.txt"}
    assert "Ada Lovelace" in docs["alpha.md"].text


def test_title_from_heading_or_filename(mini_corpus):
    docs = {d.path: d for d in load_corpus(mini_corpus)}
    assert docs["alpha.md"].title == "Alpha Notes"
    assert docs["beta.txt"].title == "beta"


def test_unsupported_skipped_with_warning(tmp_path, caplog):
    (tmp_path / "a.md").write_text("# A\n\ntext")
    (tmp_path / "img.png").write_bytes(b"\x89PNG")
    with caplog.at_level(logging.WARNING, logger="kgrag.ingest"):
        docs = load_corpus(tmp_path)
    assert [d.path for d in docs] == ["a.md"]
    assert "img.png" in caplog.text


def test_nested_and_hidden(tmp_path):
    (tmp_path / "sub" / "deep").mkdir(parents=True)
    (tmp_path / "sub" / "deep" / "n.markdown").write_text("# Deep\n\nx")
    (tmp_path / ".hidden.md").write_text("# no")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "x.md").write_text("# no")
    (tmp_path / "top.txt").write_text("hi")
    assert [d.path for d in load_corpus(tmp_path)] == ["sub/deep/n.markdown", "top.txt"]


def test_missing_folder(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_corpus(tmp_path / "nope")


def test_empty_folder(tmp_path):
    (tmp_path / "x.png").write_bytes(b"1")
    with pytest.raises(ValueError, match="No supported documents"):
        load_corpus(tmp_path)


def test_ids_stable(mini_corpus):
    a, b = load_corpus(mini_corpus), load_corpus(mini_corpus)
    assert [d.id for d in a] == [d.id for d in b]
    assert len({d.id for d in a}) == len(a)
    ca = [c.id for d in a for c in chunk_document(d, 40, 10)]
    cb = [c.id for d in b for c in chunk_document(d, 40, 10)]
    assert ca == cb and len(set(ca)) == len(ca)


def test_offsets_exact_on_research_corpus():
    from pathlib import Path
    root = Path(__file__).parent.parent / "research"
    for doc in load_corpus(root):
        for size, overlap in [(200, 30), (800, 100), (50, 0)]:
            chunks = chunk_document(doc, size, overlap)
            assert chunks
            for c in chunks:
                assert doc.text[c.start:c.end] == c.text
                assert c.doc_id == doc.id and c.text.strip()


def test_paragraph_and_heading_boundaries():
    text = "# H1\n\npara one.\n\npara two.\n## H2\nunder h2\n"
    doc = Document(id="d", path="p", title="t", text=text)
    chunks = chunk_document(doc, size=100, overlap=5)
    # small paragraphs pack together, but a heading always starts a new chunk
    assert [c.text for c in chunks] == ["# H1\n\npara one.\n\npara two.", "## H2\nunder h2"]
    chunks = chunk_document(doc, size=16, overlap=5)
    assert [c.text for c in chunks] == ["# H1\n\npara one.", "para two.", "## H2\nunder h2"]


def test_long_paragraph_windows():
    doc = Document(id="d", path="p", title="t", text="a" * 250)
    chunks = chunk_document(doc, size=100, overlap=20)
    assert [(c.start, c.end) for c in chunks] == [(0, 100), (80, 180), (160, 250)]


def test_bad_params():
    doc = Document(id="d", path="p", title="t", text="x")
    with pytest.raises(ValueError):
        chunk_document(doc, 10, 10)
