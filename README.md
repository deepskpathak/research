# research
Research Docs, plus `kgrag`, a knowledge graph and agentic RAG system over `research/`.

## Setup
```
pip install -e .[dev]
pytest
```

## Dependencies
- Runtime: Python 3.10+ standard library only. No runtime dependencies are declared.
- Dev: `pytest` (optional extra `dev`).
- Network: none by default. `AnthropicLLM` calls api.anthropic.com **only** when `ANTHROPIC_API_KEY` is set (model `claude-sonnet-5-5`, override with `KGRAG_MODEL`). Otherwise the deterministic `OfflineLLM` is used. Flag for approval before enabling in a regulated environment.

## Layout
- `kgrag/` package (models, config, llm; more modules arrive in later tasks)
- `research/` sample corpus (see `research/README.md`)
- `tests/fixtures/` tiny test corpus
