# Product Requirements Document: Repository AI-Readiness Service

**Working name:** RARM Service (Repository AI-Readiness Model service)
**Version:** 1.0 draft, September 2026
**Status:** For review
**Companion document:** *AI-Ready Repositories: Assessing AI maturity, effectiveness and readiness from the codebase up* (working paper v2.0, September 2026), referred to below as "the paper"
**Assumed environment:** a regulated financial institution with a GitHub- or GitLab-style forge, a central CI platform, one or more approved coding-agent harnesses (for example Claude Code, Codex, GitHub Copilot coding agent, Devin), an AI inventory owned by technology risk, and supervision under one or more of MAS, EU DORA, FFIEC/OCC, NYDFS and PCI DSS

---

## 1. Summary

The RARM Service computes, per code repository and per task class, whether a coding agent can be expected to work on that repository reliably and safely, assigns a readiness tier that doubles as an authorization level, tracks the estate's maturity as a repeatable process, and produces the evidence that auditors and supervisors expect for agent-authored changes.

It is a scoring and evidence product, not an enforcement product. Enforcement stays with the forge (rulesets, CODEOWNERS), the CI platform (required status checks) and the harness (hooks, sandboxes). The service tells those systems and their owners what the repository's state is, what tier it justifies, and what to fix first.

**Why now.** Coding agents are the most-scaled agent class in the enterprise, the evidence shows their success depends on repository properties rather than on the model (Section 3 of the paper), and US model risk guidance now explicitly excludes generative and agentic AI, which leaves the firm to evidence its own controls (Section 2.4 of the paper).

---

## 2. Problem statement

Engineering leadership at a regulated firm cannot answer, per repository, three questions: can an agent work here, what may it be allowed to do, and can we prove the controls held. Today the answers are anecdotal (a team "tried Claude Code on the payments repo"), the authorization is implicit (whoever has a licence uses it wherever they like), and the evidence is assembled by hand when an auditor asks.

The cost of not solving it is threefold. Agents are used on repositories that cannot be built or verified, producing confident, unverifiable output and review load rather than value (the paper's Sections 2.2 and 3.1: environment-setup success as low as 6.69% on hard repositories, 31% of "passing" benchmark patches passing only because of weak tests, review time up 91% in high-adoption teams). Agents are kept off repositories where they would work, because no one can show they are safe. And the first supervisory examination of agent-authored code finds controls that exist for human-authored code but were never evidenced for agents: independent approval, source-code testing, change records, provenance, identity.

**Who experiences it.** Platform engineering (owns the harnesses and cannot say where they are safe), repository owners (asked to "adopt AI" without a definition of ready), technology risk and internal audit (asked to sign off on a control environment they cannot see), and engineering leadership (asked for value numbers they cannot defend).

---

## 3. Goals

1. **Every repository has a readiness state.** 100% of repositories in the estate inventory carry a RARM score, a tier per task class, and a last-assessed date within 90 days of launch for the top-traffic repositories and within 365 days for the whole estate.
2. **Authorization follows evidence.** By day 180, at least 80% of agent-authored pull requests originate on repositories at tier T1 or above for the task class attempted, measured from harness and forge telemetry.
3. **Remediation is prioritized by the weakest dimension.** Each scored repository shows its minimum dimension and the single highest-leverage fix; 60% of remediation actions closed in the first two quarters address R1 (executability), R2 (verification) or R7 (guardrails), the dimensions the evidence ranks highest.
4. **Evidence on demand.** The audit evidence pack for any repository, or for the estate, is generated in under one working day, down from a multi-week manual exercise, and passes internal audit review without supplementary requests.
5. **Effectiveness is measured at the system level.** For repositories at T2 and above, the service reports delivery, quality, reliability and cost outcomes for agent-assisted changes alongside usage, so that no value claim rests on usage or self-report alone.

---

## 4. Non-goals

- **Enforcing gates.** The service will not block merges or agent actions in v1. Enforcement belongs to rulesets, status checks and harness hooks; the service publishes tier and indicator data those systems can consume. Rationale: keeps the blast radius small, avoids a second policy engine, and lets tiers be trusted before they are binding. (Planned for P2.)
- **Remediation agents.** The service will not run agents that fix setup, tests or documentation. Rationale: remediation should run under the same gates as any other agent work and belongs in the harness platform; the service supplies the backlog. (P2.)
- **Scoring non-code repositories** (documentation stores, wikis, data assets). Rationale: different indicators; separate initiative.
- **Individual developer productivity measurement.** The service reports repository and team outcomes, never per-person metrics, and will not feed performance reviews. Rationale: the paper's anti-pattern list; gaming risk; employment-law exposure.
- **Model or harness evaluation leaderboards.** The service consumes private eval results per task class; it does not rank vendors. Rationale: public benchmark comparisons are contaminated and infrastructure-sensitive.
- **Replacing DORA or developer-experience dashboards.** The service reads those metrics for T2+ repositories; it does not re-implement them.

---

## 5. Users and user stories

### 5.1 Personas

| Persona | Role in the product |
|---|---|
| **Platform engineering lead** | Product owner; operates the service; owns harness integrations |
| **Repository owner / tech lead** | Sees the score, the weakest dimension and the fix list; requests tier promotion |
| **Developer using an agent** | Sees the tier and permitted task classes before delegating |
| **Harness owner** | Consumes tier data to configure defaults; supplies telemetry |
| **Technology risk (second line)** | Reviews tier assignments and evidence; validates scoring |
| **Internal audit (third line)** | Pulls evidence packs; tests the control design |
| **Engineering leadership** | Sees estate maturity, tier distribution and outcome metrics |

### 5.2 User stories (ordered by priority)

**Repository owner**

- As a repository owner, I want to see my repository's RARM score by dimension and the minimum dimension, so that I know what is blocking agent use.
- As a repository owner, I want a ranked list of fixes with the expected tier change for each, so that I spend effort where it moves the tier.
- As a repository owner, I want to request tier promotion for a task class and see exactly which evidence is missing, so that promotions are predictable.
- As a repository owner, I want to be notified when a score drops (a new flaky test, a ruleset weakened, a context file grown past threshold), so that regressions are caught before an agent acts on them.

**Developer using an agent**

- As a developer, I want to see the repository's tier and permitted task classes in the harness before I delegate, so that I do not attempt work the repository cannot verify.
- As a developer, I want to know why a task class is not permitted, so that I can fix it or choose a different approach.

**Platform engineering lead**

- As a platform lead, I want indicators computed automatically from the forge, CI, code-analysis and harness telemetry, so that scores stay current without manual questionnaires.
- As a platform lead, I want to define task classes and the pass^k threshold per class, so that tiering reflects the firm's risk appetite.
- As a platform lead, I want to publish tier data through an API, so that harnesses and rulesets can consume it later.

**Technology risk**

- As a second-line reviewer, I want to see the evidence behind every score above 2 and to record my validation, so that tiers are defensible.
- As a second-line reviewer, I want the repository's sensitivity tier and RARM tier side by side, so that materiality decisions use both.

**Internal audit**

- As an auditor, I want to generate the evidence pack for a repository or the estate as of a date, so that I can test controls over agent-authored changes without asking the team for screenshots.
- As an auditor, I want to trace any agent-authored change to its task, agent identity, model, harness version, verification results and approver, so that I can test segregation of duties and change records.

**Engineering leadership**

- As an engineering leader, I want the tier distribution across the estate and the estate maturity level, so that I can report readiness truthfully.
- As an engineering leader, I want outcome metrics for agent-assisted changes on T2+ repositories next to usage, so that no value claim rests on usage alone.

**Edge cases**

- As a repository owner of a monorepo, I want scoring per service or directory, so that one unready service does not block the rest.
- As a platform lead, I want repositories with missing telemetry to show "not assessable" rather than a low score, so that gaps in instrumentation are not read as poor engineering.
- As a harness owner operating under zero-data-retention, I want the service to work from aggregate telemetry only, so that no prompt or code content leaves the harness boundary.

---

## 6. Solution overview

The service has five parts.

1. **Collectors** pull data from the forge (rulesets, CODEOWNERS, PR metadata, commit signatures), CI (build and test results, coverage on changed lines, flaky-test retries, status checks), code analysis (duplication, maintainability, static-analysis and security findings), harness telemetry (agent sessions, tool calls, tokens, PRs opened, model and harness versions), the eval harness (pass^k by task class) and the AI inventory.
2. **Indicator engine** computes the indicators in Section 7 on a schedule (daily for R1, R2, R7; on change for R6; weekly for R4, R5; on run for R8) and stores them with provenance.
3. **Scoring and tiering** maps indicators to dimension scores 0-4, computes the minimum-across score and the mean, assigns tiers per task class, and computes the estate maturity level.
4. **Evidence store** keeps immutable snapshots of indicators, scores, validations and per-change records for the retention period required by the applicable change-management rules.
5. **Surfaces**: a dashboard (repository, team, estate views), a read API (tier and indicators per repository and task class), notifications, and an evidence-pack export.

Everything the service computes is explainable: each score shows the indicators, thresholds and data sources behind it, and the timestamp of the data.

---

## 7. Requirements

Priorities: **P0** must ship in v1; **P1** planned fast follow; **P2** design for, do not build.

### 7.1 Inventory and scope (P0)

**REQ-1. Repository register.** Every repository in scope is registered with owner (from CODEOWNERS or the inventory), sensitivity tier (from data classification), harnesses observed, task classes attempted, and assessment status (assessable, not assessable, exempt).

- Given a repository exists in the forge, when the nightly sync runs, then it appears in the register within 24 hours with owner and sensitivity tier populated or flagged missing.
- Given a repository has no telemetry source for a dimension, when scored, then that dimension shows "not assessable" and the repository's tier is capped at T0 with the reason stated.

**REQ-2. Monorepo scoping.** Scoring units can be a repository or a directory subtree; a monorepo owner can define units mapped to CODEOWNERS paths.

- Given a monorepo with defined units, when indicators are computed, then each unit has its own score and tier and the repository view shows the distribution.

**REQ-3. Task-class taxonomy.** The platform lead defines task classes (default set: dependency upgrade, test generation, bug fix with reproduction, documentation, feature behind an interface, migration) with a pass^k threshold and k per class.

- Given a task class is added or its threshold changed, when tiers are recomputed, then affected repositories are re-tiered and owners notified.

### 7.2 Indicator catalogue (P0 unless marked)

Each indicator must state its data source, computation, freshness and the dimension score bands. Bands below are defaults; the platform lead can tune them, and changes are versioned.

**R1 Executability and environment determinism**

| Indicator | Source | Computation | Default bands (score 0 / 2 / 4) |
|---|---|---|---|
| Automated-setup success rate | CI or a service-run clean-container build using the declared setup (devcontainer, Dockerfile, setup workflow) | Successful setups / attempts over 14 days | <50% / 50-90% / >95% |
| Reproducible-build rate | CI | Two builds of the same commit produce identical artifact hashes, sampled weekly | not measured / <80% / >95% |
| Median setup time | CI | p50 minutes from clean checkout to test-ready | >30 / 10-30 / <10 |
| Dependency pinning | Forge (Scorecard Pinned-Dependencies check or equivalent) | Score 0-10 | <4 / 4-7 / >7 |
| Sandbox policy | Harness config | Egress policy and no-production-data attestation present for the repository's sensitivity tier | absent / partial / present |

**R2 Verification signal quality**

| Indicator | Source | Computation | Default bands |
|---|---|---|---|
| Coverage on changed lines | CI coverage reports on PRs | Median over last 30 merged PRs | <40% / 40-70% / >80% |
| Flaky-test rate | CI retries and quarantine list | Runs with pass-on-retry / total runs, 30 days | >3% / 1-3% / <0.5% with quarantine process |
| CI feedback latency | CI | p50 minutes to first required-check result | >60 / 15-60 / <15 |
| Static and security analysis | CI and code-analysis platform | Required status checks present for SAST, secrets scanning, dependency risk; findings available to the harness | none / present, advisory / required and machine-readable |
| Green-merge share | Forge | Merged PRs with all required checks passing / merged PRs | <80% / 80-95% / >98% |
| Mutation score (P1) | Mutation tool | On changed code, sampled | not measured / <50% / >70% |

**R3 Task specification hygiene**

| Indicator | Source | Computation | Default bands |
|---|---|---|---|
| Acceptance-criteria coverage | Issue tracker templates | Share of agent-assigned issues with acceptance criteria fields completed | <30% / 30-70% / >90% |
| Acceptance-test linkage | Issue tracker and CI | Share of agent tasks with a linked failing-then-passing test | <10% / 10-50% / >70% |
| Wrong-solution share (P1) | Agent PR failure taxonomy (labels applied at review) | Share of rejected agent PRs labelled wrong solution | >40% / 20-40% / <10% |

**R4 Structure and navigability**

| Indicator | Source | Computation | Default bands |
|---|---|---|---|
| File size distribution | Forge | p90 lines per source file | >1,000 / 400-1,000 / <400 |
| Duplication rate | Code-analysis platform | Duplicated lines / total | >10% / 3-10% / <3% |
| Code-health or maintainability score | Code-analysis platform | Platform score | below platform "warning" / mid / above "good" |
| Dependency cycles | Build graph | Count of cyclic module dependencies | >10 / 1-10 / 0 |
| Code index freshness | Search or index service | Hours since last successful index | >168 / 24-168 / <24 |

**R5 Documentation and decisions**

| Indicator | Source | Computation | Default bands |
|---|---|---|---|
| README completeness | Forge | Purpose, status, setup, test sections present | <2 / 2-3 / 4 of 4 |
| Doc currency | Forge | Days since architecture docs last verified (front-matter date or commit) | >365 / 90-365 / <90 |
| ADR coverage | Forge | ADR directory present; ADRs added for changes tagged architectural in last 6 months | none / present / >70% coverage |
| Broken references | Link checker | Broken internal links in docs | >20 / 1-20 / 0 |

**R6 Context files and procedural knowledge**

| Indicator | Source | Computation | Default bands |
|---|---|---|---|
| Context file presence and ownership | Forge and CODEOWNERS | AGENTS.md, CLAUDE.md or copilot-instructions present and covered by an owner | absent / present, unowned / present, owned |
| Context file size and age | Forge | Lines and days since last edit | >500 lines or >365 days / 150-500 or 90-365 / <150 lines and <90 days |
| Prescriptive content heuristic | Static check | Contains build, test and PR commands; does not contain generated repository overview sections | fails / partial / passes |
| Procedural knowledge on demand | Harness config | Skills, playbooks or knowledge items registered for the repository | none / some / catalogued with owners |
| Incremental token cost per task (P1) | Harness telemetry | Median tokens per task with context file versus without, sampled | >+40% / +20-40% / <+20% |

**R7 Ownership, workflow and guardrails**

| Indicator | Source | Computation | Default bands |
|---|---|---|---|
| CODEOWNERS coverage | Forge | Share of paths with an owner | <60% / 60-95% / 100% |
| Ruleset strength | Forge | Required review, required status checks, signed commits, empty or audited bypass list | <2 of 4 / 2-3 / 4 of 4 |
| Separate approver for agent PRs | Forge | Rule that the assigner cannot approve; agent identity cannot approve | absent / manual practice / enforced |
| Agent identity | Identity provider and harness | Each agent runs under its own identity with repository-scoped credentials | shared human credentials / mixed / dedicated identities |
| Governed-flow share | Harness and forge telemetry | Agent changes arriving through PRs with required checks / all agent changes | <80% / 80-95% / >99% |
| Guardrail hooks | Harness config | Hooks blocking destructive commands, secret access and non-allowlisted egress; MCP allowlist with pinned versions | none / partial / complete |
| Audit log ingestion | Harness and gateway | Agent tool-call logs retained for the change-record retention period | none / partial / complete |

**R8 Measurement and evaluation**

| Indicator | Source | Computation | Default bands |
|---|---|---|---|
| Private eval suite | Eval harness | Tasks per task class from real tickets | none / <20 / 20-50 per class |
| pass^k by task class | Eval harness | All k trials succeed, per class, latest run | below threshold / within 10 points / at or above threshold |
| Cost per merged agent change | Harness and forge | Tokens and compute per merged PR, 30-day median | not measured / measured / measured with trend |
| Outcome attribution | Code analysis, incident system, forge | Review time, rework, defects and vulnerabilities attributed to agent-assisted changes | not measured / partial / complete |
| Regression evals on change | Eval harness | Suite re-run on model or harness version change | never / manual / automatic |

### 7.3 Scoring and tiering (P0)

**REQ-4. Dimension scores.** Each dimension scores 0-4 from its indicators using the band table; where indicators disagree, the dimension takes the lowest banded score unless the platform lead has configured a weighting, which is versioned.

**REQ-5. Repository score.** The repository score is the minimum across the eight dimensions; the mean is shown alongside and labelled as a planning aid only.

- Given a repository with seven dimensions at 4 and one at 1, when scored, then the repository score is 1 and the dashboard highlights the minimum dimension.

**REQ-6. Evidence caps.** No dimension may score above 2 without telemetry-derived indicators, or above 4 without a recorded second-line validation.

- Given a dimension whose indicators come only from self-declared configuration, when scored, then it is capped at 2 and labelled "telemetry required."

**REQ-7. Tiers.** Tier is computed per task class: T0 (score 0-1), T1 (2, with R1, R2, R7 at 2 or above), T2 (3 across all dimensions and pass^k at or above the class threshold), T3 (4 across all dimensions with monitoring and audit evidence recorded).

- Given a repository at score 3 whose pass^k for "migration" is below threshold, when tiered, then "migration" is T1 while other classes meeting their thresholds are T2.

**REQ-8. Tier changes.** Promotions require the missing-evidence checklist to be empty; demotions happen automatically when an indicator drops below its band, with the owner notified and a 5-working-day grace period before harnesses are told, except for R7 guardrail regressions, which take effect immediately.

**REQ-9. Estate maturity level.** The estate level (1 Ad hoc to 5 Optimizing) is computed from process coverage: share of repositories inventoried, share scored with automated indicators, share with second-line validation, presence of regression evals, presence of external assurance. The definition follows Table 3.2 of the paper and is displayed with the supporting percentages.

### 7.4 Surfaces (P0)

**REQ-10. Repository view.** Score, tier per task class, dimension breakdown, indicator values with sources and timestamps, ranked fix list with expected tier impact, promotion checklist, history.

**REQ-11. Estate view.** Tier distribution, estate maturity level, share of agent traffic by tier, top blocking dimensions, remediation burn-down, outcome metrics for T2+ repositories (delivery, quality, reliability, cost) next to usage.

**REQ-12. Read API.** Tier and indicators per repository and task class, versioned, with an "as of" parameter; rate-limited; consumable by harness configuration and ruleset automation in later phases.

**REQ-13. Notifications.** Owners notified on score drops, tier changes and stale data; second line notified on promotion requests.

### 7.5 Evidence pack (P0)

**REQ-14. Per-change record.** For every agent-authored PR, the service stores task reference, acceptance criteria, agent identity, model and harness version, context files and skills in effect, verification results, approver identity and rollback note, linked to the PR.

**REQ-15. Evidence pack export.** For a repository or the estate, as of a date, export a bundle containing: inventory entries, register entry with tier and indicators, ruleset and CODEOWNERS snapshots with bypass logs, per-change records, sandbox and data-masking attestations, test and scan results, agent audit-log references, eval results, third-party register references, validation records. Format: PDF summary plus machine-readable JSON.

- Given an auditor requests the pack for a repository as of 30 June, when the export runs, then it completes within one hour and every item either contains data or states why it is not applicable.

**REQ-16. Retention.** Evidence snapshots are immutable and retained for the longest applicable change-record retention period; deletion requires a recorded approval.

### 7.6 Security, privacy and compliance (P0)

**REQ-17. No content egress.** The service stores indicators, metadata and references, never source code, prompts or agent transcripts. Under zero-data-retention harness configurations, collectors use aggregate telemetry only.

**REQ-18. Access control.** Repository views follow forge permissions; estate views require a role; evidence packs are generated only for authorized second- and third-line roles and logged.

**REQ-19. No per-person metrics.** The data model has no per-individual productivity fields; agent identities are distinguished from human identities and only agent identities appear in per-change records as authors.

**REQ-20. Sensitivity alignment.** Repository sensitivity tier is displayed with the RARM tier and constrains which harnesses and retrieval sources may be recorded as permitted.

### 7.7 Nice-to-have (P1)

- Harness integration that shows tier and permitted task classes inside the harness before delegation (Claude Code, Copilot, Codex, Devin adapters).
- Mutation score, wrong-solution taxonomy and incremental token cost indicators.
- Fix-list automation that opens tracked issues for the top remediation items with owners and due dates.
- Comparison design support: mark repositories or teams as treatment and control for a staggered rollout and report the difference in outcome metrics.

### 7.8 Future considerations (P2)

- **Gating.** Rulesets and harness policies that read tier from the API and block agent PRs or task classes below tier. Design the API and evidence caps so this can be switched on without re-scoring.
- **Remediation agents.** Agents that raise R1, R2, R5 and R6 under the same gates, drawing tasks from the fix list.
- **Non-code repositories** and enterprise agents outside software engineering.
- **External assurance export** mapped to ISO/IEC 42001 controls and to the MAS AI risk management guidelines once final.

---

## 8. Success metrics

| Metric | Type | Target | Measured how and when |
|---|---|---|---|
| Repositories inventoried with owner and sensitivity tier | Leading | 100% of in-scope repositories by day 30 | Register versus forge listing, weekly |
| Repositories with automated scores | Leading | Top 50 by agent traffic by day 90; 100% by day 365 | Register, monthly |
| Indicator freshness | Leading | 95% of R1, R2, R7 indicators under 24 hours old | Engine job logs, daily |
| Owner engagement | Leading | 70% of scored repositories have an owner who viewed the fix list within 30 days | Dashboard analytics, monthly |
| Agent traffic on tiered repositories | Lagging | 80% of agent PRs on repositories at T1 or above for the task class by day 180 | Harness and forge telemetry, monthly |
| Governed-flow share | Lagging | 99% of agent changes through PRs with required checks by day 180 | Forge telemetry, monthly |
| Evidence-pack turnaround | Lagging | Under one working day; zero supplementary requests from internal audit in the first audited cycle | Audit log and audit feedback, per cycle |
| Remediation mix | Lagging | 60% of closed remediation items in R1, R2 or R7 in the first two quarters | Fix-list tracking, quarterly |
| Outcome delta on T2 repositories | Lagging | Review time per agent PR and rework rate on T2 repositories at or below the human baseline within two quarters of promotion; change-failure rate not worse than baseline | DORA and code-analysis metrics, quarterly, with a comparison group where available |
| Tier reliability | Lagging | pass^k on T2 task classes stays at or above threshold in 90% of scheduled eval runs | Eval harness, monthly |

Success threshold for v1: the first five leading metrics met and no audit finding on agent-authored change controls in the first examined cycle. Stretch: 90% of agent traffic on T1+ repositories and measured review-time parity on T2 repositories within two quarters.

---

## 9. Open questions

| Question | Owner | Blocking? |
|---|---|---|
| What pass^k threshold and k per task class reflect the firm's risk appetite for T2? The paper suggests reliability must govern; the number is a policy choice | Technology risk with platform engineering | Yes, before tiering |
| Is the tier advisory in v1, or does any harness read it immediately? | Platform engineering and harness owners | Yes |
| Which team owns the score of record: platform engineering (producer) or technology risk (validator)? | CTO office | Yes |
| Which harness telemetry is available under the firm's zero-data-retention terms, and at what granularity? | Harness owners and legal | Yes, for R8 indicators |
| How are monorepo units defined where CODEOWNERS paths do not align with services? | Repository owners | No |
| Should indicator values be visible across teams (transparency and learning) or only to owners and second line (gaming risk)? | Engineering leadership | No |
| What retention period applies to per-change records for agent PRs under each applicable regime? | Compliance and legal | Yes, for REQ-16 |
| Which framework covers coding agents in the firm's risk taxonomy while US model risk guidance excludes them, and who signs the statement of coverage? | Technology risk | No, but needed before the first evidence pack |
| Should the wrong-solution taxonomy be applied by reviewers or by a model-based grader, and how is grader bias controlled? | Platform engineering | No |

---

## 10. Timeline considerations

**Dependencies.** Forge API access with organization-wide read scope; CI coverage-on-changed-lines reports; a code-analysis platform with an API; harness telemetry agreements; an eval harness and a first private task suite; the AI inventory's API; identity provider support for agent identities.

**Hard dates.** EU Cyber Resilience Act reporting obligations from September 2026 and DORA supervision already in force set the expectation for source-code testing and change records; MAS's AI risk management guidelines are expected to be finalized with a 12-month transition; the US interagency request for information on generative and agentic AI in model risk management is pending. None of these dates blocks v1, but the evidence pack should be examinable before the first of them is enforced against the firm.

**Phasing.**

- **Phase 0 (weeks 0-6): inventory and collectors.** Register, sensitivity tiers, collectors for R1, R2 and R7, first task-class taxonomy. Exit: REQ-1 to REQ-3 met for the top 50 repositories.
- **Phase 1 (to day 90): scoring and repository view.** Indicator engine, scoring and tiering, repository dashboard, notifications. Exit: top 50 repositories scored with fix lists; first tier assignments validated by second line.
- **Phase 2 (to day 180): all dimensions and evidence.** R3 to R6 and R8 collectors, eval-harness integration, per-change records, evidence-pack export, estate view, read API. Exit: evidence pack accepted by internal audit for one repository; 80% of agent traffic on tiered repositories.
- **Phase 3 (to day 365): estate scale and validation.** Whole-estate scoring, second-line validation workflow, regression-eval triggers, P1 harness integration. Exit: estate maturity level 4 evidenced; gating design (P2) reviewed.

---

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Scores are gamed (tests that assert nothing, context files padded to pass heuristics) | Minimum-across scoring; telemetry-derived indicators; second-line validation above 2; mutation score in P1; random manual audits of top-tier repositories |
| Low scores discourage teams rather than direct them | Fix list with expected tier impact; "not assessable" state distinct from low score; no per-person metrics; leadership reporting on remediation, not blame |
| Telemetry gaps make the service look like a compliance tax | Phase 0 limited to indicators the firm already collects; freshness metric visible; cost of collection tracked |
| Tier becomes binding before it is trusted | Advisory in v1; gating designed but not enabled until tier reliability metric is met for two quarters |
| Indicator bands are wrong for parts of the estate (legacy platforms, embedded, data pipelines) | Bands versioned and tunable per repository family; exceptions recorded with rationale and expiry |
| Vendor telemetry changes (endpoint retirements, format changes) | Collector adapters isolated per vendor; contract tests; degradation surfaces as "stale" not as a lower score |

---

## 12. Sources

This PRD implements Sections 3 and 5 of the companion paper, which cite the underlying evidence. The requirements above rely in particular on: the ML Test Score's minimum-across scoring rule (Breck et al., 2017); the environment-setup benchmarks (EnvBench, Repo2Run, ExecutionAgent, 2024-2025); Google's flaky-test and static-analysis practice (Micco, 2016; Sadowski et al., 2018); the AGENTS.md controlled study (Gloaguen et al., 2026); DORA's 2025 AI Capabilities Model and AI-accessible internal data guide; OpenSSF Scorecard checks; GitHub rulesets and CODEOWNERS documentation; Sonar's quality gate for agentic AI; DORA's technical standards Articles 16 and 17 on source-code testing and independent change approval; PCI DSS v4.0.1 Requirement 6; MAS Technology Risk Management Guidelines (2021); the FINOS AI Governance Framework v2.0; and SR 26-2 on the current scope of US model risk guidance. Full citations with URLs are in the paper's reference list.
