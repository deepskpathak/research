# Code Graph Vendors: Landscape, Shortlist and Use Cases

**Research date:** 2026-11-18 | **Scope:** industry and open-source code graph tools that serve AI agents, change campaigns, code review and knowledge graphs

**How to read this**

- Every fact carries a numbered source. Lines marked **Assessment** are my analysis, not sourced facts.
- **Vendor-reported** means the number comes from the party selling or building the tool. Independent benchmarks are rare.
- GitHub stars and forks were read from the GitHub REST API on 2026-11-18 at 02:06 UTC, and each figure links to its repository.
- "Generative agents" is read here as AI coding agents that generate code (Claude Code, Codex, Cursor and similar).

---

## 1. Summary

**Bottom line (Assessment):** no single vendor covers all four use cases well. The pattern that fits the evidence is a layered stack: a precise, persistent code graph as the corpus, an SDLC graph for merge request and pipeline context, and a deterministic transformation engine for campaigns, all served to agents over MCP.

**What changed in 2026**

- **Code graphs became agent infrastructure.** Sourcegraph 7.0 (Feb 2026) repositioned the product as a shared intelligence layer for developers and AI agents \[[1][1]\]. GitLab Orbit went GA on 29 Oct 2026 \[[2][2]\]. Moderne now calls itself "the Agent Tools company" \[[3][3]\].
- **MCP is the delivery channel.** Orbit exposes `query_graph` and `get_graph_schema` \[[4][4]\], Sourcegraph serves search, navigation and Deep Search over MCP \[[5][5]\], and Moderne ships its LST engine and Moddy agent over MCP \[[6][6]\].
- **Open-source local graphs exploded.** CodeGraph, created in Jan 2026, has 77,889 stars \[[7][7]\], and codebase-memory-mcp, created in Feb 2026, has 48,789 \[[8][8]\].
- **SCIP became a shared standard.** SCIP moved to open governance in March 2026 with a steering committee that includes engineers from Meta and Uber \[[9][9]\].

**What the evidence says**

- **Graphs help on multi-hop questions.** In KGCompass, 89.7% of the bugs it localized had no location hint in the issue and were found only through multi-hop graph traversal \[[10][10]\].
- **Agents often ignore the graph.** In CodeCompass, 58% of trials with graph access skipped the graph tool despite explicit instructions \[[11][11]\].
- **Graph grounding costs more per call.** In Compare the Market's test, the Orbit-grounded reviewer cost $2.37 per merge request versus $0.58 for diff-only review \[[12][12]\].

**Shortlist at a glance (Assessment)**

| Need | Lead pick | Alternative |
| --- | --- | --- |
| Code graph corpus for a context service | Sourcegraph (any code host) or GitLab Orbit (GitLab-native) | codebase-memory-mcp (local, MIT) |
| SDLC knowledge graph (MRs, pipelines, deployments) | GitLab Orbit | Potpie (open source) |
| Toil reduction campaigns | Moderne + OpenRewrite | Sourcegraph Batch Changes |
| Automated MR review context | GitLab Orbit on GitLab | Greptile or CodeRabbit (built-in graphs); code-review-graph (open source) |
| Security semantics | GitHub CodeQL | Joern (open source CPG) |

---

## 2. Key terms

- **Code graph:** nodes for files and symbols, edges for calls, imports and definitions. Orbit, for example, indexes files, directories, definitions, imports and calls \[[13][13]\].
- **SCIP:** a language-agnostic protocol for indexing source code that powers go-to-definition and find-references \[[14][14]\].
- **Code property graph (CPG):** a graph for mining large codebases for programming patterns, queried with a Scala-based DSL \[[15][15]\]. It merges a syntax tree, a control-flow graph and a program-dependence graph \[[16][16]\].
- **Lossless Semantic Tree (LST):** OpenRewrite's code tree that keeps whitespace, so it can print back the original source without reformatting \[[17][17]\]. It is type-attributed \[[18][18]\].
- **Context graph (SDLC graph):** a code graph joined with lifecycle data. Orbit maps code, work items, pipelines, deployments and production signals into one graph \[[19][19]\]. Graphiti's context graphs also record when each fact became true and when it was superseded \[[20][20]\].
- **MCP:** the Model Context Protocol, which every shortlisted tool uses to serve agents \[[4][4], [6][6], [7][7], [21][21]\].

---

## 3. Landscape

### 3.1 Industry vendors

| Vendor | Category | Graph and technology | Agent interface | Deployment and license | Traction signal |
| --- | --- | --- | --- | --- | --- |
| **Sourcegraph** | Code intelligence platform | Search index across all repos plus optional SCIP precise graph \[[5][5]\] | MCP server (Enterprise) \[[21][21]\] | Dedicated Cloud or Self Hosted, $59/user/month list \[[22][22]\] | SCIP repo 890 stars \[[14][14]\] |
| **GitLab Orbit** | SDLC context graph | Rust service; ClickHouse hosted, DuckDB local \[[23][23]\] | MCP, REST, CLI, Duo Agent Platform \[[23][23]\] | GitLab EE license \[[23][23]\]; Premium and Ultimate \[[2][2]\] | 1,500+ developers built on it at Transcend \[[24][24]\] |
| **Moderne** | Transformation engine | OpenRewrite LST plus recipes \[[25][25]\] | MCP, CLI, IDE plugins, Moddy \[[6][6]\] | SaaS tenant on Azure \[[26][26]\]; OpenRewrite Apache-2.0 \[[27][27]\] | Five top North American banks are customers (vendor-reported) \[[28][28]\] |
| **GitHub CodeQL** | Semantic analysis database | Queries a codebase as if it were data \[[29][29]\] | Code scanning, Copilot code review, Autofix \[[30][30]\] | Private code needs GitHub Advanced Security \[[31][31]\] | github/codeql 10,377 stars \[[32][32]\] |
| **Greptile** | Review bot with graph | Graph of functions, classes, imports and dependencies \[[33][33]\] | PR and MR reviewer on GitHub and GitLab, incl. self-managed \[[34][34]\] | Commercial, 14-day trial \[[35][35]\]; self-hosting options \[[36][36]\] | 22,000+ teams (vendor-reported) \[[37][37]\] |
| **CodeRabbit** | Review bot with graph | Symbol definitions and references plus files that change together \[[38][38]\] | PR reviewer and chat \[[38][38]\] | Not covered here | Not measured here |
| **Augment Code** | Semantic context engine | Semantic retrieval, which Sourcegraph calls approximate \[[5][5]\] | Context Engine MCP, SDK, Context Connectors \[[39][39]\] | Not covered here | 70%+ agent improvement in its own benchmarks (vendor-reported) \[[40][40]\] |
| **Gitar (Sonar)** | Review and CI verification agent | Consumes context (org instructions, Jira, Slack); not a graph vendor \[[41][41]\] | Reviews, diagnoses CI failures, applies fixes \[[41][41]\] | Joined Sonar in May 2026 \[[42][42]\] | Not measured here |
| **Harness (Qwiet AI)** | CPG-based security | Code property graph for reachability analysis \[[43][43]\] | Embedded in Harness application security \[[43][43]\] | Acquired by Harness, Sep 2025 \[[43][43]\] | Not measured here |

### 3.2 Open-source tools

| Tool | What it is | Technology | License | Stars | Forks |
| --- | --- | --- | --- | --- | --- |
| **Graphify** | Multimodal knowledge graph skill for Claude Code \[[44][44]\] | tree-sitter plus Claude extraction; NetworkX and Leiden \[[44][44]\] | Apache-2.0 \[[44][44]\] | 149,689 \[[44][44]\] | 14,381 \[[44][44]\] |
| **CodeGraph** | Local code graph over MCP \[[7][7]\] | Rust parsing kernel; SQLite with FTS5 \[[7][7]\] | MIT \[[7][7]\] | 77,889 \[[7][7]\] | 5,199 \[[7][7]\] |
| **codebase-memory-mcp** | Local code, docs and infra graph over MCP \[[8][8]\] | Native C; tree-sitter grammars; hybrid LSP \[[8][8]\] | MIT \[[8][8]\] | 48,789 \[[8][8]\] | 4,050 \[[8][8]\] |
| **GitNexus** | Code graph with impact tools and web UI \[[45][45]\] | tree-sitter; LadybugDB (formerly KuzuDB) \[[45][45]\] | PolyForm Noncommercial \[[45][45]\] | 48,620 \[[45][45]\] | 5,263 \[[45][45]\] |
| **Graphiti** | Temporal context graph framework \[[20][20]\] | Facts with validity windows and provenance \[[20][20]\] | Apache-2.0 \[[20][20]\] | 32,898 \[[20][20]\] | 3,386 \[[20][20]\] |
| **code-review-graph** | Local graph for review context \[[46][46]\] | tree-sitter; one SQLite file \[[46][46]\] | MIT \[[46][46]\] | 32,827 \[[46][46]\] | 2,987 \[[46][46]\] |
| **Serena** | Symbol-level retrieval and editing over MCP \[[47][47]\] | IDE-style semantic tools \[[47][47]\] | See repo \[[47][47]\] | 31,485 \[[47][47]\] | 2,145 \[[47][47]\] |
| **Potpie** | SDLC context graph for agents \[[48][48]\] | Indexes code, decisions, history and team knowledge \[[48][48]\] | Apache-2.0 \[[48][48]\] | 5,800 \[[48][48]\] | 697 \[[48][48]\] |
| **code-graph-rag** | Graph RAG for monorepos \[[49][49]\] | tree-sitter; embedded graph DB; natural language to Cypher \[[49][49]\] | MIT \[[49][49]\] | 5,381 \[[49][49]\] | 719 \[[49][49]\] |
| **CodeGraphContext** | Graph-DB-backed MCP server and CLI \[[50][50]\] | Neo4j, KuzuDB or FalkorDB backends \[[50][50]\] | MIT \[[50][50]\] | 4,433 \[[50][50]\] | 852 \[[50][50]\] |
| **Sourcebot** | Self-hosted code search with MCP \[[51][51]\] | Search plus symbol definitions and references \[[51][51]\] | MIT \[[51][51]\] | 4,034 \[[51][51]\] | 385 \[[51][51]\] |
| **OpenRewrite** | Refactoring engine behind Moderne \[[52][52]\] | Lossless Semantic Tree and recipes \[[25][25]\] | Apache-2.0 \[[27][27]\] | 3,992 \[[27][27]\] | 608 \[[27][27]\] |
| **Joern** | Code property graph analysis platform \[[53][53]\] | CPG in a custom graph DB; Scala DSL \[[53][53]\] | Apache-2.0 \[[53][53]\] | 3,650 \[[53][53]\] | 476 \[[53][53]\] |
| **Auryn (FalkorDB)** | Code graph in FalkorDB over MCP \[[54][54]\] | FalkorDB graph database \[[54][54]\] | MIT \[[54][54]\] | 385 \[[54][54]\] | 56 \[[54][54]\] |

### 3.3 Building blocks

| Component | Role | Stars |
| --- | --- | --- |
| **tree-sitter** | Parser used by CodeGraph, GitNexus and code-review-graph, among others \[[7][7], [45][45], [46][46]\] | 27,498 \[[55][55]\] |
| **Kythe** (Google) | Pluggable, mostly language-agnostic ecosystem for code tools \[[56][56]\]; Google's migration tooling uses it to follow references \[[57][57]\] | 2,171 \[[58][58]\] |
| **Glean** (Meta) | Fact store for code in RocksDB, queried with the Datalog-like Angle language \[[59][59]\] | 1,445 \[[60][60]\] |
| **SCIP** | Open code indexing protocol with Go and Rust bindings \[[14][14]\] | 890 \[[14][14]\] |
| **stack-graphs** (GitHub) | GitHub library, repository now archived \[[61][61]\] | 877 \[[61][61]\] |

### 3.4 Common usage patterns

1. **Local stdio MCP server beside the agent.** CodeGraph, codebase-memory-mcp and Orbit Local all run on the developer's machine \[[7][7], [8][8], [23][23]\].
2. **Shared remote MCP endpoint over an org-wide index.** Sourcegraph serves `/.api/mcp` from its instance \[[21][21]\]; Orbit Remote spans a top-level GitLab.com group \[[23][23]\].
3. **Index in CI.** Sourcegraph recommends running SCIP indexing in CI for complex builds \[[62][62]\]. Compare the Market ran Orbit as a sidecar that re-indexed on each MR pipeline \[[12][12]\].
4. **Review bot with a private graph.** Greptile builds a graph at sign-up and queries it on every review \[[63][63]\].
5. **Campaign engine.** Sourcegraph Batch Changes opens and tracks PRs across many repos \[[64][64]\]; Moderne runs recipes across thousands of repos \[[65][65]\].
6. **Push context with hooks and skills.** GitNexus registers Claude Code hooks and writes `AGENTS.md` and `CLAUDE.md` files \[[45][45]\]; codebase-memory-mcp installs skills, agent profiles and hooks \[[8][8]\].

---

## 4. Shortlist deep dives

Four industry vendors and four open-source tools, picked for fit with the four use cases and for traction.

### 4.1 Sourcegraph (industry)

**What it is:** a code understanding platform that 7.0 repositioned as a shared intelligence layer for developers and agents \[[1][1]\].

**Features**

- Indexes every repository, branch, tag and revision across GitHub, GitLab, Bitbucket, Gerrit, Perforce and Azure DevOps \[[5][5]\].
- Structural, semantic and regex search, plus commit, diff and blame history \[[5][5]\].
- Cross-repo go-to-definition and find-references out of the box \[[5][5]\].
- **Deep Search:** agentic natural-language exploration on the same index \[[5][5]\]. 7.0 improved its accuracy, added image support and embedded code navigation \[[1][1]\].
- **Batch Changes:** creates PRs on every affected repo and tracks them until merged \[[64][64]\]. Agentic Batch Changes adds AI-generated, reviewable changes across thousands of repos \[[5][5]\].

**Technology**

- Precise navigation uses per-language SCIP indexes uploaded to the instance \[[62][62]\], with search-based navigation as the fallback \[[66][66]\].
- SCIP is optional, and Sourcegraph says search, navigation, Deep Search and MCP work without it \[[5][5]\].

**Usage patterns**

- Agents connect to `/.api/mcp`, with `/.api/mcp/all` and `/.api/mcp/deepsearch` as alternate tool suites \[[21][21]\].
- Authentication is OAuth 2.0 (including Dynamic Client Registration) or access tokens \[[21][21]\].
- Campaigns are YAML batch specs naming target repos, commands and changeset templates \[[64][64]\].

**Deployment and price**

- Enterprise Dedicated Cloud is the default and Enterprise Self Hosted is on request, both listed at $59 per user per month \[[22][22]\].
- Self-hosting runs on Kubernetes with Helm (recommended) or Docker Compose \[[67][67]\].

**Watch-outs**

- MCP server is an Enterprise plan feature \[[21][21]\].
- Precise data needs a working indexer per language, and Sourcegraph recommends CI indexing for authenticated builds \[[62][62]\].
- **Assessment:** the fetched pages describe code and version history, not pipelines, deployments or vulnerabilities, so SDLC context would come from elsewhere.

### 4.2 GitLab Orbit (industry)

**What it is:** formerly the GitLab Knowledge Graph, a Rust service that builds a property graph from SDLC metadata and code, queried with a JSON Cypher-like DSL compiled to ClickHouse SQL \[[68][68]\]. GA on 29 Oct 2026 \[[2][2]\].

**Features**

- Indexes default-branch code (files, directories, definitions, imports, calls) plus merge requests, pipelines, vulnerabilities and branches \[[13][13]\].
- Code languages: Ruby, Java, Kotlin, Python, TypeScript, JavaScript, Rust, Go, C#, C, C++, PHP, Bash and Elixir \[[23][23]\].
- Hosted DSL supports aggregations, traversals, neighbors and pathfinding \[[23][23]\].
- File content is resolved at query time, so agents can read code without a second API call \[[69][69]\].

**Technology**

- **Orbit Remote:** `gkg-server` on ClickHouse, fed by change data capture through GitLab's Data Insights Platform \[[23][23]\].
- **Orbit Local:** a single-binary `orbit` CLI on DuckDB with a stdio MCP server \[[23][23]\].

**Usage patterns**

- Agents connect through MCP or `glab orbit setup`; named clients include Claude Code, Codex, Cursor, OpenCode, Gemini CLI and Antigravity \[[2][2]\].
- Native in Duo Agent Platform, REST for custom agents, and Data Explorer for engineers \[[2][2]\].
- REST endpoints: `/api/v4/orbit/query`, `/schema`, `/status` and `/tools` \[[70][70]\].

**Pricing and availability**

- Premium and Ultimate. GitLab.com first; Self-Managed and Dedicated follow in the coming weeks \[[2][2]\].
- Query packs of $30 in GitLab Credits per user per month add 1,000 queries to an org-wide pool; overage is about $0.03 per query \[[2][2]\].
- `get_graph_schema` calls are free, while queries consume credits \[[71][71]\].

**Scale and claims (vendor-reported)**

- More than 1.5 million projects and 8 TB of graph data indexed in under 2 hours \[[2][2]\].
- Up to 11x faster responses and 4.5x fewer tokens \[[19][19]\]; up to 45x fewer retries \[[2][2]\].

**Watch-outs**

- Only the default branch is indexed \[[13][13]\].
- License is the GitLab Enterprise Edition license, not open source \[[23][23]\].
- Some MCP clients truncate the long `query_graph` description, so models miss the DSL grammar \[[72][72]\].
- In the pre-GA Compare the Market test, latency was 80.6 s versus about 44 s for diff-only review \[[12][12]\].

### 4.3 Moderne and OpenRewrite (industry with open-source core)

**What it is:** OpenRewrite is an open-source semantic analysis and refactoring project \[[52][52]\]; Moderne adds tooling to run its recipes against thousands of repositories at once \[[65][65]\].

**Features**

- Recipes search and transform code represented as LSTs \[[25][25]\].
- **Moddy:** a multi-repo AI agent, in restricted beta, that runs across thousands of repositories \[[73][73]\].
- **Prethink (launched 10 Feb 2026 \[[74][74]\]):** pre-resolved context for agents on service endpoints, database connections, external calls, messaging patterns and test coverage \[[75][75]\]. It can also emit an optional knowledge graph and FINOS CALM architecture diagrams \[[76][76]\].
- **Changelog (May 2026):** shows what is ready, blocked or waiting across a changeset, through MCP and GraphQL \[[3][3]\].
- **Trigrep:** symbol-aware code search for agents \[[3][3]\].

**Technology**

- Run locally, the LST must fit in memory \[[17][17]\]. Moderne serializes LSTs as a build byproduct and edits them in bulk later \[[65][65]\].
- Python support was added in Feb 2026 \[[77][77]\].

**Usage patterns**

- Delivered as the LST engine, recipe catalog, CLI, IDE plugins and Moddy, over MCP to coding agents \[[6][6]\].
- Positioning: the agent plans while Moderne's deterministic tools execute \[[6][6]\].
- Moddy Desktop runs an MCP server at `localhost:4848/mcp` \[[78][78]\].

**Traction**

- $30M Series B (Feb 2025) with Morgan Stanley, Amex Ventures and TIAA Ventures participating \[[79][79]\].
- OpenRewrite is integrated into Amazon Q and Broadcom App Advisor \[[79][79]\].

**Watch-outs**

- Moddy is still restricted beta \[[73][73]\].
- **Assessment:** strongest on JVM ecosystems; check recipe coverage for each language and framework you plan to migrate.

### 4.4 GitHub CodeQL (industry)

**What it is:** GitHub's semantic code analysis engine, which queries a codebase as though it were data \[[29][29]\].

**Features**

- **Copilot Autofix** suggests fixes for CodeQL alerts. It is on by default for repos using CodeQL and needs no Copilot subscription \[[80][80]\].
- Autofix runs on pull requests and on the default branch \[[81][81]\].
- **Copilot code review** now blends LLM detection and tool calling with CodeQL and ESLint \[[82][82]\]. CodeQL is on by default; ESLint and PMD are off \[[30][30]\].
- Data-flow libraries can be extended with sources and sinks for extra frameworks \[[83][83]\].

**Technology and languages**

- Supports C/C++, C#, Go, Java/Kotlin, JavaScript/TypeScript and more; it does not support PHP or Scala \[[84][84]\].
- Standard queries are open source in github/codeql \[[32][32]\].

**Usage patterns**

- Default setup picks languages, query suite and trigger events automatically \[[84][84]\].
- Code scanning runs on public repos, and on org repos with GitHub Code Security enabled \[[85][85]\].

**Watch-outs**

- Without GitHub Advanced Security, the CodeQL CLI may only be used on open-source codebases \[[31][31]\].
- **Assessment:** CodeQL is a deep analysis database, not a general MCP-queryable code graph; it fits review and security, less so agent navigation on GitLab-hosted code.

### 4.5 CodeGraph (open source)

**What it is:** a pre-built graph of every symbol, call edge and dependency, so an agent gets the code it needs in one call \[[7][7]\].

- **Tech:** Rust parsing kernel for 20 languages; local SQLite with FTS5; no data leaves the machine \[[7][7]\].
- **Interface:** one default MCP tool, `codegraph_explore`, with narrower tools available but unlisted \[[7][7]\].
- **Freshness:** watches the project and updates the graph on every file change \[[7][7]\].
- **Benchmark (vendor-reported):** across 7 repos on Claude Opus 4.8, 88% fewer tool calls, 53% faster, 62% fewer tokens and 44% cheaper \[[7][7]\].
- **Honest caveat:** multi-turn sessions keep about 80% more retrieval context resident in the window \[[7][7]\].
- **Roadmap:** a hosted PR platform is announced as coming \[[7][7]\].

### 4.6 codebase-memory-mcp (open source)

**What it is:** a persistent local knowledge graph that connects code, documentation, configuration and infrastructure \[[8][8]\].

- **Tech:** native C backend with 17 MCP tools, vendored grammars and hybrid LSP type resolution \[[8][8]\]; the preprint stores the graph in SQLite and uses Louvain community detection \[[86][86]\].
- **Beyond code:** traces Docker, Kubernetes, Helm, Terraform, Ansible and CI configuration \[[8][8]\].
- **Scale:** the Linux kernel (28M lines) fully indexes in 3 minutes into 4.81M nodes and 7.72M edges on an Apple M3 Pro \[[8][8]\].
- **Results (authors' own):** 10x lower token use and 2.1x fewer tool calls than file-by-file exploration across 31 repos \[[8][8]\].
- **Supply chain:** publishes OpenSSF Scorecard and SLSA 3 badges \[[8][8]\].

### 4.7 GitNexus (open source, non-commercial license)

**What it is:** a code graph of symbols, calls, dependencies and execution flows, used through MCP, a CLI or a web explorer \[[45][45]\].

- **Tools:** `query`, `context`, `impact`, `trace`, `detect_changes` and `rename` \[[45][45]\].
- **Languages:** 18 providers, including COBOL \[[45][45]\].
- **Tech:** tree-sitter parsing and LadybugDB, an embedded graph database with vector support \[[45][45]\].
- **Multi-agent:** one shared HTTP MCP server can serve several concurrent agents \[[45][45]\].
- **Watch-outs:** PolyForm Noncommercial license; commercial use, PR blast-radius review and unified multi-repo graphs sit in the paid enterprise offering \[[45][45]\].

### 4.8 Joern (open source)

**What it is:** a platform that turns source, bytecode and binaries into code property graphs for vulnerability discovery and static analysis research \[[53][53]\].

- **Tech:** CPGs stored in a custom graph database and mined with a Scala DSL \[[53][53]\]; v4.0.0 moved from overflowdb to flatgraph \[[53][53]\].
- **Origin:** introduced for vulnerability discovery in C system code and the Linux kernel \[[15][15]\].
- **Stewardship:** Harness acquired Qwiet AI (formerly ShiftLeft) in Sep 2025, and CPG creator Fabian Yamaguchi is now at Harness \[[43][43]\].
- **Watch-out:** Harness's own docs call the CPG learning curve steep \[[87][87]\].

---

## 5. Side-by-side comparison

| | Graph scope | Precision | Multi-repo | Writes code | Self-host | License | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Sourcegraph** | Code plus commit, diff, blame history | Compiler-grade with SCIP, search-based otherwise | Yes, six code hosts | Batch Changes | Yes, on request | Commercial, $59/user/month list | \[[5][5], [22][22], [64][64]\] |
| **GitLab Orbit** | Code plus MRs, pipelines, vulnerabilities | AST-based code graph | Top-level GitLab.com group | No (read-only API) | Coming after GA | GitLab EE | \[[2][2], [12][12], [13][13], [23][23], [88][88]\] |
| **Moderne** | Type-attributed code model | Compiler-accurate LST | Thousands of repos | Recipes, Moddy | SaaS tenant | OpenRewrite Apache-2.0 | \[[18][18], [26][26], [27][27], [65][65], [89][89]\] |
| **CodeQL** | Code database with data flow | Semantic analysis | Per repository (Assessment) | Autofix suggestions | GitHub Enterprise Server | Restricted CLI terms | \[[29][29], [31][31], [80][80], [83][83], [84][84]\] |
| **CodeGraph** | Symbols, calls, dependencies | tree-sitter plus cross-file resolution | Other indexed projects by path | No | Local only | MIT | \[[7][7]\] |
| **codebase-memory-mcp** | Code, docs, config, infra | tree-sitter plus hybrid LSP | Calls across services | No | Local only | MIT | \[[8][8]\] |
| **GitNexus** | Symbols, calls, flows | Varies by language | Enterprise edition | Semantic rename | Local; paid self-hosted | PolyForm NC | \[[45][45]\] |
| **Joern** | AST, control flow, data dependence | Semantic CPG | Per project (Assessment) | No | Local | Apache-2.0 | \[[16][16], [53][53]\] |

---

## 6. Use cases

### 6.1 Generative agents (AI coding agents)

**The gap:** coding agents rebuild context from scratch on every task with grep, glob and file reads \[[5][5]\].

1. **Answer codebase questions with fewer calls.** CodeGraph cut tool calls by 88% in its own benchmark \[[7][7]\]; codebase-memory-mcp reports 10x lower token use \[[8][8]\]. Fits: CodeGraph, codebase-memory-mcp, Sourcegraph MCP.
2. **Localize and repair issues.** RepoGraph improved all four SWE-bench systems it was plugged into (ICLR 2025) \[[90][90]\]. KGCompass reached 58.3% on SWE-bench Lite at about $0.2 per repair \[[10][10]\].
3. **Find hidden dependencies before editing.** CodeCompass reached 99.4% on hidden-dependency tasks versus 76.2% for a vanilla agent \[[91][91]\].
4. **Refuse to invent missing code.** A Transcend hackathon team's agent checks Orbit and asks for the real location when it cannot find a service \[[24][24]\].
5. **Edit in dependency order.** The runner-up hackathon project maps every affected file and edits them in dependency order \[[24][24]\].
6. **Ground answers in architecture facts.** Moderne Prethink gives agents verified service endpoints and dependencies instead of making them infer architecture \[[75][75]\].

**Watch-out:** the graph only helps if it is called. When CodeCompass's tool was used, coverage hit 99.5%; when skipped, 80.2% \[[11][11]\]. **Assessment:** deliver context through hooks or skills, not prompts alone.

### 6.2 Toil reduction campaigns

**Definition:** Software Engineering at Google defines a large-scale change as logically related changes that cannot be submitted as one atomic unit \[[92][92]\].

1. **Build the impact set before changing anything.** Google's migration tooling follows Kythe references up to five hops from a field, then an LLM fills the accuracy gaps \[[57][57]\]. Across 39 migrations the LLM generated 74.45% of code changes, and developers estimated a 50% time saving \[[57][57]\].
2. **Run deterministic framework and dependency upgrades.** OpenRewrite recipes transform LSTs, and Moderne runs them across thousands of repos \[[65][65]\].
3. **Open, track and merge fleet PRs.** Batch Changes tracks every changeset until merged \[[64][64]\]. At Spotify, Fleetshift handles target selection, scheduling and tracking while the Honk agent edits code, and Fleet Management has merged more than 2.5 million automated PRs \[[93][93]\].
4. **Remove dead code and stale flags.** Uber's Piranha has removed around two thousand stale feature flags and their code \[[94][94]\]. Meta uses Glean to find unused C++ includes and automate cleanup \[[59][59]\].
5. **See what is blocked.** Moderne Changelog exposes ready, blocked and waiting work to agents through MCP \[[3][3]\]; Meta tracks API migration progress with Glean \[[59][59]\].
6. **Feed LLM migrations rich context.** Airbnb's prompts included sibling tests, imports and component source \[[95][95]\]. It migrated nearly 3.5K test files in 6 weeks \[[95][95]\] against a 1.5-year manual estimate \[[96][96]\].

**Scale context:** around half of Spotify's pull requests have been automated since mid-2024 \[[97][97]\].

### 6.3 Automated code review tooling

1. **Show the blast radius beyond the diff.** Greptile queries its graph for a changed function's dependencies and usage \[[63][63]\]. code-review-graph reports reachable callers, dependents and tests with a risk score \[[46][46]\].
2. **Pull cross-file definitions into the review.** CodeRabbit maps definitions and references and finds files that often change together \[[38][38]\].
3. **Ground GitLab MR review in the SDLC graph.** Compare the Market's Orbit-grounded reviewer matched about 70% of expected inline comments versus about 58% for RAG, which did worse than no added context \[[2][2]\].
4. **Mix deterministic findings into AI review.** Copilot code review combines LLM analysis with CodeQL and ESLint \[[82][82]\].
5. **Select tests a change can reach.** A hackathon team used Orbit's whole-codebase call graph to find the tests a change can reach \[[24][24]\]. Meta uses Glean for test selection \[[59][59]\].
6. **Cut noise with reachability.** Harness uses Qwiet's reachability analysis to cut noise and prioritize real risk \[[43][43]\].
7. **Index diffs for review tooling.** Meta indexes diffs into "diff sketches" that drive lint rules and notifications \[[59][59]\].

**Watch-out:** Compare the Market scored alignment with a golden set using an LLM judge on 79 MRs, which the authors call directional \[[12][12]\].

### 6.4 Knowledge graphs

1. **SDLC context graph.** Orbit links merge requests, pipelines and vulnerabilities to projects and code \[[13][13]\]; engineers use it to trace changes and investigate incidents \[[98][98]\].
2. **Incident and reliability forensics.** A financial services company traced a build-system outage to a CI job failing half the time \[[2][2]\].
3. **Code, docs and infrastructure in one graph.** codebase-memory-mcp links docs, architecture decisions and Terraform or Kubernetes config to code \[[8][8]\].
4. **Architecture knowledge as data.** Prethink emits FINOS CALM diagrams and an optional knowledge graph \[[76][76]\].
5. **Decisions and team knowledge.** Potpie indexes decisions, source history, team knowledge and workflows \[[48][48]\].
6. **Facts that change over time.** Graphiti gives each fact a validity window and traces it back to source episodes \[[20][20]\].
7. **Org-wide code fact store.** Meta's Glean serves code navigation, search, docs and RAG for AI coding assistants \[[59][59]\].
8. **Mixed corpora.** Graphify merges code, PDFs and images, and tags each edge as extracted, inferred or ambiguous \[[44][44]\].

---

## 7. Evidence quality

- **Mostly vendor numbers.** Orbit, CodeGraph, Augment and codebase-memory-mcp all publish their own benchmarks \[[2][2], [7][7], [8][8], [40][40]\].
- **One public customer A/B test.** Compare the Market compared baseline, Orbit, RAG and Orbit plus RAG on 79 real MRs \[[12][12]\].
- **Small corpora show little gain.** Graphify's reduction was about 1x on a 6-file corpus versus 71.5x on 52 files \[[44][44]\].
- **Assessment:** star counts track attention. Graphify passed 149k stars within about seven and a half months of its April 2026 creation \[[44][44]\], so treat stars as a weak proxy for production use.

---

## 8. Decision guide (Assessment)

**Evaluation criteria**

- **Precision:** compiler-grade (SCIP, LST, CodeQL) versus tree-sitter heuristics.
- **Scope:** code only, or code plus MRs, pipelines and deployments.
- **Freshness:** per-commit or per-file-save updates versus scheduled re-indexing.
- **Access control:** permission-aware results across repos.
- **Agent ergonomics:** tool count and description size, since clients truncate long descriptions \[[72][72]\].
- **Deployment and license:** self-hosting timing and commercial terms.
- **Cost per query:** graph calls add latency and spend \[[12][12]\].

**Recommended path**

1. **Fix the eval harness first.** Reuse Compare the Market's four-arm design: no context, graph, RAG and both, on real MRs \[[12][12]\].
2. **Pick the corpus layer.** If code lives on GitLab, trial Orbit Remote; if it spans hosts, trial Sourcegraph. Keep codebase-memory-mcp or CodeGraph as the local, MIT-licensed baseline.
3. **Pick the campaign layer.** Pilot Moderne on one JVM migration and measure merged PRs and blocked changes.
4. **Check licenses early.** GitNexus is noncommercial \[[45][45]\], CodeQL CLI terms restrict private code \[[31][31]\], and Orbit uses the GitLab EE license \[[23][23]\].
5. **Confirm self-host dates.** Orbit Self-Managed and Dedicated follow GA \[[2][2]\]; Sourcegraph Self Hosted is on request \[[22][22]\].

**Next actions**

- [ ] Ask GitLab for the Orbit Self-Managed date and RBAC model.
- [ ] Run the four-arm MR review eval on 50 to 100 internal MRs.
- [ ] Shortlist one campaign (for example a Java or Spring upgrade) for a Moderne pilot.
- [ ] Index two or three large repos locally with codebase-memory-mcp and CodeGraph as a free baseline.

---

## Sources

1. [Sourcegraph blog: A new era for Sourcegraph, Sourcegraph 7.0 (25 Feb 2026)](https://sourcegraph.com/blog/a-new-era-for-sourcegraph-the-intelligence-layer-for-ai-coding-agents-and-developers)
2. [GitLab blog: GitLab Orbit is generally available (29 Oct 2026)](https://about.gitlab.com/blog/gitlab-orbit-ga/)
3. [Business Wire: Moderne Changelog (19 May 2026)](https://www.businesswire.com/news/home/20260519919718/en/)
4. [GitLab: GitLab Orbit product page](https://about.gitlab.com/gitlab-orbit/)
5. [Sourcegraph: AI coding context tools compared](https://sourcegraph.com/resources/context-compare)
6. [AWS Marketplace: Moderne listing](https://aws.amazon.com/marketplace/pp/prodview-qa5qb3cy3ofbc)
7. [GitHub: colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)
8. [GitHub: DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)
9. [Sourcegraph blog: The future of SCIP (25 Mar 2026)](https://sourcegraph.com/blog/the-future-of-scip)
10. [arXiv 2503.21710v2: KGCompass, Knowledge Graph Enhanced Repository-Level Software Repair](https://arxiv.org/pdf/2503.21710v2)
11. [arXiv 2602.20048: CodeCompass, the Navigation Paradox (HTML v1)](https://arxiv.org/html/2602.20048v1)
12. [Compare the Market: Comparing Context Retrieval Approaches for AI Code Review](https://comparethemarketcareers.com/blog/comparing-context-retrieval-approaches-for-ai-code-review/)
13. [GitLab Docs: GitLab Orbit indexed data (schema)](https://docs.gitlab.com/orbit/schema/)
14. [GitHub: scip-code/scip](https://github.com/scip-code/scip)
15. [Joern Docs: Code Property Graph](https://docs.joern.io/code-property-graph/)
16. [Qwiet AI: The semantic code property graph](https://qwiet.ai/?p=9049)
17. [OpenRewrite Docs: Lossless Semantic Trees](https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees.md)
18. [Moderne Docs: Lossless semantic trees (platform reference)](https://docs.moderne.io/administrator-documentation/moderne-platform/references/lossless-semantic-trees)
19. [GitLab press release: new capabilities at Transcend (10 Jun 2026)](https://about.gitlab.com/press/releases/2026-06-10-gitlab-announces-new-capabilities-to-give-enterprises-speed-control-at-agentic-scale/)
20. [GitHub: getzep/graphiti](https://github.com/getzep/graphiti)
21. [Sourcegraph Docs: Sourcegraph MCP Server (7.5)](https://7.5.sourcegraph.com/api/mcp.md)
22. [Sourcegraph Docs: Enterprise plan](https://sourcegraph.com/docs/pricing/enterprise)
23. [GitLab Orbit (Knowledge Graph) README, GitHub mirror](https://github.com/gitlabhq/orbit-knowledge-graph)
24. [GitLab blog: Transcend hackathon, what developers built with Orbit (20 Jul 2026)](https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/)
25. [ICSME 2023 tool demo: Deterministic Automatic Refactoring at Scale (OpenRewrite)](https://conf.researchr.org/details/icsme-2023/icsme-2023-tool-demo-track/7/Deterministic-Automatic-Refactoring-at-Scale)
26. [GlobeNewswire via Manila Times: Moderne joins Microsoft Pegasus program (15 Apr 2025)](https://manilatimes.net/2025/04/15/tmt-newswire/globenewswire/moderne-joins-microsoft-pegasus-program-to-accelerate-large-scale-code-modernization-for-enterprises/2092757)
27. [GitHub: openrewrite/rewrite](https://github.com/openrewrite/rewrite)
28. [Intel Capital: Moderne Series B announcement](https://www.intelcapital.com/?p=11696)
29. [GitHub blog: Fixing security vulnerabilities with AI](https://github.blog/2024/02/14/fixing-security-vulnerabilities-with-ai/)
30. [GitHub Docs: About GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review)
31. [GitHub Security Lab: GitHub CodeQL Terms and Conditions](https://securitylab.github.com/tools/codeql/license)
32. [GitHub: github/codeql](https://github.com/github/codeql)
33. [Greptile Docs: Key features](https://www.greptile.com/docs/code-review/key-features)
34. [Greptile Docs: Introduction (platforms)](https://www.greptile.com/docs/introduction.md)
35. [Greptile: Code context](https://www.greptile.com/code-context)
36. [Greptile Docs: product overview (enterprise readiness)](https://www.greptile.com/docs/api-reference/zapier)
37. [Greptile homepage](https://www.greptile.com)
38. [CodeRabbit Docs: Code Graph Analysis](https://docs.coderabbit.ai/integrations/code-graph-analysis)
39. [Augment Docs: Context Services overview](https://docs.augmentcode.com/context-services/overview)
40. [Augment Code changelog: Context Engine MCP for any AI coding agent (6 Feb 2026)](https://www.augmentcode.com/changelog/context-engine-mcp-in-ga)
41. [Sonar: Gitar product page](https://www.sonarsource.com/products/gitar/)
42. [Sonar: Get started with Gitar](https://www.sonarsource.com/developers/blueprints/get-started-with-gitar/)
43. [Harness blog: Harness acquires Qwiet AI (29 Sep 2025)](https://harness.io/blog/harness-acquires-qwiet-ai)
44. [GitHub: Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)
45. [GitHub: abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus)
46. [GitHub: tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph)
47. [GitHub: oraios/serena](https://github.com/oraios/serena)
48. [GitHub: potpie-ai/potpie](https://github.com/potpie-ai/potpie)
49. [GitHub: vitali87/code-graph-rag](https://github.com/vitali87/code-graph-rag)
50. [GitHub: CodeGraphContext/CodeGraphContext](https://github.com/CodeGraphContext/CodeGraphContext)
51. [GitHub: sourcebot-dev/sourcebot](https://github.com/sourcebot-dev/sourcebot)
52. [Moderne blog: Overview of OpenRewrite and Moderne](https://moderne.io/blog/overview-of-openrewrite-and-moderne)
53. [GitHub: joernio/joern](https://github.com/joernio/joern)
54. [GitHub: FalkorDB/Auryn (formerly FalkorDB/code-graph)](https://github.com/FalkorDB/Auryn)
55. [GitHub: tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter)
56. [Kythe project site](https://kythe.io/)
57. [arXiv 2504.09691: Google's use of LLMs for internal code migrations (FSE 2025 preprint)](https://arxiv.org/html/2504.09691v1)
58. [GitHub: kythe/kythe](https://github.com/kythe/kythe)
59. [Meta Engineering: Indexing code at scale with Glean (19 Dec 2024)](https://engineering.fb.com/2024/12/19/developer-tools/glean-open-source-code-indexing/)
60. [GitHub: facebookincubator/Glean](https://github.com/facebookincubator/Glean)
61. [GitHub: github/stack-graphs (archived)](https://github.com/github/stack-graphs)
62. [Sourcegraph Docs: Precise Code Navigation](https://sourcegraph.com/docs/code-navigation/precise-code-navigation)
63. [Greptile Docs: Graph-based codebase context](https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context)
64. [Sourcegraph Docs: Batch Changes](https://sourcegraph.com/docs/batch_changes)
65. [Moderne Docs: Lossless semantic trees (recipe authoring concepts)](https://docs.moderne.io/user-documentation/recipes/authoring-recipes/concepts/lossless-semantic-trees)
66. [Sourcegraph Docs: Precise code navigation explanation (search-based fallback)](https://sourcegraph.com/docs/code_navigation/explanations/precise_code_navigation)
67. [Sourcegraph Docs: Self-hosted deployment overview](https://sourcegraph.com/docs/self-hosted/deploy)
68. [GitLab Handbook: GitLab Orbit design document](https://handbook.gitlab.com/handbook/engineering/architecture/design-documents/orbit/)
69. [GitLab Docs: Orbit indexed data, properties resolved at query time](https://docs.gitlab.com/orbit/indexed-data/)
70. [GitLab Docs: Orbit REST API endpoints](https://docs.gitlab.com/orbit/remote/access/api/)
71. [GitLab blog: GitLab Orbit and Google Antigravity (25 Jun 2026)](https://about.gitlab.com/blog/gitlab-orbit-and-google-antigravity)
72. [GitLab issue 553: query_graph tool description truncated by MCP clients](https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/553)
73. [Moderne Docs: Getting started with Moddy](https://docs.moderne.io/user-documentation/moddy/moddy-platform)
74. [Business Wire: Moderne introduces Prethink (10 Feb 2026)](https://www.businesswire.com/news/home/20260210110758/en/Moderne-Introduces-Prethink-to-Give-AI-Agents-the-Structured-Knowledge-Theyve-Been-Missing)
75. [Moderne Docs: Moderne Prethink (agent tools)](https://docs.moderne.io/user-documentation/agent-tools/prethink)
76. [Moderne Docs: Prethink recipes](https://docs.moderne.io/user-documentation/recipes/prethink)
77. [Business Wire: Moderne expands Agent Tools platform with Python (19 Feb 2026)](https://www.businesswire.com/news/home/20260219393723/en/Moderne-Expands-Agent-Tools-Platform-with-Python)
78. [Moderne Docs: Moddy Desktop MCP tools reference](https://docs.moderne.io/user-documentation/moddy/mcp-tools-reference)
79. [App Developer Magazine: Moderne closes $30M Series B](https://appdevelopermagazine.com/automated-code-refactoring-platform-moderne/amp/)
80. [GitHub Docs: Responsible use of Copilot Autofix for code scanning](https://docs.github.com/en/enterprise-cloud@latest/code-security/responsible-use/responsible-use-autofix-code-scanning)
81. [GitHub Docs: Security and quality AI features](https://docs.github.com/en/enterprise-cloud%40latest/code-security/responsible-use/security-and-quality-ai-features)
82. [GitHub changelog: New public preview features in Copilot code review (28 Oct 2025)](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/)
83. [CodeQL Docs: Supported languages and frameworks](https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/)
84. [GitHub Docs: About code scanning with CodeQL (GHES 3.18)](https://docs.github.com/en/enterprise-server@3.18/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql)
85. [GitHub Docs: Code scanning with CodeQL (availability)](https://docs.github.com/en/enterprise-server@3.17/code-security/concepts/code-scanning/codeql/codeql-code-scanning)
86. [arXiv 2603.27277: Codebase-Memory, Tree-Sitter-Based Knowledge Graphs for LLM Code Exploration via MCP](https://arxiv.org/html/2603.27277)
87. [Harness Docs: Code Property Graph](https://developer.harness.io/ai-sca/core-concepts/code-property-graph)
88. [GitLab epic 19744: Orbit as a Service GA](https://gitlab.com/groups/gitlab-org/-/epics/19744)
89. [IT Brief UK: Moderne unveils Prethink (12 Feb 2026)](https://itbrief.co.uk/story/moderne-unveils-prethink-to-boost-ai-code-governance)
90. [arXiv 2410.14684: RepoGraph, Repository-level Code Graph (ICLR 2025)](https://arxiv.org/abs/2410.14684)
91. [OpenTrain abstract page: CodeCompass (arXiv 2602.20048)](https://www.opentrain.ai/papers/codecompass-navigating-the-navigation-paradox-in-agentic-code-intelligence--arxiv-2602.20048/)
92. [Sourcegraph blog: Large-scale code changes, how to do them safely](https://sourcegraph.com/blog/large-scale-code-changes)
93. [InfoQ: Spotify more than doubled monthly code changes as AI accelerated development (Oct 2026)](https://infoq.com/news/2026/10/spotify-ai-quality-controls)
94. [Uber Engineering: Introducing Piranha](https://www.uber.com/cz/en/blog/piranha/)
95. [Airbnb Tech: Accelerating large-scale test migration with LLMs](https://airbnb.tech/?p=366)
96. [The Pragmatic Engineer: We need to talk about migrations with AI](https://newsletter.pragmaticengineer.com/p/the-pulse-we-need-to-talk-about-migrations-b3d?r=1q9je3)
97. [Spotify Engineering: 1,500+ PRs later, background coding agent (Honk, Part 1)](https://engineering.atspotify.com/2025/11/spotifys-background-coding-agent-part-1)
98. [GitLab blog: Introducing GitLab Orbit (10 Jun 2026)](https://about.gitlab.com/blog/introducing-gitlab-orbit/)

<!-- citation link definitions -->
[1]: https://sourcegraph.com/blog/a-new-era-for-sourcegraph-the-intelligence-layer-for-ai-coding-agents-and-developers
[2]: https://about.gitlab.com/blog/gitlab-orbit-ga/
[3]: https://www.businesswire.com/news/home/20260519919718/en/
[4]: https://about.gitlab.com/gitlab-orbit/
[5]: https://sourcegraph.com/resources/context-compare
[6]: https://aws.amazon.com/marketplace/pp/prodview-qa5qb3cy3ofbc
[7]: https://github.com/colbymchenry/codegraph
[8]: https://github.com/DeusData/codebase-memory-mcp
[9]: https://sourcegraph.com/blog/the-future-of-scip
[10]: https://arxiv.org/pdf/2503.21710v2
[11]: https://arxiv.org/html/2602.20048v1
[12]: https://comparethemarketcareers.com/blog/comparing-context-retrieval-approaches-for-ai-code-review/
[13]: https://docs.gitlab.com/orbit/schema/
[14]: https://github.com/scip-code/scip
[15]: https://docs.joern.io/code-property-graph/
[16]: https://qwiet.ai/?p=9049
[17]: https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees.md
[18]: https://docs.moderne.io/administrator-documentation/moderne-platform/references/lossless-semantic-trees
[19]: https://about.gitlab.com/press/releases/2026-06-10-gitlab-announces-new-capabilities-to-give-enterprises-speed-control-at-agentic-scale/
[20]: https://github.com/getzep/graphiti
[21]: https://7.5.sourcegraph.com/api/mcp.md
[22]: https://sourcegraph.com/docs/pricing/enterprise
[23]: https://github.com/gitlabhq/orbit-knowledge-graph
[24]: https://about.gitlab.com/blog/gitlab-transcend-hackathon-orbit/
[25]: https://conf.researchr.org/details/icsme-2023/icsme-2023-tool-demo-track/7/Deterministic-Automatic-Refactoring-at-Scale
[26]: https://manilatimes.net/2025/04/15/tmt-newswire/globenewswire/moderne-joins-microsoft-pegasus-program-to-accelerate-large-scale-code-modernization-for-enterprises/2092757
[27]: https://github.com/openrewrite/rewrite
[28]: https://www.intelcapital.com/?p=11696
[29]: https://github.blog/2024/02/14/fixing-security-vulnerabilities-with-ai/
[30]: https://docs.github.com/en/copilot/concepts/agents/code-review
[31]: https://securitylab.github.com/tools/codeql/license
[32]: https://github.com/github/codeql
[33]: https://www.greptile.com/docs/code-review/key-features
[34]: https://www.greptile.com/docs/introduction.md
[35]: https://www.greptile.com/code-context
[36]: https://www.greptile.com/docs/api-reference/zapier
[37]: https://www.greptile.com
[38]: https://docs.coderabbit.ai/integrations/code-graph-analysis
[39]: https://docs.augmentcode.com/context-services/overview
[40]: https://www.augmentcode.com/changelog/context-engine-mcp-in-ga
[41]: https://www.sonarsource.com/products/gitar/
[42]: https://www.sonarsource.com/developers/blueprints/get-started-with-gitar/
[43]: https://harness.io/blog/harness-acquires-qwiet-ai
[44]: https://github.com/Graphify-Labs/graphify
[45]: https://github.com/abhigyanpatwari/GitNexus
[46]: https://github.com/tirth8205/code-review-graph
[47]: https://github.com/oraios/serena
[48]: https://github.com/potpie-ai/potpie
[49]: https://github.com/vitali87/code-graph-rag
[50]: https://github.com/CodeGraphContext/CodeGraphContext
[51]: https://github.com/sourcebot-dev/sourcebot
[52]: https://moderne.io/blog/overview-of-openrewrite-and-moderne
[53]: https://github.com/joernio/joern
[54]: https://github.com/FalkorDB/Auryn
[55]: https://github.com/tree-sitter/tree-sitter
[56]: https://kythe.io/
[57]: https://arxiv.org/html/2504.09691v1
[58]: https://github.com/kythe/kythe
[59]: https://engineering.fb.com/2024/12/19/developer-tools/glean-open-source-code-indexing/
[60]: https://github.com/facebookincubator/Glean
[61]: https://github.com/github/stack-graphs
[62]: https://sourcegraph.com/docs/code-navigation/precise-code-navigation
[63]: https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context
[64]: https://sourcegraph.com/docs/batch_changes
[65]: https://docs.moderne.io/user-documentation/recipes/authoring-recipes/concepts/lossless-semantic-trees
[66]: https://sourcegraph.com/docs/code_navigation/explanations/precise_code_navigation
[67]: https://sourcegraph.com/docs/self-hosted/deploy
[68]: https://handbook.gitlab.com/handbook/engineering/architecture/design-documents/orbit/
[69]: https://docs.gitlab.com/orbit/indexed-data/
[70]: https://docs.gitlab.com/orbit/remote/access/api/
[71]: https://about.gitlab.com/blog/gitlab-orbit-and-google-antigravity
[72]: https://gitlab.com/gitlab-org/orbit/knowledge-graph/-/work_items/553
[73]: https://docs.moderne.io/user-documentation/moddy/moddy-platform
[74]: https://www.businesswire.com/news/home/20260210110758/en/Moderne-Introduces-Prethink-to-Give-AI-Agents-the-Structured-Knowledge-Theyve-Been-Missing
[75]: https://docs.moderne.io/user-documentation/agent-tools/prethink
[76]: https://docs.moderne.io/user-documentation/recipes/prethink
[77]: https://www.businesswire.com/news/home/20260219393723/en/Moderne-Expands-Agent-Tools-Platform-with-Python
[78]: https://docs.moderne.io/user-documentation/moddy/mcp-tools-reference
[79]: https://appdevelopermagazine.com/automated-code-refactoring-platform-moderne/amp/
[80]: https://docs.github.com/en/enterprise-cloud@latest/code-security/responsible-use/responsible-use-autofix-code-scanning
[81]: https://docs.github.com/en/enterprise-cloud%40latest/code-security/responsible-use/security-and-quality-ai-features
[82]: https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/
[83]: https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/
[84]: https://docs.github.com/en/enterprise-server@3.18/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql
[85]: https://docs.github.com/en/enterprise-server@3.17/code-security/concepts/code-scanning/codeql/codeql-code-scanning
[86]: https://arxiv.org/html/2603.27277
[87]: https://developer.harness.io/ai-sca/core-concepts/code-property-graph
[88]: https://gitlab.com/groups/gitlab-org/-/epics/19744
[89]: https://itbrief.co.uk/story/moderne-unveils-prethink-to-boost-ai-code-governance
[90]: https://arxiv.org/abs/2410.14684
[91]: https://www.opentrain.ai/papers/codecompass-navigating-the-navigation-paradox-in-agentic-code-intelligence--arxiv-2602.20048/
[92]: https://sourcegraph.com/blog/large-scale-code-changes
[93]: https://infoq.com/news/2026/10/spotify-ai-quality-controls
[94]: https://www.uber.com/cz/en/blog/piranha/
[95]: https://airbnb.tech/?p=366
[96]: https://newsletter.pragmaticengineer.com/p/the-pulse-we-need-to-talk-about-migrations-b3d?r=1q9je3
[97]: https://engineering.atspotify.com/2025/11/spotifys-background-coding-agent-part-1
[98]: https://about.gitlab.com/blog/introducing-gitlab-orbit/
