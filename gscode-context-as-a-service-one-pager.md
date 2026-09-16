# Context as a Service: The GSCode Standards Repo

**Owner:** Deepak Kumar, Core Engineering | **Status:** Draft for review | **Date:** 16 Sep 2026 | **Audience:** GSCode team, SDLC Engineering, EngHub

## Problem

GSCode gives every harness the same SDD chain (`/analyze` → `/specify` → `/plan` → `/tasks` → implement → review) and the same code graph. What it does not give the agent is the firm's rules. Enterprise standards, BU conventions, and product-family constraints live in Confluence pages, wiki tables, and individual `CLAUDE.md` files. The agent either never sees them or gets a front-loaded instruction file that bloats context and goes stale. Every team re-teaches GSCode by hand, or does not. The Skills RFC already names the need (enterprise standards + identity skills); this one-pager turns that into a product surface: **one governed standards repo, plugged into GSCode, delivered to agents at the moment of lookup.**

## Goals

- **Coverage:** 100% of GSCode runs (harness and headless) resolve and apply enterprise standards with no per-repo setup.
- **Precision:** agents receive only standards matched to the repo's identity and tech stack, not the full corpus (target: under 8k tokens of standards context per run).
- **Enforcement:** every applied standard is logged (source, version, evidence) and checkable at `/codereview`.
- **Ownership:** standard owners publish and update through a normal MR flow, with changes reaching agents on the next GSCode run.

## Non-Goals (v1)

- **Not a skills marketplace.** Procedural "how to build X" content stays in EngHub certified skills. Standards are constraints and conventions ("what must be true").
- **Not a widening of the local MCP.** The 10 Sep decision scopes the local MCP to graph generation only. Standards delivery goes through the command layer, not the graph MCP.
- **Not a replacement for EngHub.** Enterprise-tier standards are certified through EngHub's existing process; the repo is the authoring source, not a parallel certification path.
- **Not private repos.** Worker pool restriction (AI-enabled, non-private) still applies.
- **Not runtime policy enforcement.** v1 informs and logs; it does not block a merge.

## User Stories

- As a **developer running Claude Code**, I want the plan and code GSCode produces to already follow my BU's conventions so that I stop hand-pasting rules into prompts.
- As a **standards owner (e.g. Tech Risk, Testing)**, I want to publish a standard via MR to one repo so that every agent picks it up without me integrating with each harness.
- As a **headless worker pool run**, I want standards resolved from the repo's identity at `/initialize` so that unattended runs do not need a human to point at sources.
- As a **reviewer**, I want to see which standards were applied and where so that I can audit AI-generated changes.
- As a **standard author**, I want to pilot a draft standard against my own repo before certification so that I can prove it works.

## Requirements

**P0 (must ship)**
- **Repo layout:** `standards/<domain>/<slug>/STANDARD.md` with required frontmatter: `id`, `version`, `owner`, `scope` (`enterprise` | BU ID | SBU ID | app-family ID), `tech_stack` tags, `keywords`, `status` (`draft` | `preview` | `certified`), `supersedes`. CODEOWNERS on `/standards/` for MD approval at `certified`.
- **Index build:** CI compiles `standards-index.yml` on merge and publishes it to a fetchable URL, reusing the existing `gscode.skillsIndexUrl` pattern.
- **Resolution:** GSCode resolves repo identity once at `/initialize` (GitLab project ID → SPR API → BU/SBU/App Family, matched by ID). Enterprise standards always apply; scoped standards apply only on identity match. Unresolved identity → enterprise only.
- **Retrieval:** one keyword pass after `/specify` (repo tech stack + feature spec) selects matching standards; results stay available through `plan`, `implement`, `codereview`. Unreachable index is recorded as unreachable, never as "nothing found".
- **Logging:** every applied standard logged with id, version, timestamp, and the file or task it influenced.
- **On-demand lookup:** `/standard <topic>` command for a developer, and an equivalent lookup step the agent can invoke mid-task.

**P1 (fast follow)**
- **Checks section:** each STANDARD.md may carry a `## Check` block that `/codereview` evaluates and reports pass/fail on.
- **Preview pinning:** a repo can pin a `draft` or `preview` standard by path until certified.
- **Standard-to-EngHub sync:** `certified` standards auto-publish to EngHub so non-GSCode harnesses (Devin, Codex) get them over EngHub MCP.

**P2 (design for, do not build)**
- Blocking enforcement of P0-severity standards at MR creation.
- Telemetry dashboard: standards hit rate, staleness, and unresolved-identity rate by BU.
- Semantic (embedding) retrieval replacing keyword matching.

## Success Metrics

| Metric | Target at 90 days | How measured |
|---|---|---|
| Runs applying ≥1 standard | 95% of GSCode runs | Skill/standard log |
| Standards context size per run | < 8k tokens median | Run telemetry |
| Standards published | 20 enterprise, 10 scoped, 5 owners | Repo index |
| Time from merge to agent availability | < 1 run cycle | Index publish timestamp vs first log hit |
| Reviewer audit coverage | 100% of MRs carry applied-standards list | MR description template |

## Open Questions

- **Blocking (Skill Registry / SDLC Eng):** which identity level backs which tier? BU vs SBU vs App Family, and who owns the mapping.
- **Blocking (EngHub):** does a `certified` standard in the repo satisfy EngHub certification, or must it be re-published? Avoid two sources of truth.
- **Non-blocking (Engineering):** should `/standard` lookup be a command-catalog fetch (v1 proposal) or a separate standards MCP for harness parity? Recommendation: command layer first, MCP only if Devin/Codex adoption demands it.
- **Non-blocking (Tech Risk):** minimum metadata for an AI-control audit trail (AI-4, AI-7).

## Timeline

- **Phase 1 (4 wks):** repo scaffold, frontmatter schema, index CI, 5 enterprise standards from SDLC Engineering. Pilot on the GSCode repo itself.
- **Phase 2 (4 wks):** identity resolution + scoped standards with two BUs; logging in MR descriptions.
- **Phase 3 (4 wks):** `## Check` blocks in `/codereview`, EngHub sync, preview pinning.

**Dependencies:** SPR API access from worker pool, EngHub certification alignment, Skill Registry identity tagging.
