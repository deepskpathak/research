# Knowledge Graphs That Serve Generative Agents: Demand, Value, Case Studies

## 1. Demand

- **Review history is the source data.** Qodo calls recurring comments, accepted and rejected suggestions, and approval patterns the richest signal of how a team really reviews code, sitting in plain sight in PR history.
- **Agents start every task without that context.** Webflow described agents as starting every task "as strangers".
- **Enterprises are actively evaluating.** One GitLab field note records a customer evaluating knowledge graphs to shift to agentic development. For that customer, RBAC across repositories is a non-negotiable requirement.
- **Agent usage grows once a graph is connected.** Expo saw 38x growth in MCP calls from coding agents between May and September 2026.

## 2. Value

- **Accuracy:** GitLab reports up to 45x fewer hallucinations and 4.5x fewer tokens in its own testing.
- **Cost and speed:** Invoca made its Claude Code and Cursor agents 30% faster and 40% cheaper.
- **Standards that maintain themselves:** in Qodo's loop, every interaction with the review agent is a learning signal that creates, updates and deletes rules without manual curation.
- **Day-one onboarding:** a team's real standards apply from a new engineer's first PR, instead of being learned through months of repeated comments.

## 3. Case studies

| Company | Platform | Result |
| --- | --- | --- |
| **Compare the Market** | GitLab Orbit | Graph-grounded agents placed inline review comments in the right location 70% of the time, vs 58% for RAG, on 79 real MRs |
| **Invoca** | Unblocked | Coding agents 30% faster, 40% cheaper |
| **Cloudbeds** | Unblocked | Context for nearly 1,000 repositories at a third of the tokens |
| **Codat** | Unblocked | 92 NPS; MCP wired into Claude Code so agents pull context automatically |
| **Advidi** | Unblocked | Engineers and the OpsClaw incident agent share one context engine across 400+ repos, Slack, Confluence and Jira |
| **Expo** | Unblocked | 90% of weekly context gathering eliminated for product |
| **Privado** | Bito AI Architect | Enterprise SSO shipped in 5 hours of working time (14x faster) |
| **Pax8** | Qodo | Scattered standards surfaced and put into practice by the Rules System |

**A small example of mining:** in one Qodo walkthrough, 11 accepted review comments became 5 rules. The bar for a rule is a reviewer comment that the author agreed with and fixed, recurring across PRs.

## 4. Read with caution

- Compare the Market's A/B test is the only independent-style benchmark here, and DevOps.com notes one customer test doesn't settle the question.
- Every other number comes from a vendor case study.
- Not every evaluation succeeds. One customer said Orbit lacks full API access and is "not a full MCP as expected".

**Next action:** Use the Compare the Market setup as the template for wiselotus evals: the same MRs, compared across no context, RAG and graph.

## Sources

- [GitLab Transcend announcements](https://about.gitlab.com/blog/gitlab-transcend-announcements)
- [DevOps.com on Orbit](https://devops.com/gitlab-bets-context-not-bigger-models-will-fix-ai-agent-costs)
- [GitLab: Orbit customer use cases](https://gitlab.com/gitlab-org/gitlab/-/work_items/594388)
- [Unblocked: Invoca](https://getunblocked.com/customers/invoca/)
- [Unblocked: Expo](https://getunblocked.com/customers/expo/)
- [Unblocked: Cloudbeds](https://getunblocked.com/customers/cloudbeds/)
- [Unblocked: Codat](https://getunblocked.com/customers/codat/)
- [Unblocked: Advidi](https://getunblocked.com/customers/advidi/)
- [Unblocked: Webflow](https://getunblocked.com/customers/webflow/)
- [Bito: Privado case study](https://www.casestudies.com/company/bito-ai/case-study/privadoai-ships-enterprise-sso-in-5-hours-with-bito)
- [Qodo: Rule Miner blog](https://www.qodo.ai/blog/codify-what-your-best-reviewers-already-know-with-rule-miner/)
- [Qodo 2.4 release](https://www.qodo.ai/blog/introducing-qodo-2-4-the-next-layer-of-code-quality-governance/)
