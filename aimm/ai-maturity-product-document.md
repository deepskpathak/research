# AI Maturity Assessment — Technical Product Document

**Status:** Proposed MVP · **Date:** 16 September 2026  
**Audience:** Product, engineering, AI platform, risk, and business owners  
**Purpose:** Help an organization decide which AI workflows to pilot, scale, constrain, improve, or retire using inspectable evidence.

This document condenses the research paper into product requirements. Research and company claims retain their original dates; sources were checked on 15 September 2026. The proposed rubric and acceptance criteria require local calibration and are not a validated industry ranking.

## 1 What is the problem

Organizations track AI licenses, model counts, and demonstrations without consistently knowing whether deployed workflows are ready, reliable, or valuable. A model benchmark cannot establish correct behavior across enterprise data, permissions, human review, and downstream actions.

The product must keep three decisions separate:

| Decision | Question | Required output |
|---|---|---|
| Maturity | Can teams repeatedly deliver and improve AI workflows? | Capability profile with evidence coverage and confidence |
| Readiness | May this system version enter this deployment stage? | Reviewed gate decision, restrictions, owner, and review trigger |
| Effectiveness | Does this workflow improve outcomes against a credible baseline? | Outcome change, uncertainty, full cost, and attribution limits |

**Unit of assessment:** business unit → workflow → system version. A version includes the model, prompts, retrieval configuration, knowledge sources, tool schemas, and permissions. Enterprise reporting aggregates these records without hiding blocked workflows.

**Primary users and jobs**

- **Business owner:** establish the outcome, baseline, and investment decision; name the final accountable release approver in the assessment record.
- **Engineering/platform owner:** identify missing integration, evaluation, and operational controls.
- **Risk/security reviewer:** verify evidence and approve or reject the applicable control gates. The release approver cannot override failed mandatory gates.
- **Finance partner:** distinguish realized savings, productive capacity, and incremental margin.

**MVP scope:** assess two bounded workflows using existing enterprise records; produce evidence-linked findings, a capability profile, readiness decisions, and an improvement backlog.

**Non-goals:** autonomous deployment approval, regulatory certification, a universal company score, or inferring ROI from adoption. Academic readiness and capability research supports assessing organizational resources and practices alongside technology. [1][2]

## 2 What agents need as context

### Required sources and contracts

An **assessment agent** analyzes organizational evidence. An **operational agent** executes or assists a business workflow. They need different records and permissions.

| Context | Authoritative source | Required metadata/control |
|---|---|---|
| Scope and success | Workflow charter, KPI dictionary, owner | Population, baseline, exclusions, outcome, deployment stage |
| Rules and authority | Approved policies, delegation matrix | Effective version, jurisdiction, precedence, approval limits |
| Organizational evidence | Evaluation store, release records, incidents, training and finance records | Source ID, owner, observation period, system version |
| Domain knowledge | Manuals, procedures, contracts, knowledge base | Provenance, validity dates, access labels, retirement rules |
| Live task state | CRM, ERP, ticketing, transaction systems | Tenant/user identity, record version, timestamp, concurrency checks |
| Tools and evaluation | API schemas, test cases, runbooks | Preconditions, allowed actions, retry behavior, expected final state |

Every evidence item must be addressable by source and version. Preserve source permissions through retrieval, caches, generated summaries, and exports. Mark inaccessible or missing evidence **unknown**; do not treat it as a failed control or invent supporting facts.

Context is a managed dependency: test relevance, freshness, and completeness for the task. More retrieved text does not establish better answers. Retrieved content remains data; authorization must be enforced outside the language model. [5][6]

### Exact assessment workflow

1. **Register:** freeze scope, rubric version, assessed system versions, reporting period, and sampling plan.
2. **Collect:** read approved sources; store evidence references, timestamps, permissions, and content hashes or immutable versions.
3. **Reconcile:** compare inventory with release/usage records; detect stale, contradictory, or unsupported claims.
4. **Evaluate:** map evidence to rubric criteria and deployment gates; run configured checks against held-out cases.
5. **Draft:** propose findings with supporting evidence, missing evidence, coverage, and confidence. A policy's existence does not prove its operation.
6. **Review:** accountable humans adjudicate findings; engineering verifies controls, finance verifies benefits, and the designated approver records the readiness decision.
7. **Track:** create owned remediation items; reassess when evidence expires or a material dependency changes.

The assessment agent reads source systems and writes drafts to its review store. It cannot approve a release or modify production records.

### Operational example: support refund

`Verify identity → read current order → retrieve applicable policy → propose resolution → authorize → execute → verify final state`

The order establishes facts; policy establishes eligibility; the authorization service establishes permitted actions. Bind approval to the specific amount and record version. Use an idempotency key to prevent duplicate payments, check transaction state after timeouts, and escalate conflicting policy or partial execution. Initially expose only a draft operation; add payment execution after its own gates pass.

Evaluate final records and policy adherence, not just answer fluency or successful API calls. The τ-bench research provides a useful final-state and repeated-trial evaluation pattern, although its simulated results do not establish enterprise readiness. [4]

## 3 What we have in the industry

### Existing building blocks

| Building block | Applicable capability | Product implication |
|---|---|---|
| NIST AI RMF 1.0; ISO/IEC 42001:2023 [7][8] | Risk activities and AI management systems | Map requirements to evidence and accountable decisions; neither establishes workflow ROI |
| AWS CAF for AI; Google Cloud MLOps guidance [9][10] | Organizational capability planning and deployment automation | Reuse capability categories and engineering practices; validate local readiness separately |
| ML Test Score [3] | 28 production-readiness tests | Assess data, models, infrastructure, and monitoring together |
| Academic readiness/capability research [1][2] | Strategy, resources, skills, organizational practices | Use observable evidence; survey associations are not causal ROI estimates |

### Large-organization cases and transferable lessons

| Case | Documented evidence | Requirement to carry forward |
|---|---|---|
| Uber Michelangelo, 2017 [11] | Shared lifecycle platform for data, training, deployment, and monitoring; first-party engineering account | Capture reproducible versions and reusable operational evidence |
| Microsoft Responsible AI Standard v2, 2022 [12] | Published internal governance requirements and assessment practices | Attach review evidence and decision ownership to releases |
| DBS, 2024 reporting period [13] | Reported SGD 750 million economic value from analytics and AI/ML | Maintain a benefit ledger; do not reinterpret the disclosure as audited incremental profit or generative-AI-only value |
| Morgan Stanley, June 2024 [14] | Reported Assistant adoption by 98% of Financial Advisor teams | Measure adoption separately from individual use, quality, time savings, and financial benefit |

**Effectiveness is task-specific.** A published observational study of 5,172 support agents reported 15% more issues resolved per hour with AI assistance. [15] A separate early-2025 randomized study of 16 experienced developers across 246 tasks found 19% longer completion times; this is a specialized research preprint. [16] Neither result is a company-wide productivity forecast. The product must support local comparison groups and report task/population boundaries.

## 4 What a regular company can do

### MVP architecture and data model

`Approved sources → access-controlled connectors → evidence registry → assessment agent + deterministic checks → human review → decisions and remediation`

Reuse existing identity, document management, ticketing, and analytics services. Start with manual imports where connectors would delay the first assessment. Store large documents and traces in their governed repositories; retain references and permitted excerpts in the registry.

| Entity | Minimum fields |
|---|---|
| Assessment | ID, business unit, workflow, population, stage, system version, rubric version, owner, release approver, period |
| Evidence | ID, source URI/version, observed-at, valid-until or refresh rule, owner, access scope, evidence type |
| Finding | Criterion, claim, evidence IDs, rating, coverage numerator/denominator, confidence rationale, reviewer |
| Decision | Assessment ID, stage, gate results, disposition, approver, restrictions, expiry/reassessment trigger |
| Evaluation run | System/test-set versions, comparison design, sample, metrics, uncertainty, failures, cost boundary |

Keep finalized records immutable and supersede them with new revisions. Log review changes. Recheck access before displaying or exporting evidence.

### Functional requirements and acceptance

| ID | Requirement | MVP acceptance |
|---|---|---|
| R1 | Register scope and versions | No finalized assessment without required identifiers and an accountable owner |
| R2 | Link findings to evidence | Every finalized non-unknown rating resolves to permitted evidence and a reviewer; unknowns include a resolution action |
| R3 | Generate a capability profile | Eight dimensions retained separately; missing evidence cannot become zero or a positive rating |
| R4 | Enforce readiness gates | Failed or unknown mandatory gates block approval for that scope/stage; restrictions require a revised, enforceable scope whose applicable gates pass |
| R5 | Measure effectiveness | Every benefit claim declares its baseline/comparator, population, uncertainty, cost boundary, and finance-reviewed benefit category |
| R6 | Maintain reassessment and export | Dependency changes flag affected decisions for review; export preserves scope, evidence links, restrictions, and revision history |

Rate eight dimensions: **strategy/value; workflow/people; data/context; engineering/integration; evaluation/experimentation; governance/accountability; security/action control; operations/learning.**

Use **U: unknown; 0: absent; 1: ad hoc; 2: defined and used with gaps; 3: consistently operating; 4: demonstrably improving.** Levels 3–4 require current operating records; level 4 additionally requires measured improvement. Report coverage and confidence separately. Do not use an arithmetic average to authorize deployment.

Readiness gates cover purpose/ownership, data permissions, task quality, action authorization/recovery, human review capacity, and monitoring/economics. Decisions are **ready**, **ready with restrictions**, or **not ready**, for a specified stage. An expired or materially invalidated decision cannot remain an active authorization without review.

The existing release process must check a current decision before progressing deployment. The registry alone does not enforce production behavior.

### Measurement and release criteria

**Measure the assessment product:** evidence retrieval recall, citation correctness, unsupported positive findings, missed critical gaps, agreement with independent reviewers, and review time. Before its first pilot, the product owner and risk/security reviewers must approve thresholds and a held-out test set for these metrics. Test stale sources, conflicting policies, denied access, prompt injection, and changed versions. Require zero prohibited disclosures or unauthorized approval transitions in the release suite; this is a test criterion, not proof of zero production risk.

**Measure each assessed workflow:**

- Task success = accepted correct outcomes / all eligible assigned tasks; retain failures and escalations in the denominator.
- End-to-end labor and elapsed time, including verification, rework, and waiting.
- Full workflow cost / accepted successful outcomes, with allocation of setup and shared costs disclosed.
- Quality failures by severity and relevant segment; latency and recovery performance.
- Incremental benefit against the declared comparator, with uncertainty and adoption reported separately.

Predeclare quality limits, the minimum useful benefit, and sample requirements. Randomize eligible tasks or teams where feasible; otherwise document comparison assumptions and confounding. Scale only when the agreed benefit rule and applicable readiness gates both pass. Finance must distinguish reusable capacity from cash savings.

### First 90 days

| Period | Deliverable | Accountable roles |
|---|---|---|
| Days 1–30 | Two workflow charters, source/permission map, baseline, rubric, evaluation plan | Business and data owners |
| Days 31–60 | Evidence registry, draft assessments, offline tests, shadow or supervised pilot | Engineering and domain evaluators |
| Days 61–90 | Comparative results, reviewed economics, signed decisions, remediation backlog | Named release approver, risk/security, finance |

The first assessment cycle's outcome is **two defensible workflow decisions**, including stop or improve when warranted. Ninety days is a planning assumption; evaluation must continue if evidence is insufficient. Review the portfolio quarterly and after material changes. Track whether higher capability ratings predict better outcomes over time.

Keep the common evidence model but calibrate gates by sector: local clinical validation in healthcare, decision and loss outcomes in financial services, site/sensor validation in manufacturing, and transaction consistency in customer operations. Confirm applicable requirements with domain owners.

### Sources

1. Jöhnk, Weißert & Wyrtki (2021). [Organizational AI readiness factors](https://link.springer.com/article/10.1007/s12599-020-00676-7). *Business & Information Systems Engineering*.
2. Mikalef & Gupta (2021). [AI capability: conceptualization and empirical measurement](https://doi.org/10.1016/j.im.2021.103434). *Information & Management*.
3. Breck et al. (2017). [The ML Test Score](https://research.google.com/pubs/archive/aad9f93b86b7addfea4c419b9100c6cdd26cacea.pdf). IEEE Big Data.
4. Yao et al. (2024). [τ-bench](https://arxiv.org/abs/2406.12045). Research preprint.
5. Anthropic (2025). [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). Engineering guidance.
6. OWASP (2025 edition). [LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/). Security guidance.
7. NIST (2023). [AI Risk Management Framework 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf).
8. ISO/IEC (2023). [ISO/IEC 42001](https://www.iso.org/standard/42001). Public standard description.
9. AWS (2024). [Cloud Adoption Framework for AI](https://docs.aws.amazon.com/whitepapers/latest/aws-caf-for-ai/aws-caf-for-ai.html).
10. Google Cloud (2024 review). [MLOps: delivery and automation pipelines](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning).
11. Uber (2017). [Meet Michelangelo](https://www.uber.com/blog/michelangelo-machine-learning-platform/). Engineering case study.
12. Microsoft (2022). [Responsible AI Standard v2](https://msblogs.thesourcemediaassets.com/sites/5/2022/06/Microsoft-Responsible-AI-Standard-v2-General-Requirements-3.pdf).
13. DBS (2024 reporting period; published 2025). [Letter from Chairman and CEO](https://www.dbs.com/annualreports/2024/letter-from-chairman-ceo.html). Company disclosure.
14. Morgan Stanley (2024). [Debrief launch announcement](https://www.morganstanley.com/press-releases/ai-at-morgan-stanley-debrief-launch). Company disclosure.
15. Brynjolfsson, Li & Raymond (2025). [Generative AI at Work](https://academic.oup.com/qje/article/140/2/889/7990658). *Quarterly Journal of Economics*; observational field study.
16. Becker et al. (2025). [AI and experienced developer productivity](https://arxiv.org/abs/2507.09089). Research preprint; randomized trial.
