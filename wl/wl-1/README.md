# Research index: wiselotus

Research date: 2026-11-14. Each note is a Markdown source of truth with an HTML twin. Facts carry sources, recommendations are labelled, and unconfirmed items are marked **Unverified**.

## Notes

### [Personas and the problem](personas-and-problem.md)

Five personas (developer, reviewer, platform team, engineering leader, security owner) and three linked problems. **Key finding:** review knowledge stays in threads and static instruction files drift, but no fetched source quantifies repeated review comments, so that is **Unverified**.

### [Landscape and patterns](landscape-and-patterns.md)

Industry products, case studies, open-source and academic work, with a pattern table. **Key finding:** hand-written files and feedback-learned preferences exist, but a traceable, outcome-weighted lesson graph under a small budget is not described on the fetched pages, and no independent study shows injected review lessons improve agent output.

### [Business value, alternatives and ROI](business-value-and-roi.md)

Benefit per persona, alternatives for putting knowledge into context, published productivity evidence and a justification framework. **Key finding:** productivity evidence is mixed and none measures review-lesson serving, so justify by a pilot that reports built-in outcome metrics, not borrowed percentages.

### [The simplest elegant solution](simplest-solution.md)

Synthesis of the three notes. **Key finding (recommendation):** a deterministic versioned JSON lesson store, scope matching and ranking in code, a small capped slice served identically over MCP and CLI, and outcome feedback adjusting confidence, with one model call site (extraction). Lists adopted and rejected patterns and what to build first.

## Key sources across the notes

- https://arxiv.org/abs/2307.03172 (Lost in the Middle)
- https://research.trychroma.com/context-rot
- https://arxiv.org/abs/2602.11988 (repository context files; cite v3, revised 2026-09-29)
- https://arxiv.org/abs/2511.12884 (agent context files study)
- https://code.claude.com/docs/en/memory
- https://docs.coderabbit.ai/guides/learnings
- https://www.greptile.com/docs/how-greptile-works/memory-and-learning
- https://modelcontextprotocol.io/introduction
- https://research.google/blog/resolving-code-review-comments-with-ml/
- https://arxiv.org/abs/2302.06590
- https://arxiv.org/abs/2507.09089
- https://agents.md/

## Sources

The URLs above are reused from the four notes. Full source lists are in each note's own `## Sources` section.

- https://research.google/pubs/modern-code-review-a-case-study-at-google/
- https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/
- https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report
