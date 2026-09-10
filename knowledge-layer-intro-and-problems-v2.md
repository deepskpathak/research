# Proposal: Engineering Knowledge Layer

## Introduction

A developer at the firm can hand a task to Claude Code or Devin and get compiling, tested code back in minutes. What that code knows about the firm is a separate question. Which internal library to call, which dependencies are approved, which logging convention applies, which API was deprecated last quarter: each harness learns these things through its own mechanism, and each developer fills the gaps by hand.

Foundation Engineering supports several harnesses today. Claude Code and Devin are in production use, Codex is under evaluation, and GitHub Copilot is being retired, with its configurations treated as migration input only. Each harness has its own context-loading mechanism, configuration format, and default behaviors. The firm has real assets that serve these agents. What it does not have is a single path that delivers the right knowledge to the right agent at the right point in a task, scoped to what the requesting developer is entitled to see.

### Customer

The customer is the developer who delegates a firm task to a coding agent. Every problem in this document is felt first by that developer: rejected output, the skill they did not install, the instruction file they maintain by hand. The Knowledge Layer succeeds or fails on whether the developer's agent gets the right firm context without the developer supplying it.

Four other groups are served through the same service and are not its primary customer:

| Group | What they need from the layer |
|---|---|
| Knowledge owners (platform teams, EngHub, architecture, security) | Publish once, reach every harness, see evidence of consumption |
| Harness and tooling owners | One integration target instead of one per source |
| Engineering leadership | Measurement of which knowledge agents use, where output fails, and what it costs |
| Tech Risk and control functions | Entitlement-scoped retrieval, provenance, and an audit trail per agent request |

The agent is the delivery channel, not the customer.

### Terms used in this document

**Harness.** The coding agent product a developer runs: Claude Code, Devin, Codex.

**Knowledge.** Firm-specific information that changes what correct output looks like for a task, and that an agent cannot derive from the repository in front of it or from its training. Knowledge has an owner, a scope of applicability, and a validity period. Content that lacks those three attributes is a source, not knowledge. It falls into five kinds:

1. **Constraints.** What the agent must not do. Banned dependencies, security rules, information barriers, MNPI handling. Low volume, high cost when missed.
2. **Conventions.** How the firm does things when several ways would work. Approved libraries, logging, naming, error handling. Highest volume; most review rejections are here.
3. **Estate facts.** What exists and how it connects. Service owners, API contracts, deprecation state, the code graph. Changes fastest, most likely to be stale.
4. **Decisions.** Why something is the way it is. ADRs, design rationale, ticket context. Lets the agent choose correctly where no rule applies.
5. **Procedures.** How to complete a multi-step firm process. Release steps, certification workflows, skills. Executable rather than descriptive.

Out of scope as knowledge: general programming ability (the model has it), content in the repository being worked on (the harness has it), raw business data (governed as data access), and chat or channel history until a constraint, convention, fact, decision, or procedure has been extracted from it.

**Knowledge source.** Anything knowledge is extracted from or served by: documentation, skills, code graphs, tickets, wiki pages, chat threads, document shares.

**Certified.** EngHub's term for content an owning team has published through EngHub's review process. Certified content carries a named owner and a version. Certification says the owner reviewed it at publication. It does not say the content is current, or that it applies to the task at hand. What certification means also varies by kind: a certified constraint is a control; a certified convention is a preference the owner will defend in review. In this document, everything outside that process (local skills, pasted pages, team scrapers, Devin knowledge base entries) is referred to as uncertified.

### What coding agents can reach today

This section is limited to sources at least one coding agent can read today.

1. **EngHub over MCP.** Engineering documentation and certified skills, reachable from Claude Code.
2. **Local skills.** Team-authored SKILL.md files loaded per repository or per developer, on any harness that supports the format.
3. **Devin knowledge bases and wiki.** Devin only, populated and maintained per team.
4. **GSCode.** A code graph of the GitLab estate built from the current repository. It runs in local memory and is not served as a service.
5. **Jira and Confluence.** Reachable today only through team-built skills that call the APIs over S2SProxy. Native MCP servers are in progress and not yet available to agents.

| Harness | What it reaches today |
|---|---|
| Claude Code | EngHub over MCP, certified and local skills, GitLab, Jira and Confluence through team skills over S2SProxy |
| Devin | Knowledge bases, local skills, Ask Devin, wiki with code graph |
| Codex | None yet (under evaluation) |
| Copilot (retiring) | Local skills, GitLab, Jira and Confluence through team skills over S2SProxy |

Developers also draw on sources no agent reaches in a governed way today: team document shares, Teams channels, Stack Overflow Enterprise, and per-team skills registries. The working group will maintain an inventory of these sources as the candidate set for a single gateway. That inventory is a workstream of this proposal, not a claim about current reach.

These are the right pieces. What is missing is a service that sits over them and answers one question on the developer's behalf: for this task, on this harness, with this developer's entitlements, what does the agent need to know right now?

## Problems

The agents are not uninformed. Claude Code reaches EngHub over MCP, Devin has its knowledge bases, and both can load certified and local skills. The gap is that what an agent knows on any given task depends on which harness the developer selected, which skills they happened to install, and what they pasted into the session.

Over the past year, teams have closed that gap themselves. They have written their own skills, scrapers, knowledge bases, and code graphs. Each works for the team that built it. Together they form a bespoke body of content that the firm does not govern, cannot measure, and cannot reuse, and that ages independently of the sources it was copied from. The six problems below describe how this shows up for the developer, which kind of knowledge fails in each case, and what each one costs.

| Problem | Knowledge kind that fails |
|---|---|
| 1. Uneven delivery | Constraints, conventions |
| 2. Reachability and discovery | Procedures, estate facts |
| 3. Front-loaded context | Conventions (over-supplied) |
| 4. Bespoke supply chains | All kinds, ungoverned |
| 5. No telemetry | All kinds, unmeasured |
| 6. Unknown validity | Estate facts, decisions |

Constraints and conventions dominate the review cost. Estate facts and decisions dominate the staleness cost. Procedures dominate the integration cost. This split is what the scope decision later in the proposal is based on.

### 1. Firm conventions reach agents unevenly, and the gaps surface in review.

A developer asks an agent to add a retry wrapper around an internal service call. In Devin, a knowledge base entry may steer it to the firm's approved library. In Claude Code, the answer is available if the developer installed the right skill or the EngHub page is indexed. On a harness with nothing beyond the repository, the agent guesses. The output compiles and passes tests in every case. Whether it also pulls in a banned dependency, a deprecated API pattern, or the wrong logging convention is decided by harness of choice, not by the rule. The rule existed. The agent may or may not have seen it.

**Cost.** Senior review time. Rejections for firm-knowledge reasons land on the engineers who know the conventions, the most expensive labor in the organization, spent catching errors an agent could have avoided. Each rejection is a second agent run, a second review, and a delay to whatever the developer was trying to ship.

### 2. Reachability depends on the harness, and reachable sources still have to be found.

MCP itself is harness-agnostic. The work of connecting each harness to it (configuration, authentication, session behavior) sits with each tooling owner, so it is repeated per harness and drifts per harness. On the source side, EngHub exposes skills over MCP but does not publish a catalog or front-matter index, so an agent that needs a skill makes several calls to discover it before it can use it. Jira and Confluence are reached only through team-built skills over S2SProxy, and those skills are being wired into team-specific SDLC processes. Each new harness and each new source multiplies this integration work, with no standard way for an agent to discover what knowledge exists or how to reach it.

**Cost.** Duplicate integration effort, rebuilt on every harness change, plus token spend on discovery calls that a catalog would make unnecessary. Every per-team connection is engineering time spent on a problem the firm has already solved elsewhere, and it is thrown away when harness capabilities catch up.

### 3. The workaround for problems 1 and 2 is to front-load everything, which bloats the context window.

When a developer cannot rely on the agent finding firm knowledge, the safe move is to put all of it in the instruction file. CLAUDE.md, AGENTS.md, and copilot-instructions.md grow into standing documents that describe every convention the team has ever been burned by, loaded into every session regardless of the task. The agent reads all of it, uses a fraction of it, and the developer has no way to know which fraction.

**Cost.** Token and compute spend, paid on every call. A team that loads a large instruction file into every session pays a tax on every request. The tax scales with the number of agents, the number of sessions, and the size of the file, and none of those are trending down.

### 4. Every team runs its own knowledge supply chain.

Across teams, the same problem is being solved independently. Teams maintain their own skills registries, write scrapers against Jira and Confluence under system tokens, build their own code graphs, and inject context into sessions by hand. Each supply chain reflects one team's understanding at one point in time. None of them share provenance, access control, or a refresh mechanism.

**Cost.** Ungoverned reach. Where retrieval is bespoke, so are access control, provenance, and audit. A scraper under a system token does not carry the requesting developer's entitlements. A pasted page carries no record of where it came from or whether the developer was permitted to see it. Each bespoke path is a new conversation with Tech Risk, and the number of paths is growing.

### 5. There is no telemetry on what agents consume, so there is no path to improve it.

The firm does not know, per product or per team, how often agent output is rejected. There are no dashboards measuring agent output, rework, or token spend by failure reason. Nobody can say which knowledge sources agents consult, which rules in an instruction file are ever relevant, or what share of context tokens is spent on guidance the task never used.

The move from a human SDLC to an AI SDLC changes what DXR needs to measure. Today's telemetry tracks developer activity. It needs to also track what knowledge each agent request drew on, whether that knowledge was certified, current, and permitted, and what happened to the output. Knowledge consumption by agents is now a first-class signal for quality, compliance, and audit, and it is not being captured.

**Cost.** No basis for prioritization or improvement. Without the split between product outcomes and agent output, no team can say whether any of the above is getting better, and no investment in fixing it can be justified or ranked.

### 6. The validity of available knowledge is unknown, and staleness is only the most visible form.

Whatever context a team has assembled goes stale on the product's next release. A platform team deprecates an API and publishes the replacement; the instruction file in a hundred repositories still describes the old one. The agent follows it with full confidence, and the change passes tests against a compatibility shim that is itself scheduled for removal. No signal tells the agent or the developer that the guidance is out of date.

Staleness is one failure. The broader question is validity: is this content current, does it have an owner, does it apply to this task, and is this developer permitted to see it? EngHub answers part of that for certified sources through merge-request tracking and semantic search. Confluence pages, architecture decisions, agent instruction files, and code standards are updated with no event reaching the agents that depend on them. An agent's context is only as good as the validity of what went into it, and today nothing checks.

**Cost.** Invalid guidance is followed with the same confidence as valid guidance. The failure is silent until review, and by then it has been multiplied across every repository that copied the same file. Downstream it shows up as rework, rejections, token waste, and longer debugging during incidents.
