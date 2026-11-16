# Personas and the problem wiselotus solves

Status: draft research note, 2026-11-14. Part 1 of the research effort under `docs/research/`.

## How to read this note

- Claims about wiselotus come from `AGENTS.md` and `docs/decisions/0001-borrowed-patterns.md` in this repo. They describe the design, not market results.
- External facts carry a bracketed source number that maps to the `## Sources` list at the end, for example [1].
- Anything not confirmed from a page fetched while writing this note is marked **Unverified**.
- Personas are working hypotheses built from the design and from the cited studies. They are not interview data. **Unverified** against real customers.

## What wiselotus is, in one paragraph

wiselotus turns code review history (merge requests, review comments, applied suggestions, judge verdicts) into a graph of lessons, then serves small scoped slices of it to agent harnesses at the moment they generate or review code. The pipeline is ingest, extract, curate, serve, learn (`AGENTS.md`).

Pipeline diagram (text form): five stages in a row, **ingest**, **extract**, **curate**, **serve**, **learn**. A feedback arrow runs from **learn** back to **curate**, labelled "outcomes move confidence".

## Personas

Five personas. Each lists goals, pains, current workaround and what they would measure. The measures are proposals for wiselotus, not figures from a study.

### Developer using an agent harness

- **Goals:** the agent's first draft already respects what reviewers in this repo keep asking for, so fewer review round trips.
- **Pains:** the agent repeats mistakes that a reviewer already flagged on an earlier change. Instruction files help only with what someone remembered to write down.
- **Current workaround:** a hand-written `AGENTS.md` or `CLAUDE.md`. AGENTS.md is described as "a README for agents", and agents.md reports use in over 60k open-source projects [3].
- **Success measure:** fewer review comments per change that repeat an earlier lesson, and lesson `helped` versus `misled` outcome counts from served slices.

### Code reviewer or tech lead

- **Goals:** stop writing the same comment again. Keep review time for design and risk.
- **Pains:** expectations live in closed merge request threads. A published Microsoft study (Bacchelli and Bird, ICSE 2013) found that finding defects remains the main motivation for review, but reviews also deliver knowledge transfer and team awareness [2]. That value is lost when the knowledge cannot be found again.
- **Current workaround:** copy and paste of prior comments, wiki style guides, and verbal reminders. **Unverified** as a measured practice.
- **Success measure:** share of review comments that restate an existing lesson, and reviewer time per change.

### Platform or developer-experience team

- **Goals:** one mechanism that works across the several agent harnesses their developers use.
- **Pains:** each harness has its own instruction format and per-repo files drift apart. **Unverified** at scale, the drift claim is argued in the problem section below.
- **Current workaround:** curated instruction files per repo, plus tool connectors. Anthropic's MCP announcement (2024-11-25) says it "provides a universal, open standard for connecting AI systems with data sources" [4].
- **Success measure:** harnesses supported through one contract (MCP tool plus CLI), lessons retired for staleness, tokens per slice.

### Engineering leader or budget owner

- **Goals:** faster delivery and less rework without adding review headcount, and evidence that an AI investment pays back.
- **Pains:** agent output increases review demand, and spend is hard to tie to outcomes. **Unverified**: no sourced figure on this is cited here. Task T3 covers business value.
- **Current workaround:** training, style guides, bigger context windows. **Unverified** as a measured practice. Longer inputs are not a free fix, see problem statement [5][6].
- **Success measure:** aggregate misled rate, tokens per slice, cost per 100 review events (tracked metrics in `AGENTS.md`). Never per person.

### Security or compliance owner in a regulated firm

- **Goals:** no secrets or personal data stored, no write access to source repositories, an audit trail for why guidance was given.
- **Pains:** review comments can contain secrets, personal data and text that reads like instructions to an agent. This is a design premise taken from `AGENTS.md` rules 1 and 5, not an observed finding.
- **Current workaround:** blocking tools outright, or manual redaction. **Unverified** as industry practice.
- **Success measure:** zero secrets in stored excerpts (redaction at ingest), every served lesson links to evidence, read-only toward sources.

## Problem statement

Three linked problems, each stated with what is sourced and what is not.

### 1. Review knowledge stays in threads and is repeated

- Modern code review is tool-based and lightweight, and has become the norm. A case study at Google combined 12 interviews, a survey of 44 respondents and logs of 9 million reviewed changes [1].
- At Microsoft, a 2013 study (Bacchelli and Bird, ICSE 2013) found that finding defects remains the main motivation for review, but reviews are less about defects than expected and instead provide benefits such as knowledge transfer and increased team awareness [2].
- Together these support that review comments carry durable knowledge. They do not measure how often comments are repeated. **Unverified**: no fetched source here quantifies repeated comments or review load, so this note makes no number claim about either.

### 2. Agents do not learn from past reviews

- Language models can use long inputs unevenly. One paper reports that performance is often highest when relevant information is at the beginning or end of the input, and degrades when it is in the middle [5].
- A 2025 technical report evaluating 18 models reports that "model performance consistently degrades with increasing input length" [6]. The report text fetched was truncated at about 68 percent, so only the abstract and introduction quotes are relied on.
- Implication for design: dumping all review history into context is not a safe fix. A small, ranked, relevant slice is the design response. This is an inference, marked **Unverified** as a measured result for wiselotus.
- That a given harness does not persist lessons across sessions is **Unverified** here, because it differs per harness and no source was fetched.

### 3. Static instruction files drift

- Static files such as AGENTS.md exist, and agents.md reports use in over 60k open-source projects [3].
- That they drift out of date is plausible by construction (a human must edit them) but **Unverified**: no fetched study measures drift.
- wiselotus design response: lessons carry evidence, confidence moves with outcomes and recency, and lessons that mislead decay and retire (`AGENTS.md` rule 4 and domain words).

## What is unique about wiselotus (design claims)

These are claims about how the system is specified. Nothing here asserts that competitors lack them. The landscape is covered in task T2.

- **Evidence-backed lessons.** A lesson without evidence is dropped (rule 2). Each served lesson has provenance.
- **Scoped slices under a token budget.** Scope is repo, paths, symbols, language and change type (domain words). Default budget is 2k tokens. An empty slice is valid (rule 3).
- **Outcome-driven confidence.** Outcomes `helped`, `ignored`, `misled` move confidence. Confidence is never derived from who wrote the comment (rule 4 and domain words).
- **Review content is data.** Comments and judge output are quoted with provenance. Instruction-shaped text is stripped from slices (rule 1).
- **No per-person metrics.** No ranking or naming of individuals, and no reviewer identity in a lesson (rule 6).
- **Deterministic before model.** Normalization, dedupe, scope matching and ranking are code. Model calls go through one provider adapter (rule 7).
- **Least data and read-only.** Redaction at ingest, short excerpts, no pushes or comments to source repos (rules 5 and 8).
- **Harness-agnostic.** Every serve capability is an MCP tool and a CLI command with one contract (rule 9).

Most of these patterns are borrowed from sibling projects, per `docs/decisions/0001-borrowed-patterns.md`. The combination, not any single idea, is the claim. Novelty versus the market is **Unverified** until T2.

## Open questions

- Which personas are real buyers? Needs interviews. **Unverified**.
- How often are review comments repeated in a real repo? Needs measurement on fixtures or public repos.
- Do slices actually lower repeated comments? To be tested by `make eval`, not yet built.

## Sources

1. https://research.google/pubs/modern-code-review-a-case-study-at-google/ (fetched, abstract summary: 12 interviews, 44 survey respondents, 9 million changes)
2. https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/ (fetched, Bacchelli and Bird, ICSE 2013)
3. https://agents.md/ (fetched, "a README for agents", "over 60k open-source projects")
4. https://www.anthropic.com/news/model-context-protocol (fetched, post dated 2024-11-25, "a universal, open standard for connecting AI systems with data sources")
5. https://arxiv.org/abs/2307.03172 (fetched, Lost in the Middle)
6. https://www.trychroma.com/research/context-rot (fetched, truncated at about 68 percent; originally https://research.trychroma.com/context-rot)
