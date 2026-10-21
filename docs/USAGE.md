# Using kgrag

`kgrag` answers questions over a folder of Markdown/text files using a knowledge graph plus BM25 search, and always cites verbatim quotes. It needs Python 3.10+ and no runtime dependencies. No graph database is involved.

Related: [ARCHITECTURE](ARCHITECTURE.md), [HLD](HLD.md), [LLD](LLD.md).

## Install

```
pip install -e .[dev]
```

This installs the `kgrag` command (also available as `python -m kgrag`) and `pytest`. In zsh, quote the extra: `pip install -e '.[dev]'`.

## Ingest

```
kgrag ingest research/
```

Prints documents, chunks, entities, relations, skipped files and the store path. Details:

- Reads `.md`, `.markdown`, `.txt` recursively (nested folders are fine). Hidden paths and the corpus-root `README.md` are ignored. Other file types are counted as skipped.
- Rebuilds the store from scratch each time, so re-running gives identical counts.
- `--extractor heuristic` (default) or `--extractor llm` (uses the API when a key is set, otherwise falls back to heuristic with a note on stderr).
- A missing or empty corpus folder prints an error and exits 1.

## Ask

```
kgrag ask "Which university created the algorithm GraphRAG uses?"
kgrag ask "Which university created the algorithm GraphRAG uses?" --trace
kgrag ask "Which university created the algorithm GraphRAG uses?" --json
```

`--trace` prints each tool step; `--json` prints the full result (`answer`, `citations`, `trace`, `truncated`).

### Reading the output

Answers end with numbered citations: file path relative to the corpus, and a verbatim quote from the retrieved chunk. Multi-hop questions cite more than one document.

```
The Leiden algorithm is a community detection method created by ... at Leiden University in 2019. [1] It uses an LLM to extract entities ... [2] ...

Citations:
[1] leiden-algorithm.md: "The Leiden algorithm is a community detection method created by ... at Leiden University in 2019."
[2] graphrag.md: "It uses an LLM to extract entities and relations from documents ..."
```

If the corpus cannot support an answer (the relevance gate fails), the answer is the fixed message below with no citations:

```
The corpus does not contain the information needed to answer this question.
```

If the step limit is reached first, a note is printed to stderr and `truncated` is true in `--json`.

## Stats

```
kgrag stats
```

Prints `documents`, `chunks`, `entities`, `relations`, then a "Top entities by degree" list (degree = number of relations touching the entity, top 10).

## Entity

```
kgrag entity "GraphRAG"
```

Prints the entity name and type, aliases, number of mentioning chunks, and its relations as `A --type--> B`. Lookup is case-insensitive and folds plural/singular forms. An unknown name exits 1 with `Entity not found`.

## Store directory

All commands take `--store DIR` (default `.kgrag/`, gitignored). It holds `graph.json` and `bm25.json`; see the layout in [LLD](LLD.md). Querying before ingesting exits 1 with a message to run `kgrag ingest` first. Delete the directory to reset.

## Offline mode vs API-key mode

| | Offline (default) | API-key mode |
|---|---|---|
| Trigger | `ANTHROPIC_API_KEY` unset or blank | `ANTHROPIC_API_KEY` set and non-empty |
| Network | none | calls `api.anthropic.com` |
| Agent | deterministic policy, extractive answer | the model chooses tools and writes the answer |
| Citations | verbatim sentences from retrieved chunks | model quotes, kept only if verbatim in the cited chunk |

Enable API mode by exporting the key in your shell. Do not put it on the command line, in files in the repo, or in logs; kgrag never prints it.

```
export ANTHROPIC_API_KEY=...        # paste from your secret manager
export KGRAG_MODEL=claude-sonnet-5-5   # optional override
kgrag ask "..." --trace
```

If the model returns malformed output twice, errors, or gives no verifiable citations, the agent falls back to the offline policy and records a `fallback` step in the trace. In a regulated environment, get approval before enabling API mode, since question and chunk text are sent to the external API.

## Tests and evals

```
pytest                 # unit and integration tests, fully offline
python -m evals        # offline eval suite
```

The evals cover retrieval quality, multi-hop questions, groundedness and citation accuracy, not-found refusal, graph extraction quality and idempotency, run against `research/` with the offline LLM. Results are written to `evals/results.json` (gitignored); use `--corpus DIR` or `--out FILE` to change the inputs. The same gate runs under `pytest` via `tests/test_evals.py`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: kgrag` under pytest | Run from the repo root, or `pip install -e .[dev]`. |
| `command not found: kgrag` | Use `python -m kgrag ...`, or reinstall into the active environment. |
| Error about a missing store or unreadable store | Run `kgrag ingest` (also needed after a schema change). |
| `Corpus folder not found` / `No supported documents found` | Check the path; add `.md`, `.markdown` or `.txt` files. |
| "skipped files" is nonzero | Unsupported file types under the corpus; expected. |
| Everything answers "does not contain..." | Rephrase with terms from the corpus, or check `kgrag stats` and `--trace`. |
| `--extractor llm` prints a note about the key | No key set; the heuristic extractor was used. |
| Answer ignores a new document | Re-run `kgrag ingest`; the store is not updated automatically. |
