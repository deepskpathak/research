# Landscape and patterns: how the industry injects review and repo knowledge into coding agents

Status: draft, 2026-11-14. Task T2 of the wiselotus research effort.

## Method and labels

Every claim below comes from a page fetched during this task, or is marked **Unverified**. Only numbers stated on those pages are reported. Result labels:

- **Vendor-reported**: measured and published by the party selling or running the system.
- **Independent**: analysis by a party with no stake in the system.
- **Peer-reviewed venue, authors' own evaluation**: the page names a venue, but the numbers are the authors' own and were not replicated here.
- **Preprint, authors' own evaluation**: arXiv abstract page only; peer-review status not confirmed here.
- **Vendor docs (no results)**: product documentation describing behavior, with no measured outcome.

Limits: for arXiv works only the abstract page was read, not the full paper. No independent replication of any tool's quality claims was found in the pages read. Absence of a feature on a fetched page is not proof the product lacks it.

## 1. Industry products and approaches

| Product | How knowledge is captured | Scope | Stated limitation | Label | Source |
|---|---|---|---|---|---|
| AGENTS.md | Manual: you write it; described as a README for agents. | Nested files; closest to the edited file wins. | None stated; plain Markdown, no required fields. | Vendor docs (no results) | [agents](https://agents.md/) |
| GitHub Copilot custom instructions | Manual (or ask the cloud agent to generate one). Learning from review feedback is not described on the page. | Repo-wide file, path-specific files with an applyTo glob, nearest AGENTS.md. Code review reads them from the PR head branch. | Path-specific instructions only supported for Copilot cloud agent and Copilot code review (on GitHub.com). | Vendor docs (no results) | [copilot](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) |
| Claude Code memory (CLAUDE.md and auto memory) | CLAUDE.md is manual. Auto memory is written by Claude from corrections across sessions. | CLAUDE.md at managed, user, project or local level. Auto memory per repository, shared across worktrees. Loaded at start: first 200 lines or 25KB. | Claude treats memory as context, not enforced configuration. Claude does not save something every session. | Vendor docs (no results) | [cc](https://code.claude.com/docs/en/memory) |
| CodeRabbit Learnings | Learned from chat interactions; can import a file via a PR comment; page also mentions CodeRabbit-inferred learnings from the review pipeline. | Setting knowledge_base.learnings.scope: local, global or auto (local for public repos, global for private). | Learnings from an open PR first apply only to that PR, then repository-wide after merge. Page points to review instructions or coding guidelines for formal standards. | Vendor docs (no results) | [cr](https://docs.coderabbit.ai/guides/learnings) |
| Greptile | Learns from thumbs up/down reactions and replies; builds a graph of the codebase. | Connected repositories on GitHub, GitLab, Bitbucket and others. | None stated. The claim that after 2-3 weeks it stops commenting on things you do not care about is the vendor's own and unmeasured on the page. | Vendor-reported | [gt](https://www.greptile.com/docs/introduction) |
| Sourcegraph Cody context | Retrieval at prompt time (keyword search, Sourcegraph search, code graph) plus @-mentions. No persistent learned knowledge described. | Single or multiple linked repositories. | Context window limits (administrators can change the maximum); a too-small context window can trigger errors such as 'You've selected too much code' on edit or describe prompts. | Vendor docs (no results) | [cody](https://sourcegraph.com/docs/cody/core-concepts/context) |
| Qodo PR-Agent | Commands /describe, /review, /improve, /ask; the page says /review and /ask use a single LLM call. No learning feature described on the fetched page. | Per pull request. | Now a community-maintained legacy project of Qodo per its README. Qodo Merge learning: see the next row. | Vendor docs (no results) | [pra](https://github.com/qodo-ai/pr-agent) |
| Qodo Merge auto best practices | Once a month, Qodo analyzes accepted suggestions to generate a custom `.pr_agent_auto_best_practices` Wiki file. Suggestions that match it are labelled "Learned best practice". Flag: `enable_auto_best_practices = true`. | A Wiki file; a Wiki must be enabled. Platforms supported: GitHub. | The page documents the Qodo v1 experience, which "is being sunset". Whether v2 keeps this feature is **Unverified** (the page does not mention v2). | Vendor docs (no results) | [qm](https://docs.qodo.ai/v1/features/best-practices) |
| Cursor rules | Not read: the docs URL redirected to a different page and was not followed. | - | - | **Unverified** | - |
| Model Context Protocol | Open standard for connecting AI applications to external systems. | Clients named on the page include Claude, ChatGPT, VS Code and Cursor. | No numbers on the page. | Vendor docs (no results) | [mcp](https://modelcontextprotocol.io/introduction) |

Reading across the table: capture is mostly manual (instruction files) or learned from chat and reactions (CodeRabbit, Greptile, Claude auto memory). Qodo Merge auto best practices learns from accepted suggestions, which makes it the closest prior art found to the wiselotus "suggestion applied" review event (v1 docs, being sunset; v2 support **Unverified**). On the fetched pages, none describes per-lesson evidence links, confidence from served outcomes, or retirement of lessons that mislead. That is the gap wiselotus targets, stated as an observation of these pages and not a claim about the products' internals.

## 2. Published case studies

### Google: resolving code review comments with ML

Label: Vendor-reported (Google's own measurements, not independent). Source: <https://research.google/blog/resolving-code-review-comments-with-ml/>

- Authors: Alexander Frömmgen and Lera Kharatyan, Google Core Systems & Experiences; post dated May 23, 2023.
- A fine-tuned large sequence model (DIDACT methodology) proposes code edits that address reviewer comments.
- Offline: 'the model addresses 52% of comments with a target precision of 50%'.
- Online: '40% to 50% of all previewed suggested edits are applied by code authors'.
- Preview rate about 20% at beta and about 40% at launch; of applied suggested edits (per the post), 'more than 70% of these are applied in the code review tool and fewer than 30% are applied in the IDE'.
- Authors 'require an average of ~60 minutes' of active shepherding time; the phrase links to an earlier Google publication (pub49446, https://research.google/pubs/pub49446/), not a measurement of this system.
- The 12-week A/B experiment is listed as future work, so the page reports no productivity result.
- Relevance: shows that the review comment is a usable signal and that applied edits are a measurable outcome, which maps to the wiselotus Outcome concept. It resolves comments after they are written; it does not prevent them.

### AutoCommenter: coding best practices in code review

Label: Peer-reviewed venue (AIware '24), authors' own evaluation. Source: <https://arxiv.org/abs/2405.13565>

- Paper: 'AI-Assisted Assessment of Coding Practices in Modern Code Review' (arXiv 2405.13565, to appear at AIware '24).
- An LLM-backed system that learns and enforces coding best practices during review, for C++, Java, Python and Go.
- Deployed in a large industrial setting reaching 'tens of thousands of developers'; reports 'a positive impact on the developer workflow'.
- The abstract page gives no numeric results and does not name the organization. Google Research lists the paper on its publications site as 'AI-assisted Assessment of Coding Practices in Industrial Code Review' (2024), which resolves the organization to Google: <https://research.google/pubs/ai-assisted-assessment-of-coding-practices-in-industrial-code-review/>
- Relevance: closest published analogue to turning review practice into enforced, reusable guidance.

### Agent READMEs: empirical study of context files

Label: Independent (arXiv preprint; peer-review status not stated on the page). Source: <https://arxiv.org/abs/2511.12884>

- Studies 2,303 agent context files from 1,925 repositories (AGENTS.md, CLAUDE.md and similar).
- Coverage: test procedures 75.9%, implementation details 70.8%, architecture 68.1%; security 14.8% and performance 14.5%.
- It characterizes the files. It does not measure agent performance, so it is not evidence that such files help. A separate study did measure it: arXiv:2602.11988v3 (Gloaguen, Mündler-Sasahara, Müller, Raychev, Vechev, 'Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?'; Preprint, authors' own evaluation) reports that providing context files 'does not generally improve task success rates' while increasing inference cost by over 20% on average. Its v1 (12 Feb 2026) said context files 'tend to reduce' task success rates; v3 (revised 29 Sep 2026) softened this.
- Relevance: confirms hand-written context files are widespread, and that some review-relevant topics (security, performance) are rarely written down. Whether review history fills that gap is a hypothesis, not a finding.

### Mem0: memory layer benchmark claims

Label: Vendor-reported (authors' paper and the project README, both self-run). Source: <https://arxiv.org/abs/2504.19413>

- Paper: 26% relative improvement in the LLM-as-a-Judge metric over OpenAI on LOCOMO; graph variant about 2% higher overall than base; versus full-context, 91% lower p95 latency and more than 90% token cost saved.
- GitHub README (April 2026 algorithm): LoCoMo 71.4 to 92.5, LongMemEval 67.8 to 94.4, BEAM (1M) 64.1, BEAM (10M) 48.6. The README states scores reflect the managed platform with proprietary optimizations not in the open-source SDK.
- These are conversational memory benchmarks, not code review. Transfer to review lessons is **Unverified**.
- Relevance: the token saving versus stuffing full history into context supports small, scoped slices.

### Greptile: models reviewing their own code

Label: Vendor-reported (company blog post, 2026-07-21; no peer review stated). Source: <https://www.greptile.com/blog/model-inversion>

- Two datasets of 500 PRs each, one authored by Claude Code and one by Codex; recall on high-severity bugs only; LLM-as-judge matching.
- Finding: each model finds more bugs in the other model's code. The page lists 60.0%, 62.0%, 53.7% and 50.5% but the fetched text did not map values to cells, so no number is reproduced as a result here.
- Relevance (inference): the post suggests a second model catches bugs the authoring model misses ('A different model, with different instincts, helps you fill in the gaps'), which supports judge verdicts as a review event source. The post gives no cost data.

## 3. Open-source and academic works

| Work | What it does and what the source states | Label | Source |
|---|---|---|---|
| MemGPT / Letta | Tiered 'virtual context management' inspired by OS memory; document analysis and multi-session chat. | Preprint, authors' own evaluation (abstract has no numbers) | <https://arxiv.org/abs/2310.08560>, <https://github.com/letta-ai/letta> |
| Mem0 | Extract, consolidate, retrieve memory from conversations, plus graph variant. | Preprint, authors' own evaluation (see case study above) | <https://arxiv.org/abs/2504.19413>, <https://github.com/mem0ai/mem0> |
| Reflexion | Verbal reflections in an episodic memory buffer, no weight updates. Abstract: 91% pass@1 on HumanEval versus 80% for the previous GPT-4 state of the art (whether the 80% was measured by the authors is not stated). | Preprint, authors' own evaluation | <https://arxiv.org/abs/2303.11366> |
| Voyager | Skill library of executable code reused across worlds, with feedback and self-verification. Abstract: 3.3x more unique items, 2.3x longer distances, up to 15.3x faster milestones in Minecraft. | Preprint, authors' own evaluation | <https://arxiv.org/abs/2305.16291> |
| RAG (Lewis et al.) | Parametric model plus dense vector index; state of the art on three open-domain QA tasks. Accepted at NeurIPS 2020. | Peer-reviewed venue, authors' own evaluation | <https://arxiv.org/abs/2005.11401> |
| SWE-bench | 2,294 problems from 12 Python repositories; best model at the time (Claude 2) solved 1.96%. ICLR 2024. Dated result, not current capability. | Peer-reviewed venue, authors' own evaluation | <https://arxiv.org/abs/2310.06770> |
| CodeReviewer | Dataset from nine languages of open-source projects and a model with four code-review-specific pre-training tasks; evaluated on quality estimation, comment generation and code refinement. ESEC/FSE 2022. The abstract page does not list an organization. | Peer-reviewed venue, authors' own evaluation (abstract has no numbers) | <https://arxiv.org/abs/2203.09095> |
| ReWOO | Decouples reasoning from observations: 5x token efficiency and 4% accuracy gain on HotpotQA, per the abstract. | Preprint, authors' own evaluation | <https://arxiv.org/abs/2305.18323> |

Patterns visible across these: memory with a tight read budget (MemGPT, Mem0, Claude auto memory), a feedback signal that revises stored knowledge (Reflexion), and a verified reusable library (Voyager). None of the abstracts read covers review-derived lessons with provenance, so that combination is not evidenced in this survey.

## 4. Pattern table

| Pattern | Examples | Evidence | Failure modes | Relevance to wiselotus | Label |
|---|---|---|---|---|---|
| Hand-written repo instruction files | AGENTS.md, Copilot instructions, CLAUDE.md | Widespread: 2,303 files in 1,925 repos studied. Effect on agent quality not measured there; arXiv:2602.11988v3 (Preprint, authors' own evaluation) measured it and found no general gain in task success and over 20% higher inference cost on average. | Manual upkeep; treated as context, not enforced; security and performance rarely covered (14.8%, 14.5%). | Delivery format. wiselotus slices should be renderable into these files and MCP/CLI. | Independent |
| Feedback-learned review preferences | CodeRabbit Learnings, Greptile reactions | Docs only. Greptile '2-3 weeks' is a vendor claim. | Learnings from an open PR apply only to that PR until it merges, then become repository-wide (CodeRabbit). Unclear provenance per learning on the fetched pages. | Closest peer. wiselotus differs by mandatory evidence links and outcome-driven confidence. | Vendor-reported |
| Agent-written memory from corrections | Claude Code auto memory | Docs only. | Not saved every session; only first 200 lines or 25KB loaded. | Shows a hard load budget is normal; supports a 2k token slice. | Vendor docs (no results) |
| Prompt-time retrieval of code context | Sourcegraph Cody, RAG | RAG: state of the art on three QA tasks (NeurIPS 2020). | Context window limits; a too-small (admin-configurable) context window can trigger 'You've selected too much code' errors. | Scope matching and ranking before the model sees anything. | Peer-reviewed venue, authors' own evaluation |
| Tiered or virtual memory | MemGPT / Letta | Paper reports evaluations; abstract has no numbers. | Complexity of agent-managed paging. **Unverified** | Heavier than needed; wiselotus serves a fixed budget deterministically. | Preprint, authors' own evaluation |
| Extract, consolidate, retrieve memory | Mem0 | Self-reported: 26% relative LLM-judge gain, 91% lower p95 latency, over 90% token saving versus full context. | Benchmarks are conversational; README scores include proprietary optimizations absent from the OSS SDK. | Supports small slices over full history; does not address review provenance. | Vendor-reported |
| Reflection and episodic buffer | Reflexion | 91% HumanEval pass@1 versus 80% (authors' abstract). | Needs a reliable feedback signal; HumanEval is not review work. **Unverified** | Outcome feedback (helped, misled) is the same loop at lesson level. | Preprint, authors' own evaluation |
| Reusable skill or lesson library | Voyager | Minecraft only: 3.3x items, 15.3x faster milestones. | Environment is not code review. Transfer **Unverified** | Durable library plus verification maps to the lesson graph. | Preprint, authors' own evaluation |
| ML-resolved review comments | Google DIDACT | 52% of comments at 50% target precision offline; 40% to 50% of previewed edits applied. | Acts after the comment exists; no productivity result reported yet. | Applied suggestions are a measurable outcome event. | Vendor-reported |
| Best-practice enforcement from review | AutoCommenter | Deployed to tens of thousands of developers; no numbers in the abstract. | Evidence for quality beyond 'positive impact' not on the page. | Direct analogue for curated, scoped guidance. | Peer-reviewed venue, authors' own evaluation |
| Review datasets and benchmarks | CodeReviewer, SWE-bench | Peer-reviewed venues; SWE-bench best result 1.96% at publication. | Public data is open-source PRs, not private team norms; results age quickly. | Source of public fixtures and eval ideas; precision must still be measured on wiselotus's own data. | Peer-reviewed venue, authors' own evaluation |
| Open tool protocol | MCP | Adopted by named clients; no numbers. | Not a quality mechanism by itself. | Rule 9: every serve capability as MCP tool plus CLI. | Vendor docs (no results) |

## 5. Takeaways and open questions

- Hand-written files and learned preferences exist; a traceable, outcome-weighted lesson graph served under a small budget is not described on the fetched pages. Treat "unique" as provisional (**Unverified** beyond these pages).
- The only measured review-comment resolution result found is Google's, which is self-reported and addresses a different step.
- No independent study found here shows that injected review lessons improve agent output. The one measured study of context files found here (arXiv:2602.11988v3, Preprint, authors' own evaluation) found no general gain in task success and over 20% higher inference cost on average. That supports precision-first, small slices, and means wiselotus needs its own evals (lesson precision, misled rate, tokens per slice) before claiming any benefit.
- Not covered: Cursor rules (fetch redirected), Meta and Microsoft internal review-ML papers (one search target did not match its page).

## Sources

- https://agents.md/
- https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- https://code.claude.com/docs/en/memory
- https://docs.coderabbit.ai/guides/learnings
- https://www.greptile.com/docs/introduction
- https://www.greptile.com/blog/model-inversion
- https://sourcegraph.com/docs/cody/core-concepts/context
- https://github.com/qodo-ai/pr-agent
- https://docs.qodo.ai/v1/features/best-practices
- https://modelcontextprotocol.io/introduction
- https://research.google/blog/resolving-code-review-comments-with-ml/
- https://arxiv.org/abs/2405.13565
- https://research.google/pubs/ai-assisted-assessment-of-coding-practices-in-industrial-code-review/
- https://arxiv.org/abs/2511.12884
- https://arxiv.org/abs/2602.11988 (arXiv:2602.11988v3)
- https://arxiv.org/abs/2310.08560
- https://github.com/letta-ai/letta
- https://arxiv.org/abs/2504.19413
- https://github.com/mem0ai/mem0
- https://arxiv.org/abs/2303.11366
- https://arxiv.org/abs/2305.16291
- https://arxiv.org/abs/2005.11401
- https://arxiv.org/abs/2310.06770
- https://arxiv.org/abs/2203.09095
- https://arxiv.org/abs/2305.18323
