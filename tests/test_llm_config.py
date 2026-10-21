import urllib.request

import pytest

from kgrag.config import Config
from kgrag.llm import AnthropicLLM, OfflineLLM, get_llm


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network call attempted")
    monkeypatch.setattr(urllib.request, "urlopen", boom)


def test_offline_without_key():
    llm = get_llm({})
    assert isinstance(llm, OfflineLLM)
    out = llm.complete("sys", [{"role": "user", "content": "hi"}])
    assert out == llm.complete("sys", [{"role": "user", "content": "hi"}])


def test_blank_key_is_offline():
    assert isinstance(get_llm({"ANTHROPIC_API_KEY": "  "}), OfflineLLM)


def test_anthropic_with_key_hides_key():
    llm = get_llm({"ANTHROPIC_API_KEY": "sk-secret"})
    assert isinstance(llm, AnthropicLLM) and llm.model == "claude-sonnet-5-5"
    assert "sk-secret" not in repr(llm)


def test_config_defaults_and_validation():
    c = Config()
    assert str(c.corpus_dir) == "research" and str(c.store_dir) == ".kgrag"
    with pytest.raises(ValueError):
        Config(chunk_size=10, chunk_overlap=10)
