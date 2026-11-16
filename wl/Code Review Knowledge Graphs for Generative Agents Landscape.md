# Code Review Knowledge Graphs for Generative Agents: Landscape

Nov 15, 2026 · @Deepak Kumar

## Bottom line

Every serious AI code review vendor now runs the same play: **turn the codebase and its review history into a graph, then serve slices of it to agents through MCP.** They do this because AI made writing code cheap, while checking it stayed slow and depends on context. Research backs graphs for multi-hop questions, but also warns that agents often ignore the graph and that sending more context can make the output worse.

**Key terms**

- **Code graph:** symbols, files and how they depend on each other (calls, imports, inheritance).
- **Knowledge / context graph:** a code graph plus SDLC artifacts (PRs, review comments, tickets, decisions) linked to the code they touched.
- **Learnings / mined rules:** natural-language standards pulled out of past review threads and applied to future changes.

## The problem they solve

Review, not generation, is now the bottleneck, and reviewers and agents both lack the context that sits in past PRs.

1. **Review is the new bottleneck.** LinearB's 2026 benchmarks (8.1M PRs, 4,800 teams): AI users merge 98% more PRs while review time rose 91%. AI-generated PRs wait 4.6x longer for review and are accepted 32.7% of the time, versus 84.4% for manual code.
2. **Agents are blind to context.** Harness argues the bottleneck is not the model but the lack of a pre-computed, always-available representation of the codebase. CodeRabbit names the cause: AI writes code without your business logic, conventions or past decisions.
3. **Tribal knowledge lives in review threads.** Review also transfers knowledge and team awareness. Qodo calls PR history (recurring comments, accepted and rejected suggestions, approval patterns) the richest signal of how a team really reviews.
4. **Agents waste tokens searching.** Code Review Graph's value is exclusion: of 27,732 files, it tells the model to read 15.

## Industry landscape

The tools fall into three archetypes: review bots with learned memory, org-wide context engines, and platform-native lifecycle graphs.

| Tool | Archetype | What the graph holds | How it learns | Notable detail |
| --- | --- | --- | --- | --- |
| [CodeRabbit](https://docs.coderabbit.ai/knowledge-base/learnings) | Review bot | Symbol definitions and references; files that change together | Learnings from reviewer chat corrections | Inferred learnings stay off other PRs until the source PR merges |
| [Greptile](https://www.greptile.com/docs/how-greptile-works/memory-and-learning.md) | Review bot | Functions, classes, variables, dependencies, calls | Comments, reactions, which suggestions get implemented | Compares first and last commits to see which comments were addressed |
| [Qodo](https://www.qodo.ai/blog/introducing-qodo-2-4-the-next-layer-of-code-quality-governance/) | Review bot | Repo structure, PR history, cross-repo links | Rules Miner turns recurring PR comments into rules | Rules are scoped by path and decay when unused |
| [Bito AI Architect](https://bito.ai/blog/code-graphs-explained-for-ai-coding-tools-2026-guide/) | Context engine | Code plus Jira, Linear, Confluence, Slack | Graph updates as code and tickets change | Served over MCP to Cursor, Claude Code, Codex |
| [Unblocked](https://blog.getunblocked.com/blog/building-ai-code-review-with-context-as-a-first-class-system) | Context engine | Slack, docs, PR history, code | Extracts standards from the knowledge graph | Resolves source conflicts by recency and authority |
| [GitLab Orbit](https://docs.gitlab.com/orbit/) | Platform graph | Code, work items, MRs, pipelines, deployments, vulnerabilities | Indexes pushes, merges, deployments | Public beta; claims 11x faster, 4.5x fewer tokens; MCP tools query\_graph and get\_graph\_schema |

## Academic research

Three research threads feed this space, and three industrial papers show what works at scale.

**1. Retrieving past reviews to generate new ones** (oldest thread)

- Early review automation was retrieval-based. A survey roadmap notes simple Bag-of-Words retrieval beat complex deep learning models ([Yang et al.](https://arxiv.org/pdf/2405.18216)).
- [LAURA (2025)](https://arxiv.org/html/2512.01356v1) combines review exemplar retrieval, context augmentation and guidance to improve GPT-4o and DeepSeek v3 review comments.

**2. Repository knowledge graphs for agents**

- [CodexGraph (NAACL 2025)](https://arxiv.org/abs/2408.03910): similarity retrieval has low recall on complex tasks, so agents query a graph database instead.
- [KGCompass](https://arxiv.org/html/2503.21710v3), the closest analogue to wiselotus: links issues and PRs to files, functions and classes. With Claude-4 Sonnet it reached 58.3% repair accuracy, a 50.8% relative gain over plain LLM. 89.7% of localized bugs lacked location hints and were found only by multi-hop traversal.

**3. Temporal agent memory**

- [Zep / Graphiti](https://arxiv.org/html/2501.13956) records both when a fact was true and when the agent learned it, enabling edge invalidation and provenance. This matters because conventions change.

**Industrial papers**

| System | Company | Result |
| --- | --- | --- |
| [BitsAI-CR](https://arxiv.org/html/2501.15134v1) (FSE 2025) | ByteDance | 75.0% precision; prunes rules using Outdated Rate (did code change after the comment) |
| [ML-suggested edits](https://research.google/pubs/resolving-code-review-comments-with-machine-learning/) (ICSE 2024) | Google | 7.5% of all reviewer comments resolved by an applied ML edit |
| [MetaMateCR](https://arxiv.org/pdf/2507.13499) | Meta | 21.2% acceptance with GPT-4o; 27.5 to 28.7% with fine-tuned models |

## Benefits

The best-evidenced benefit is multi-hop reasoning. Vendor numbers on speed and adoption are promising but unverified.

| Benefit | Evidence | Source type |
| --- | --- | --- |
| Better multi-hop reasoning | KGCompass: +50.8% relative repair accuracy on Claude-4 Sonnet | Peer-reviewed |
| Fewer tokens, faster answers | Orbit: 11x faster, up to 4.5x fewer tokens | Vendor claim |
| More useful comments | [Greptile v4](https://vantaige.io/ai-tool/greptile): share of comments acted on rose from 30% to 43% | Vendor metric |
| Standards enforced from day one | Qodo: mined rules apply from a new engineer's first PR | Vendor claim |
| Auditability | Graphs give reasoning chains traceable to the source PR or comment | KGCompass, Zep |

## Warnings from the research

A graph only helps if the agent actually uses it, and a small, well-chosen slice beats a large one.

- **Agents skip the graph.** In [CodeCompass](https://arxiv.org/pdf/2602.20048), only 42% of trials called the graph tool even when told to. Called: 99.5% coverage. Skipped: 80.2%, close to no tool. The authors suggest enforcing tool calls structurally, not through prompts. (One codebase, one model.)
- **More retrieval can hurt.** In [RARe](https://arxiv.org/html/2511.05302v2), top-1 retrieved review beat top-3 and top-5. Extra examples add mismatched critique directions.
- **History bakes in bad habits.** If a team always waved through a risky pattern, history alone will not flag it ([Qodo](https://www.qodo.ai/?p=22534)).
- **Context drift is a running cost.** Someone has to keep the graph current and update instructions as conventions change ([CodeRabbit](https://www.coderabbit.ai/guides/agentic-context-engineering)).

## Implications for wiselotus

The accepted design already matches what the research supports. The opening is in serving review knowledge at generation time, with time-aware facts, across vendors.

**Already aligned**

- 2k-token capped context pack matches the top-1-beats-top-5 finding.
- helped / misled outcome feedback matches BitsAI-CR's Outdated Rate and Greptile's commit diffing.
- Eviction by staleness matches Qodo's rule decay.

**Gaps worth owning**

1. **Generation time, not review time.** Most vendors feed review memory to their own reviewer. Few push it to the coding agent before code is written.
2. **Bi-temporal validity for conventions.** No code review tool applies Graphiti-style "true from / superseded at" to review learnings.
3. **Push, not pull.** Given 42% tool adoption, deliver the briefing through a hook instead of waiting for a tool call.
4. **Vendor neutrality.** Every tool above keeps its memory inside its own product.

## Sources

- [KGCompass (arXiv 2503.21710)](https://arxiv.org/html/2503.21710v3)
- [CodeCompass: Navigation Paradox (arXiv 2602.20048)](https://arxiv.org/pdf/2602.20048)
- [When More Retrieval Hurts (arXiv 2511.05302)](https://arxiv.org/html/2511.05302v2)
- [BitsAI-CR (arXiv 2501.15134)](https://arxiv.org/html/2501.15134v1)
- [Zep temporal knowledge graph (arXiv 2501.13956)](https://arxiv.org/html/2501.13956)
- [CodexGraph (arXiv 2408.03910)](https://arxiv.org/abs/2408.03910)
- [LAURA (arXiv 2512.01356)](https://arxiv.org/html/2512.01356v1)
- [Google: Resolving code review comments with ML](https://research.google/pubs/resolving-code-review-comments-with-machine-learning/)
- [Meta: AI-assisted fixes to code review comments (arXiv 2507.13499)](https://arxiv.org/pdf/2507.13499)
- [Qodo 2.4: Rules Miner](https://www.qodo.ai/blog/introducing-qodo-2-4-the-next-layer-of-code-quality-governance/)
- [Greptile memory and learning](https://www.greptile.com/docs/how-greptile-works/memory-and-learning.md)
- [CodeRabbit learnings](https://docs.coderabbit.ai/knowledge-base/learnings)
- [GitLab Orbit docs](https://docs.gitlab.com/orbit/)
- [LinearB 2026 benchmarks summary](https://dev.to/code-board/the-pr-review-bottleneck-why-faster-code-generation-slows-teams-down-1peb)
