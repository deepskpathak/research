"""Runs the offline eval suite under plain pytest; fails if any threshold is missed."""
import json

import pytest

from evals import run

pytestmark = pytest.mark.filterwarnings("ignore")


@pytest.fixture(scope="module")
def result():
    return run.run_all()


def test_all_thresholds_met(result):
    failed = [m for m in result["metrics"] if not m["passed"]]
    assert not failed, run.format_table(result)


def test_all_categories_reported_with_enough_questions(result):
    assert set(result["categories"]) == {
        "retrieval", "multi_hop", "grounded", "refusal", "extraction", "idempotency"}
    assert {m["category"] for m in result["metrics"]} == set(result["categories"])
    assert result["questions"] >= 15


def test_leiden_university_question_is_multi_hop():
    q = json.loads((run.DATA / "questions.json").read_text(encoding="utf-8"))
    leiden = [i for i in q["multi_hop"] if "Leiden University" == i["answer_contains"]]
    assert leiden and len(leiden[0]["gold_sources"]) >= 2


def test_readme_answer_key_is_excluded(result):
    # If README.md were indexed it would answer questions verbatim and inflate scores.
    for cat in ("multi_hop",):
        for it in result["categories"][cat]["items"]:
            assert "README.md" not in it["cited"]


def test_top_entities_interface(result):
    assert result["top_entities"] and {"name", "degree"} <= set(result["top_entities"][0])


def test_metric_would_fail_when_quote_not_in_source(tmp_path):
    # Guards against a vacuous groundedness metric: a fabricated quote must be rejected.
    (tmp_path / "a.md").write_text("Real text.", encoding="utf-8")

    class Fake:
        def run(self, q):
            from kgrag.agent import AgentResult
            return AgentResult("x", [{"doc_path": "a.md", "chunk_id": "c", "quote": "Made up."}])

    out = run.eval_grounded(Fake(), [{"id": "x", "question": "q"}], tmp_path)
    assert out["citation_accuracy"] == 0.0


def test_cli_exit_codes(tmp_path, monkeypatch):
    out = tmp_path / "r.json"
    assert run.main(["--out", str(out)]) == 0
    assert json.loads(out.read_text())["passed"] is True
    monkeypatch.setattr(run, "_load", lambda n, _o=run._load: (
        {**_o(n), "retrieval_mrr": 2.0} if n == "thresholds.json" else _o(n)))
    assert run.main(["--out", str(out)]) == 1
