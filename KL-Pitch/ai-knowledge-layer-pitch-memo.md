# Memo: The AI Knowledge Layer, Firm Context as a Service

**To:** Engineering Leadership, AI Knowledge Layer Working Group Kickoff
**From:** Enterprise Architecture, Developer Knowledge Layer Initiative
**Date:** 19 August 2026
**Re:** Standing up the knowledge layer as a permanent firm platform
**Classification:** Internal

---

## Executive summary

Models are becoming a commodity. Firm knowledge is not. Every agent at GS (Claude Code, Copilot, the GS AI Assistant, a growing fleet of desk-built agents) is only as good as the firm knowledge it reaches at the moment it acts: who owns a service, why a system was built the way it was, what a control requires, what broke last time. Without that, agents are fluent but ignorant, producing technically correct output that duplicates an existing service, crosses an ownership boundary, or violates a control nobody told the model about.

Today each agent wires into firm knowledge on its own: a vendored snapshot here, a Confluence scrape there, a hand-maintained prompt elsewhere. This memo proposes we treat the knowledge layer as a permanent internal platform, not a project: owned by a standing team, governed like a control rather than a wiki, and consumed through a protocol-neutral interface so we are never one procurement decision away from a rebuild.

## The cost of the status quo

Four costs compound as agent count grows across 12,000 engineers:

- **Inconsistent answers.** Same question, different tool, different answer, with no way to say which is authoritative.
- **N x M integration spend.** Every new agent re-pays for authoring, indexing, freshness, and entitlements another team already funded.
- **Ungoverned reach.** Where retrieval is bespoke, so are access control, provenance, and audit. Each bespoke path is a new conversation with Tech Risk.
- **Silent staleness.** Copies drift from the owner's source of truth until an agent is confidently wrong. Stale knowledge is worse than no knowledge.

We do not have a knowledge shortage. We have no shared way to serve knowledge to machines. Closing that gap is the mandate of this group.

## Operating principles

Five principles have to hold at our scale in a regulated bank:

1. **Protocol over product.** Build to an open interface (MCP), never to one vendor's agent. The tooling market will keep moving under us; adapters change, the gateway does not.
2. **Federated content, central spine.** Sources stay where owners maintain them. No migration, no change of ownership, no new silo. A thin platform team owns the pipes; domains own truth, because only they know if it is still true.
3. **Tools, not text dumps.** Agents call named, scoped operations (service ownership, code search, related incidents, data classification) rather than receiving forty raw chunks. Named tools are auditable, cheaper, and entitlement-checkable at the field level.
4. **Govern it like a control.** Classification, entitlements, audit trail, and model-risk coverage from day one. Every AI suggestion must be explainable after the fact.
5. **Prove, then scale.** No big-bang mandate. Two divisions and one or two knowledge domains earn the firmwide expectation.

## How it works

**Sources stay put.** Security standards and Tech Risk controls, ADRs and design decisions, runbooks and postmortems, service catalog and dependency graphs, code and API contracts, data schemas with classification tags, domain glossaries; the Confluence and Jira estate, consumed through Atlassian's governed MCP connector at a lower trust tier rather than scraped; and a fast-growing agent-native class the firm does not yet govern at all: repo-level AGENTS.md and CLAUDE.md instruction files, SKILL.md packages, and soon agent-authored decision records. Their shared limitation today: written for one reader (human or one specific agent), mixed-trust, uncited, unshaped, and invisible to every other consumer.

**Context factories make knowledge agent-ready.** A factory is a pipeline, not another database. On every source change it extracts into one docs-as-code contract, shapes content for tasks, enriches it with the metadata governance depends on (owner, classification, entitlement scope, trust tier, timestamp), certifies against the firm standard with fail-closed scans, and indexes into a semantic catalog. Factories emit the open Agent Skills format (SKILL.md), now adopted across every major agent vendor, so one certified artifact serves any agent the firm licenses. Factories are run by the teams that own the source: the firm designs the assembly line once, hundreds of teams supply the goods.

**One gateway is the front door.** A single MCP/A2A endpoint answers "what do I need to know for this task," not "which of forty systems has it." One integration contract; default-deny entitlements enforced on behalf of the developer's existing SSO identity, so an agent is never a privilege-escalation path; mandatory citations and timestamps; semantic routing; one telemetry stream feeding gaps back to owners. Discovery is governed too: an internal MCP registry, conformant to the open registry standard, is the allowlist of approved servers agents may reach, and the knowledge gateway complements (and is built to fold into) the firm's LLM gateway and eventual MCP gateway rather than adding a parallel bespoke path. One rule across every channel: no agent vendors its own copy.

## Who benefits

| Customer | What they get |
|---|---|
| Developers in AI tools | GS-correct, cited answers, not generic-internet plausible |
| Agent builders | One endpoint instead of N; ship features, not connectors |
| Platform and domain teams | Reach; their standards applied at the point of work |
| GS AI Assistant, non-engineering surfaces | The same governed corpus, no separate build |
| Tech Risk and governance | One enforcement point for entitlement, provenance, audit |

## Governance and organization

Nothing new is invented. The 13 AI Controls apply at the gateway: default-deny access (AI-1), lower-trust tiering for broadly editable sources (AI-4), on-behalf-of identity with dual audit (AI-7), mandatory citations (AI-12), with Tech Risk Design Review and AIRCC/AISG as the production gate. Classification (Public through MNPI) happens at ingestion, MNPI respects existing information barriers, and the gateway's retrieval logic folds into the firm's existing Model Risk Management framework rather than sitting outside it.

The org model is designed for a firm that reorganizes constantly. Stewardship attaches to the service or dataset in the metadata catalog, not to a team name: when a reorg moves a service, one field updates. Stewardship extends existing service-ownership responsibility on the same engineering-excellence scorecard as on-call. A small permanent platform squad (5 to 8 engineers) owns the gateway, pipelines, and certification. A monthly governance council of division engineering leadership plus compliance, model risk, and security adjudicates what stewards cannot. One honest gap: no firm standard yet exists for a federated knowledge layer; this group should commission one.

## The path

Adoption at 12,000 developers is earned team by team, not mandated. Phase 0 charters the initiative and baselines metrics. Phase 1 pilots one or two domains with 200 to 500 developers in two divisions and brings measurable lift to the council for go/no-go. Expansion follows results, with freshness SLAs, steward coverage above 90 percent in core domains, fully logged retrievals, and cost per active developer tracked each phase. Near-term working-group deliverables: a ratified MCP contract and metadata schema, a reference context factory any team can copy, a named front door with SLOs, and the commissioned Knowledge-Layer standard.

## Build, buy, or assemble

This is a layer-by-layer assembly decision, not a platform bet. Buy the commodity layers: frontier models (already firm practice), managed retrieval primitives from the hyperscalers, governed source connectors such as Atlassian's MCP server, and MCP gateway infrastructure, a space Gartner expects 75 percent of API gateway vendors to enter by end-2026. Build the governed spine no vendor can carry for a bank: the contract and metadata schema, owner-run factories, entitlement and MNPI integration, and certification. Workforce platforms like Glean (700-plus enterprise customers, financial services among its strongest verticals) are worth evaluating for non-engineering search, but Morgan Stanley, JPMorgan, and this firm all built the workforce-facing capability in-house on bought model APIs, because the regulated parts are exactly what a horizontal product cannot own. Because the spine speaks MCP and emits open skills, the decision stays reversible: components swap without re-platforming.

## Decisions requested

1. **Endorse federation-first.** Unify what we own; do not fund a new knowledge silo.
2. **Mandate the contract.** MCP plus docs-as-code, firm-wide, to publish and consume knowledge.
3. **Name owners.** A factory owner per priority domain; stewards attached to entities, not org charts.
4. **Fund the platform squad.** Control plane, connectors, certification. Domains contribute within existing workflows; no net-new headcount.
5. **Rule out fragmentation.** New agent products consume the gateway; no vendored catalogs.

Net effect: every GS agent, in any tool, acting on the same trusted, cited, current context, authored once by the team that owns it, on an interface that outlives any single vendor.
