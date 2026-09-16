**Knowledge Layer as a Service for Engineering Agents**

**Where we are**

Engineering runs coding agents in production today. Devin and Claude are the primary harnesses. GitHub Copilot is deprecated and being wound down. Codex is under consideration. Each harness has its own way of loading context, its own configuration format, and its own defaults for when it goes looking for information. None of them know what Goldman Sachs knows unless someone tells them, per repository, per team, per harness.

The firm has built real infrastructure around this. Engineering documentation is served over MCP. Certified skills are served over the same channel. An MCP registry with entitlements governs who can call what. Atlassian integration is coming. GSCode gives agents a code graph of our GitLab estate. These are the right pieces. What is missing is the thing that connects a developer's task to the right subset of those pieces at the right moment, without the developer having to know the map.

This proposal is for that missing piece: a Knowledge Layer delivered as a service to agents, not as a document set for humans.

**The problems, as developers experience them**

1. The agent does not know firm conventions. It writes code that compiles and passes tests and is rejected in review because it used a banned dependency, an outdated API pattern, or the wrong logging convention. The rule existed. The agent never saw it.

2. The agent does not know where to look. Documentation, Jira, Confluence, code, and skills are all reachable, but the agent has to be told which to consult for which question. Left alone, it either searches nothing or searches everything.

3. The agent is told too much. A developer adds a large instruction file to compensate for problem 1. The agent now spends a meaningful share of its context window on rules irrelevant to the task, follows some of them too literally, and gets slower and more expensive without getting more correct.

4. Every team solves this separately. Team A maintains a Devin knowledge base entry. Team B maintains a CLAUDE.md. Team C wrote a script that dumps Confluence into a prompt. When Copilot was deprecated, everything configured for it was lost or rewritten. The next harness change will do the same.

5. Nothing is measured. We do not know, per product or per team, how often agent output is rejected for a firm-knowledge reason versus a logic reason. Without that split we cannot say whether any of the above is improving.

6. Freshness is manual. Whatever context a team has assembled goes stale on the product's next release. There is no signal that tells the agent, or the developer, that the guidance it is following is out of date.

**The cost, made explicit**

The cost of these problems is paid in four currencies and should be tracked in all four.

- Senior review time. Rejections for firm-knowledge reasons land on the engineers who know the conventions. This is the most expensive labor in the organisation, spent catching errors an agent could have avoided.
- Rework cycles. Each rejected agent change is a second agent run, a second review, and a delay to whatever the developer was actually trying to ship.
- Token and compute spend. Oversized context is paid for on every call. A team that loads a large instruction file into every agent session pays a tax on every request, and the tax grows with the number of agents and the number of sessions.
- Duplicate build effort. Every per-team integration is engineering time spent on a problem the firm has already solved elsewhere, and it is rebuilt each time a harness is added or retired.

None of these are estimates I can put a number on today. That is itself the finding. The first deliverable of this work is a baseline for each.

**A data-backed way to decide what to build**

Prior efforts in this space stalled on scope. Too many products, too many sources, too many harnesses, and no rule for choosing. The decision framework below is designed so that every choice is made from data the firm already collects.

Which products first. Rank Engineering products by the product of three signals: documentation page views, agent sessions that touch the product's repositories, and review rejections attributed to that product's conventions. The top of that list is where the knowledge gap costs the most. Start with ten to twenty products and expand only when the metrics on the first set have moved.

Which sources per product. For each product, classify available knowledge by how definitive it is. Certified documentation and certified skills are authoritative and loaded by default. Code and ADRs are authoritative but expensive and loaded on demand. Jira and Confluence are contextual and loaded only when the task type calls for them. Chat and forum content is not loaded at all in the first phase.

How much context per task. Define a context budget per SDLC phase: spec, generate, review, test, release. Code generation gets the largest budget because it is where the most value is created and the most errors are introduced. Review gets a narrower budget scoped to the rules being checked. Budgets are enforced in the harness configuration, not left to the prompt.

Which harnesses. Devin and Claude are the supported set for the first phase. Codex is added if and when it is adopted. Copilot is not migrated; its configurations are used as input to the first knowledge packs and then retired. The rule going forward is that harness-specific configuration is generated from a single source and never hand-maintained.

When to stop. Each product's knowledge pack is judged on two numbers: the change in review rejections for firm-knowledge reasons, and the change in tokens consumed per agent session. If neither moves within a defined window, the pack is redesigned before more products are added.

**The solution: Knowledge Layer as a service**

The Knowledge Layer is an MCP-served service that an agent calls with a task description and receives back a small, structured context bundle: what this product is, what rules apply to this task type, which authoritative sources to open if it needs more, and how to cite them. It does not return documents. It returns pointers, constraints, and a budget.

What it is built on. The existing documentation MCP, the certified skills framework, the MCP registry for discovery and entitlement, the Atlassian integration, and GSCode's code graph. The service composes these; it does not replace any of them.

What it adds.

- A routing standard. For each task type, which sources are consulted by default and in what order. Configured centrally, applied per harness automatically.
- Knowledge packs. One per product, versioned, owned, pointer-first. Each pack carries a verified-at date tied to the product's release process and is demoted automatically when it lapses.
- Budgets and guardrails. Hard limits on what an agent fetches by default, with an audited override path when a developer needs more.
- Telemetry. Every bundle served and every source opened is logged against the task, so the firm can see which knowledge is used, which is ignored, and which correlates with rejected output.
- Harness adapters. Generated configuration for Devin and Claude today, Codex when needed, produced from the same pack. Adding a harness is an adapter, not a migration.

**What the ideal outcome looks like**

A developer on a supported product opens a task in any supported harness. The agent, before writing code, receives the product's constraints, the relevant certified skill, and pointers to the two or three sources that matter for this task type. It writes code that passes review for the right reasons. If it needs the full ADR or the exact API surface, it fetches that one thing, and the fetch is logged.

The product owner sees a dashboard: how many agent sessions touched their product this month, which knowledge was used, which rejections still occur and why. They update the pack the way they would update a README, and the change reaches every harness the next session.

Engineering leadership sees four numbers per quarter: senior review hours spent on firm-knowledge rejections, rework cycles per agent change, tokens per session, and count of per-team integrations retired. All four go down.

When the next harness arrives, it is onboarded by writing an adapter, not by asking every team to reconfigure.

**What is being asked**

1. Sponsor the Knowledge Layer as an Engineering platform service with a single accountable owner.
2. Approve the decision framework above as the basis for product and source selection, so that scope is set by data rather than by committee.
3. Fund a baseline measurement effort in the first month: review rejection reasons, tokens per session, and an inventory of existing per-team integrations.
4. Confirm Devin and Claude as the supported harness set for the first phase, with Copilot configurations treated as migration input only.
5. Commit the pilot products' owners to maintaining their knowledge packs as part of their release process.

**What happens if we do not do this**

The per-team integrations continue to multiply. Each new harness triggers another round of rewrites. Context files grow, cost grows, and the errors they were meant to prevent persist because the right rule is buried in the wrong file. The firm's investment in MCP infrastructure, certified skills, and the code graph delivers less than it should, because the agents that could use it are never pointed at it.
