"""LLM abstraction. Offline by default; Anthropic only when ANTHROPIC_API_KEY is set."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Mapping, Protocol, Sequence, runtime_checkable

DEFAULT_MODEL = "claude-sonnet-5-5"
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"

Message = Mapping[str, str]  # {"role": "user"|"assistant", "content": "..."}


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, system: str, messages: Sequence[Message]) -> str: ...


class OfflineLLM:
    """Deterministic stub: echoes the last user message so pipelines run without a network."""

    def complete(self, system: str, messages: Sequence[Message]) -> str:
        last = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        return f"[offline] {last.strip()}"


class LLMError(RuntimeError):
    pass


class AnthropicLLM:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, max_tokens: int = 1024,
                 timeout: float = 60.0) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout

    def __repr__(self) -> str:  # never expose the key
        return f"AnthropicLLM(model={self.model!r})"

    def complete(self, system: str, messages: Sequence[Message]) -> str:
        body = json.dumps({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
        }).encode("utf-8")
        req = urllib.request.Request(API_URL, data=body, method="POST", headers={
            "content-type": "application/json",
            "x-api-key": self._api_key,
            "anthropic-version": API_VERSION,
        })
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise LLMError(f"Anthropic API returned HTTP {e.code}") from None
        except urllib.error.URLError as e:
            raise LLMError(f"Anthropic API request failed: {e.reason}") from None
        return "".join(b.get("text", "") for b in payload.get("content", [])
                       if b.get("type") == "text")


def get_llm(env: Mapping[str, str] | None = None) -> LLMClient:
    """Return AnthropicLLM iff ANTHROPIC_API_KEY is set and non-empty, else OfflineLLM."""
    env = os.environ if env is None else env
    key = env.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return AnthropicLLM(key, model=env.get("KGRAG_MODEL") or DEFAULT_MODEL)
    return OfflineLLM()
