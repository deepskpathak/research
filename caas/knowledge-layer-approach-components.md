# Approach

**Context as a Service (CaaS)** gives every coding agent at the firm one governed way to get the right engineering knowledge for the task in front of it. We separate the work into two planes. Preparing knowledge happens once, when sources change. Delivering context happens on every agent request.

![CaaS architecture](caas-architecture.png)

## Guiding principles

- **Source-owned, change-driven.** Each authoritative source (EngHub, standards, repos, Jira/Confluence, code graph, build/test/scan evidence) feeds a pipeline triggered by a commit, edit, schema change, or policy update. We don't run bulk nightly crawls.
- **Govern before you serve.** Every item carries owner, classification, entitlement, trust, version, and timestamp. Certification fails closed, so uncertified content is never served.
- **Shape for tasks, not for search.** Content is pre-shaped into summaries, sections, pointers, and relationships. Agents get a compact bundle, not raw documents.
- **Hybrid retrieval.** Lexical search (exact terms), semantic search (meaning), and graph traversal (code, dependencies, links) run in parallel. Their results are merged and then reranked for the current task.
- **Harness-agnostic delivery.** The same bundle reaches Claude Code, Devin, Codex, GSCode, CI, and future agents through MCP, API, CLI, or plugin.
- **Measure everything.** Telemetry on relevance, citations, outcome, and cost feeds ranking, content, and factory improvements.

## Plane 1: Knowledge preparation (build time)

1. **Connect & Extract:** pull, push, or event-based intake from each source.
2. **Normalize:** convert into a canonical document plus a metadata contract.
3. **Shape for Tasks:** produce summaries, sections, pointers, and relationships.
4. **Enrich & Govern:** attach owner, classification, entitlement, trust, version, and timestamp.
5. **Certify:** run quality, provenance, compliance, and safety checks; fail closed.
6. **Index & Publish:** write to the semantic, lexical, graph, and metadata indexes in the Governed Context Plane.

## Plane 2: Context delivery (runtime)

1. **Receive task:** query, repo, workflow, task type, and session state.
2. **Establish identity & scope:** caller, entitlements, repo, and data classification.
3. **Understand the task:** classify intent and identify the relevant standards and source types.
4. **Retrieve and merge:** run lexical, semantic, and graph search in parallel, then deduplicate and reconcile scores.
5. **Filter & policy check:** entitlement, trust, freshness, and certification.
6. **Rerank for the task:** weigh authority, relevance, workflow stage, and recency.
7. **Build the context bundle:** summary first, then applicable rules, recommended skills/tools, authoritative pointers, citations, and detail-retrieval handles.
8. **Budget & condense:** remove redundancy and fit the model's context limits.
9. **Return and cache:** return the bundle through MCP, API, CLI, or plugin, and cache reusable task-shaped results with invalidation.

## How the approach maps to phases

| Phase | Focus |
|---|---|
| **POC 1** | Fewer than 30 standards, one harness, one channel. Proves agents can reach knowledge they otherwise cannot. |
| **POC 2** | Telemetry baseline (tokens, queries, logs) comparing CaaS against MCP-accessed standards. Informs the choice of distribution channel. |
| **MVP** | End-to-end pipeline (both planes) on the initial sources, with basic security and monitoring. |
| **Beta** | Feedback loop live, multi-team usage, measured change in agent behavior. |
| **RC** | Source owners run their own factories. SLAs and observability are documented. |
| **GA** | Full entitlement, audit, and support. A documented onboarding interface for consumers. |
| **Operations** | Source onboarding process, freshness and deprecation reviews, support rotations. |

---

# Components

| Component | Responsibility | What it covers (diagram) | Key design decisions | Technology alternatives |
|---|---|---|---|---|
| **1. Ingestion** | Get knowledge out of authoritative sources the moment it changes | Source-owned pipelines; Connect & Extract; Normalize | Connector contract (pull/push/events); canonical document and metadata schema; ownership stays with the source | **Events:** Kafka, Amazon MSK, Kinesis. **Orchestration:** Temporal, Airflow, Dagster. **Parsing:** Apache Tika, Unstructured. **Change hooks:** GitHub/GitLab webhooks, Atlassian webhooks, Microsoft Graph change notifications (SharePoint) |
| **2. Chunk / Tag** | Make content task-ready and governable | Shape for Tasks; Enrich & Govern; Certify | Chunking by structure (sections, rules) not fixed size; required tags (owner, classification, entitlement, trust, version, timestamp); fail-closed certification | **Chunking:** LlamaIndex or LangChain splitters, tree-sitter (code-aware). **Summaries:** Claude via Bedrock or an internal LLM gateway. **Policy and tags:** Open Policy Agent (OPA), Cedar, Microsoft Purview. **Certification:** Great Expectations, Pydantic schema validation, custom checks |
| **3. Storage** | Durable, governed home for prepared knowledge | Document/object store; metadata & semantic catalog; provenance & certification records | Immutable versions; catalog as the source of truth for metadata; provenance kept for audit | **Objects:** S3, MinIO, firm object store. **Metadata:** PostgreSQL, DynamoDB. **Catalog:** DataHub, OpenMetadata, Collibra. **Provenance:** OpenLineage with Marquez, append-only audit tables |
| **4. Indexing / Ranking** | Find and order the right context for a task | Semantic + lexical index; knowledge/code graph; runtime steps 3 to 6 | Hybrid retrieval with score normalization; policy filter before rerank; rerank signals: authority, relevance, workflow stage, recency | **Hybrid search:** OpenSearch or Elasticsearch (BM25 + kNN), Vespa, PostgreSQL with pgvector. **Vector only:** Milvus, Weaviate, Qdrant. **Graph:** existing firm knowledge graph, Neo4j, Amazon Neptune. **Embeddings:** Voyage, Cohere, Titan, open models (BGE, E5). **Rerank:** Cohere Rerank, cross-encoder models, Vespa ranking profiles |
| **5. Caching** | Cut latency and cost on repeat tasks | Context cache (task/query keyed); cache of task-shaped results | Cache keys include entitlement scope; event-driven invalidation when a source changes; TTL as a safety net | **Key-value:** Redis, Valkey, ElastiCache, Memcached. **Semantic cache:** Redis vector search, GPTCache. **Invalidation:** Kafka change events, CDC (Debezium) |
| **6. Distribution** | Deliver bundles to any harness | Identity & scope; Build Bundle; Budget & Condense; MCP/API/CLI/plugin | One bundle format, many channels; caller identity drives entitlements; token budget per model | **MCP:** official MCP SDKs (TypeScript, Python, Java/Kotlin). **API:** REST or gRPC behind Kong, Apigee, or the firm gateway. **CLI:** Go or Kotlin native binary. **Plugins:** Claude Code plugins/skills, IDE extensions. **Identity:** OAuth 2.0/OIDC, SPIFFE for service identity |
| **7. Feedback Loop** | Learn from real agent use | Telemetry & feedback; improvements to ranking, content, and factories | Capture relevance, citations, outcome, and cost per request; triage cadence; top findings feed the GA plan | **Telemetry:** OpenTelemetry with Prometheus/Grafana, Splunk, Datadog. **LLM observability and evals:** Langfuse, Arize Phoenix, LangSmith. **Analytics:** Snowflake, Databricks |

## Trade-offs to weigh

- **One search engine vs. specialists.** OpenSearch or Vespa covers lexical and vector search in one system, with fewer moving parts. Separate vector databases can tune semantic search further, but you then have to reconcile scores across systems.
- **Firm knowledge graph vs. a new graph store.** Reusing the existing graph avoids duplicating data and keeps one source of truth. A dedicated Neo4j or Neptune instance gives the team more control, at the cost of syncing two graphs.
- **Managed vs. self-hosted LLM observability.** Langfuse and Phoenix can be self-hosted, which suits data-residency rules. LangSmith is quicker to start but is primarily SaaS.
- **Temporal vs. Airflow.** Temporal fits event-driven, per-change pipelines with retries. Airflow fits scheduled batch work better.

## Cross-cutting concerns

- **Security & entitlement:** enforced at both tag time (Chunk/Tag) and serve time (Indexing/Ranking filter). Content is never served without an entitlement match.
- **Observability:** per-stage metrics on both planes, with SLAs defined by RC.
- **Freshness:** change-driven ingestion plus scheduled deprecation reviews in Operations.
