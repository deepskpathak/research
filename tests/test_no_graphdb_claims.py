"""kgrag uses an in-memory, JSON-persisted graph; it must not reference a graph database."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_no_kgrag_module_mentions_neo4j():
    files = sorted((ROOT / "kgrag").rglob("*.py"))
    assert files, "expected kgrag/*.py files"
    offenders = [str(f.relative_to(ROOT)) for f in files
                 if re.search(r"neo4j", f.read_text(encoding="utf-8"), re.IGNORECASE)]
    assert offenders == []


def test_readme_states_no_graph_database():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "no Neo4j" in text and "no Cypher" in text
    # Any README line mentioning Neo4j/Cypher must be a negation.
    for line in text.splitlines():
        if re.search(r"neo4j|cypher", line, re.IGNORECASE):
            assert re.search(r"\bno\b|\bnot\b|without", line, re.IGNORECASE), line


def test_pyproject_has_no_graphdb_dependency():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert not re.search(r"neo4j|cypher", text, re.IGNORECASE)
    assert "dependencies = []" in text
