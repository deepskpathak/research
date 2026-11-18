# Code Graph Vendors Compared

Research date: 18 Nov 2026. This note compares industry and open-source code graph tools for four jobs: feeding AI coding agents, running toil reduction campaigns, automated code review, and building knowledge graphs.

Every fact links to a numbered source. Anything marked **My read** is my opinion, not something a source says. "Vendor-reported" means the vendor did the measuring, and independent benchmarks are rare in this space. I pulled GitHub stars and forks from the GitHub REST API at 02:06 UTC on 18 Nov 2026, and each figure links to its repo. I read "generative agents" as AI coding agents that write code, such as Claude Code, Codex and Cursor.

---

## 1. Summary

**My read:** no single vendor handles all four jobs well. What fits the evidence is a stack. A precise, persistent code graph sits at the bottom. On top of it, an SDLC graph adds merge request and pipeline context, and a deterministic transformation engine runs the campaigns. Agents reach all of it over MCP.

### What changed in 2026

Code graphs became agent infrastructure this year. Sourcegraph 7.0 (Feb 2026) recast the product as a shared intelligence layer for developers and AI agents \[[1][1]\]. GitLab Orbit went GA on 29 Oct 2026 \[[2][2]\]. Moderne now calls itself "the Agent Tools company" \[[3][3]\].

MCP is how they all reach agents. Orbit exposes `query_graph` and `get_graph_schema` \[[4][4]\]. Sourcegraph serves search, navigation and Deep Search over MCP \[[5][5]\], and Moderne ships its LST engine and Moddy agent the same way \[[6][6]\].

Open-source local graphs took off fast. CodeGraph, created in Jan 2026, has 77,889 stars \[[7][7]\]. codebase-memory-mcp, created in Feb 2026, has 48,789 \[[8][8]\].

SCIP became a shared standard too. It moved to open governance in March 2026, and engineers from Meta and Uber sit on its steering committee \[[9][9]\].

### What the evidence says

Graphs help when the answer is several hops away. In KGCompass, 89.7% of the bugs it localized had no location hint in the issue, and the tool found them only by traversing the graph \[[10][10]\].

The catch is that agents often don't call the graph. In CodeCompass, 58% of trials with graph access skipped the tool despite explicit instructions \[[11][11]\]. Graph grounding also costs more per call. In Compare the Market's test, the Orbit-grounded reviewer cost $2.37 per merge request, against $0.58 for diff-only review \[[12][12]\].

### Shortlist (my read)

| Need | Lead pick | Alternative |
| --- | --- | --- |
| Code graph corpus for a context service | Sourcegraph (any code host) or GitLab Orbit (GitLab-native) | codebase-memory-mcp (local, MIT) |
| SDLC knowledge graph (MRs, pipelines, deployments) | GitLab Orbit | Potpie (open source) |
| Toil reduction campaigns | Moderne + OpenRewrite | Sourcegraph Batch Changes |
| Automated MR review context | GitLab Orbit on GitLab | Greptile or CodeRabbit (built-in graphs); code-review-graph (open source) |
| Security semantics | GitHub CodeQL | Joern (open source CPG) |

---

## 2. Terms used here

- **Code graph.** Nodes for files and symbols, edges for calls, imports and definitions. Orbit's graph, for example, holds files, directories, definitions, imports and calls \[[13][13]\].
- **SCIP.** A language-agnostic protocol for indexing source code. It's what powers go-to-definition and find-references \[[14][14]\].
- **Code property graph (CPG).** A graph for mining large codebases for programming patterns, queried with a Scala-based DSL \[[15][15]\]. It merges a syntax tree, a control-flow graph and a program-dependence graph into one structure \[[16][16]\].
- **Lossless Semantic Tree (LST).** OpenRewrite's code tree. It keeps whitespace, so it can print the original source back out without reformatting \[[17][17]\], and it carries type information \[[18][18]\].
- **Context graph (or SDLC graph).** A code graph joined to lifecycle data. Orbit maps code, work items, pipelines, deployments and production signals into one graph \[[19][19]\]. Graphiti goes further and records when each fact became true and when it was superseded \[[20][20]\].
- **MCP.** The Model Context Protocol. Every tool on the shortlist uses it to serve agents \[[4][4], [6][6], [7][7], [21][21]\].

---

## 3. Who's in the market

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

### 3.4 How teams wire these tools in

These are the six patterns that came up most.

1. **A local MCP server beside the agent.** CodeGraph, codebase-memory-mcp and Orbit Local all run on the developer's machine \[[7][7], [8][8], [23][23]\].
2. **A shared remote endpoint over an org-wide index.** Sourcegraph serves `/.api/mcp` from its instance \[[21][21]\], and Orbit Remote spans a top-level GitLab.com group \[[23][23]\].
3. **Indexing in CI.** Sourcegraph recommends running SCIP indexing in CI for complex builds \[[62][62]\]. Compare the Market ran Orbit as a sidecar that re-indexed on every MR pipeline \[[12][12]\].
4. **A review bot with its own graph.** Greptile builds a graph when you sign up and queries it on every review \[[63][63]\].
5. **A campaign engine.** Sourcegraph Batch Changes opens and tracks PRs across many repos \[[64][64]\], and Moderne runs recipes across thousands of them \[[65][65]\].
6. **Hooks and skills that push context.** GitNexus registers Claude Code hooks and writes `AGENTS.md` and `CLAUDE.md` files \[[45][45]\]. codebase-memory-mcp installs skills, agent profiles and hooks \[[8][8]\].

---

## 4. The shortlist, tool by tool

I picked four industry vendors and four open-source tools, based on how well they fit the four jobs and on traction.

### 4.1 Sourcegraph

Sourcegraph is a code search and navigation platform, and version 7.0 repositioned it as a shared intelligence layer for developers and agents \[[1][1]\]. It indexes every repository, branch, tag and revision across GitHub, GitLab, Bitbucket, Gerrit, Perforce and Azure DevOps \[[5][5]\]. On top of that index you get structural, semantic and regex search, plus commit, diff and blame history \[[5][5]\]. Go-to-definition and find-references work across repos out of the box \[[5][5]\].

Two features matter most for agents. Deep Search runs agentic, natural-language exploration over the same index \[[5][5]\], and 7.0 made it more accurate, added image support and built code navigation into it \[[1][1]\]. Batch Changes opens a PR on every affected repo and tracks each one until it merges \[[64][64]\]. The agentic version generates reviewable AI changes across thousands of repos \[[5][5]\].

**How it works.** Precise navigation comes from per-language SCIP indexes that you upload to the instance \[[62][62]\]. Without one, Sourcegraph falls back to search-based navigation \[[66][66]\]. SCIP is optional, and Sourcegraph says search, navigation, Deep Search and MCP all work without it \[[5][5]\].

**How teams use it.** Agents connect to `/.api/mcp`, and `/.api/mcp/all` and `/.api/mcp/deepsearch` offer other tool sets \[[21][21]\]. Auth is OAuth 2.0 (Dynamic Client Registration included) or access tokens \[[21][21]\]. Campaigns are YAML batch specs that name the target repos, the commands to run and the changeset templates \[[64][64]\].

**Cost and deployment.** Enterprise Dedicated Cloud is the default, and Enterprise Self Hosted is available on request. Both list at $59 per user per month \[[22][22]\]. Self-hosting runs on Kubernetes with Helm, which Sourcegraph recommends, or on Docker Compose \[[67][67]\].

**Watch out for.** The MCP server needs an Enterprise plan \[[21][21]\]. Precise data needs a working indexer for each language, and for authenticated builds Sourcegraph recommends indexing in CI \[[62][62]\]. **My read:** the pages I checked cover code and version history, not pipelines, deployments or vulnerabilities, so SDLC context would have to come from somewhere else.

### 4.2 GitLab Orbit

Orbit used to be called the GitLab Knowledge Graph. It's a Rust service that builds a property graph from SDLC metadata and code, and you query it with a JSON, Cypher-like DSL that compiles to ClickHouse SQL \[[68][68]\]. It went GA on 29 Oct 2026 \[[2][2]\].

The graph covers default-branch code (files, directories, definitions, imports and calls) plus merge requests, pipelines, vulnerabilities and branches \[[13][13]\]. Code indexing supports Ruby, Java, Kotlin, Python, TypeScript, JavaScript, Rust, Go, C#, C, C++, PHP, Bash and Elixir \[[23][23]\]. The hosted DSL handles aggregations, traversals, neighbors and pathfinding \[[23][23]\]. File content is fetched at query time, so an agent can read code without a second API call \[[69][69]\].

**How it works.** Orbit comes in two shapes. Orbit Remote runs `gkg-server` on ClickHouse, fed by change data capture through GitLab's Data Insights Platform \[[23][23]\]. Orbit Local is a single-binary `orbit` CLI on DuckDB with a stdio MCP server \[[23][23]\].

**How teams use it.** Agents connect over MCP or with `glab orbit setup`, and GitLab names Claude Code, Codex, Cursor, OpenCode, Gemini CLI and Antigravity as clients \[[2][2]\]. It's also native in Duo Agent Platform, custom agents can use REST, and engineers get a Data Explorer \[[2][2]\]. The REST endpoints are `/api/v4/orbit/query`, `/schema`, `/status` and `/tools` \[[70][70]\].

**Cost and availability.** You need Premium or Ultimate. GitLab.com gets it first, and Self-Managed and Dedicated follow in the coming weeks \[[2][2]\]. Pricing is by query pack: $30 in GitLab Credits per user per month adds 1,000 queries to a pool the whole org shares, and overage runs about $0.03 per query \[[2][2]\]. Schema lookups through `get_graph_schema` are free, while queries use credits \[[71][71]\].

**What GitLab claims.** These are vendor numbers. GitLab says it indexed more than 1.5 million projects and 8 TB of graph data in under 2 hours \[[2][2]\]. It also claims up to 11x faster responses with 4.5x fewer tokens \[[19][19]\], and up to 45x fewer retries \[[2][2]\].

**Watch out for.** Only the default branch gets indexed \[[13][13]\]. The license is GitLab's Enterprise Edition license, not an open-source one \[[23][23]\]. Some MCP clients cut off the long `query_graph` description, so the model never sees the DSL grammar \[[72][72]\]. And in Compare the Market's pre-GA test, latency was 80.6 s against about 44 s for diff-only review \[[12][12]\].

### 4.3 Moderne and OpenRewrite

OpenRewrite is an open-source project for semantic analysis and refactoring \[[52][52]\]. Moderne builds on it so you can run its recipes against thousands of repositories at once \[[65][65]\]. The recipes search and transform code held as LSTs \[[25][25]\].

Moderne has layered agent features on top:

- **Moddy**, a multi-repo AI agent in restricted beta that runs across thousands of repositories \[[73][73]\].
- **Prethink**, launched 10 Feb 2026 \[[74][74]\]. It gives agents pre-resolved context on service endpoints, database connections, external calls, messaging patterns and test coverage \[[75][75]\]. It can also emit an optional knowledge graph and FINOS CALM architecture diagrams \[[76][76]\].
- **Changelog** (May 2026), which shows what's ready, blocked or waiting across a changeset through MCP and GraphQL \[[3][3]\].
- **Trigrep**, symbol-aware code search for agents \[[3][3]\].

**How it works.** Run locally, the LST has to fit in memory \[[17][17]\]. Moderne instead serializes LSTs as a build byproduct and edits them in bulk later \[[65][65]\]. Python support arrived in Feb 2026 \[[77][77]\].

**How teams use it.** Moderne ships the LST engine, recipe catalog, CLI, IDE plugins and Moddy, and serves them to coding agents over MCP \[[6][6]\]. Its pitch is that the agent plans and Moderne's deterministic tools execute \[[6][6]\]. Moddy Desktop runs an MCP server at `localhost:4848/mcp` \[[78][78]\].

**Traction.** Moderne raised a $30M Series B in Feb 2025, with Morgan Stanley, Amex Ventures and TIAA Ventures taking part \[[79][79]\]. OpenRewrite is built into Amazon Q and Broadcom App Advisor \[[79][79]\].

**Watch out for.** Moddy is still in restricted beta \[[73][73]\]. **My read:** Moderne is strongest on JVM ecosystems, so check recipe coverage for every language and framework you plan to migrate.

### 4.4 GitHub CodeQL

CodeQL is GitHub's semantic analysis engine. It lets you query a codebase as though it were data \[[29][29]\].

Most teams meet it through GitHub features rather than directly. Copilot Autofix suggests fixes for CodeQL alerts. It's on by default for repos that use CodeQL and doesn't need a Copilot subscription \[[80][80]\], and it runs on pull requests and on the default branch \[[81][81]\]. Copilot code review now mixes LLM detection and tool calling with CodeQL and ESLint \[[82][82]\]. CodeQL is on by default there, while ESLint and PMD start switched off \[[30][30]\]. If you need more framework coverage, you can extend the data-flow libraries with your own sources and sinks \[[83][83]\].

**Languages.** CodeQL supports C/C++, C#, Go, Java/Kotlin, JavaScript/TypeScript and more, but not PHP or Scala \[[84][84]\]. The standard queries are open source in github/codeql \[[32][32]\].

**How teams use it.** Default setup picks the languages, query suite and trigger events for you \[[84][84]\]. Code scanning runs on public repos, and on org repos with GitHub Code Security turned on \[[85][85]\].

**Watch out for.** Without GitHub Advanced Security, you can only use the CodeQL CLI on open-source codebases \[[31][31]\]. **My read:** CodeQL is built for deep analysis rather than for answering an agent's general code questions over MCP. It suits review and security better than agent navigation, especially for code hosted on GitLab.

### 4.5 CodeGraph

CodeGraph pre-builds a graph of every symbol, call edge and dependency, so an agent can get the code it needs in one call \[[7][7]\]. A Rust kernel parses 20 languages into a local SQLite database with FTS5, and no data leaves the machine \[[7][7]\]. By default it exposes one MCP tool, `codegraph_explore`. The narrower tools still work but stay unlisted \[[7][7]\]. It watches the project and updates the graph on every file change \[[7][7]\].

Its own benchmark (7 repos, Claude Opus 4.8) reports 88% fewer tool calls, 53% faster answers, 62% fewer tokens and 44% lower cost \[[7][7]\]. To their credit, the authors also flag a cost: in multi-turn sessions, about 80% more retrieval context stays resident in the window \[[7][7]\]. A hosted PR product has been announced \[[7][7]\].

### 4.6 codebase-memory-mcp

This tool builds a persistent local knowledge graph that links code to documentation, configuration and infrastructure \[[8][8]\]. The backend is native C, with 17 MCP tools, vendored grammars and hybrid LSP type resolution \[[8][8]\]. The accompanying preprint stores the graph in SQLite and uses Louvain community detection \[[86][86]\]. It reaches past source files into Docker, Kubernetes, Helm, Terraform, Ansible and CI configuration \[[8][8]\].

It's fast. A full index of the Linux kernel (28M lines) takes 3 minutes on an Apple M3 Pro and produces 4.81M nodes and 7.72M edges \[[8][8]\]. Across 31 repos, the authors report 10x lower token use and 2.1x fewer tool calls than file-by-file exploration \[[8][8]\]. The project also publishes OpenSSF Scorecard and SLSA 3 badges \[[8][8]\].

### 4.7 GitNexus

GitNexus builds a graph of symbols, calls, dependencies and execution flows that you can use through MCP, a CLI or a web explorer \[[45][45]\]. Its tools are `query`, `context`, `impact`, `trace`, `detect_changes` and `rename` \[[45][45]\]. It has 18 language providers, COBOL among them \[[45][45]\]. Parsing uses tree-sitter, and storage is LadybugDB, an embedded graph database with vector support \[[45][45]\]. One shared HTTP MCP server can serve several agents at once \[[45][45]\].

**Watch out for.** The license is PolyForm Noncommercial. Commercial use, PR blast-radius review and a unified multi-repo graph all sit in the paid enterprise offering \[[45][45]\].

### 4.8 Joern

Joern turns source code, bytecode and binaries into code property graphs, aimed at vulnerability discovery and static analysis research \[[53][53]\]. The graphs live in a custom graph database, and you mine them with a Scala DSL \[[53][53]\]. Version 4.0.0 moved storage from overflowdb to flatgraph \[[53][53]\]. The CPG idea started with vulnerability hunting in C system code and the Linux kernel \[[15][15]\].

Harness bought Qwiet AI (formerly ShiftLeft) in Sep 2025, and Fabian Yamaguchi, who created the CPG, now works at Harness \[[43][43]\]. Expect a learning curve. Harness's own docs call it steep \[[87][87]\].

---

## 5. Side by side

| | Graph scope | Precision | Multi-repo | Writes code | Self-host | License | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Sourcegraph** | Code plus commit, diff, blame history | Compiler-grade with SCIP, search-based otherwise | Yes, six code hosts | Batch Changes | Yes, on request | Commercial, $59/user/month list | \[[5][5], [22][22], [64][64]\] |
| **GitLab Orbit** | Code plus MRs, pipelines, vulnerabilities | AST-based code graph | Top-level GitLab.com group | No (read-only API) | Coming after GA | GitLab EE | \[[2][2], [12][12], [13][13], [23][23], [88][88]\] |
| **Moderne** | Type-attributed code model | Compiler-accurate LST | Thousands of repos | Recipes, Moddy | SaaS tenant | OpenRewrite Apache-2.0 | \[[18][18], [26][26], [27][27], [65][65], [89][89]\] |
| **CodeQL** | Code database with data flow | Semantic analysis | Per repository (my read) | Autofix suggestions | GitHub Enterprise Server | Restricted CLI terms | \[[29][29], [31][31], [80][80], [83][83], [84][84]\] |
| **CodeGraph** | Symbols, calls, dependencies | tree-sitter plus cross-file resolution | Other indexed projects by path | No | Local only | MIT | \[[7][7]\] |
| **codebase-memory-mcp** | Code, docs, config, infra | tree-sitter plus hybrid LSP | Calls across services | No | Local only | MIT | \[[8][8]\] |
| **GitNexus** | Symbols, calls, flows | Varies by language | Enterprise edition | Semantic rename | Local; paid self-hosted | PolyForm NC | \[[45][45]\] |
| **Joern** | AST, control flow, data dependence | Semantic CPG | Per project (my read) | No | Local | Apache-2.0 | \[[16][16], [53][53]\] |

---

## 6. Use cases

### 6.1 Generative agents (AI coding agents)

Coding agents rebuild context from scratch on every task, with grep, glob and file reads \[[5][5]\]. A code graph gives them a shortcut.

1. **Answer codebase questions in fewer calls.** CodeGraph cut tool calls by 88% in its own benchmark \[[7][7]\], and codebase-memory-mcp reports 10x lower token use \[[8][8]\]. Good fits: CodeGraph, codebase-memory-mcp and Sourcegraph MCP.
2. **Find and fix the bug.** RepoGraph improved all four SWE-bench systems it was plugged into (ICLR 2025) \[[90][90]\]. KGCompass reached 58.3% on SWE-bench Lite at about $0.2 per repair \[[10][10]\].
3. **Spot hidden dependencies before editing.** CodeCompass scored 99.4% on hidden-dependency tasks, where a vanilla agent scored 76.2% \[[91][91]\].
4. **Ask instead of inventing.** One hackathon team's agent checks Orbit, and when it can't find a service, it asks where the real code lives \[[24][24]\].
5. **Edit in dependency order.** The hackathon runner-up maps every affected file and edits them in dependency order \[[24][24]\].
6. **Start from architecture facts.** Moderne Prethink hands agents verified service endpoints and dependencies, so they don't have to infer the architecture \[[75][75]\].

The graph only helps if the agent calls it. In CodeCompass, runs that used the tool reached 99.5% coverage, and runs that skipped it reached 80.2% \[[11][11]\]. **My read:** push context through hooks or skills rather than relying on the prompt.

### 6.2 Toil reduction campaigns

Software Engineering at Google defines a large-scale change as a set of logically related changes that can't be submitted as one atomic unit \[[92][92]\]. Campaigns automate that kind of work, and a code graph tells you where the work is.

1. **Work out the impact set first.** Google's migration tooling follows Kythe references up to five hops out from a field, then has an LLM fill the accuracy gaps \[[57][57]\]. Over 39 migrations, the LLM generated 74.45% of the code changes, and developers estimated a 50% time saving \[[57][57]\].
2. **Run deterministic upgrades.** OpenRewrite recipes transform LSTs, and Moderne runs them across thousands of repos \[[65][65]\].
3. **Open, track and merge PRs across the fleet.** Batch Changes tracks every changeset until it merges \[[64][64]\]. At Spotify, Fleetshift picks targets, schedules work and tracks progress while the Honk agent edits the code, and Fleet Management has merged more than 2.5 million automated PRs \[[93][93]\].
4. **Delete dead code and stale flags.** Uber's Piranha has removed around two thousand stale feature flags along with their code \[[94][94]\]. Meta uses Glean to find unused C++ includes and automate the cleanup \[[59][59]\].
5. **See what's blocked.** Moderne Changelog shows agents what's ready, blocked or waiting, over MCP \[[3][3]\]. Meta tracks API migration progress with Glean \[[59][59]\].
6. **Give LLM migrations rich context.** Airbnb's prompts included sibling tests, imports and the component source \[[95][95]\]. It moved nearly 3.5K test files in 6 weeks \[[95][95]\], against a manual estimate of 1.5 years \[[96][96]\].

For scale: about half of Spotify's pull requests have been automated since mid-2024 \[[97][97]\].

### 6.3 Automated code review

1. **Show what a change can break beyond the diff.** Greptile queries its graph for the dependencies and usages of a changed function \[[63][63]\]. code-review-graph lists the callers, dependents and tests a change can reach, with a risk score \[[46][46]\].
2. **Pull cross-file definitions into the review.** CodeRabbit maps definitions and references and finds files that tend to change together \[[38][38]\].
3. **Ground GitLab MR review in the SDLC graph.** Compare the Market's Orbit-grounded reviewer matched about 70% of expected inline comments. RAG matched about 58%, worse than adding no context at all \[[2][2]\].
4. **Mix deterministic findings into AI review.** Copilot code review combines LLM analysis with CodeQL and ESLint \[[82][82]\].
5. **Pick the tests a change can reach.** A hackathon team used Orbit's whole-codebase call graph for this \[[24][24]\], and Meta uses Glean for test selection \[[59][59]\].
6. **Cut noise with reachability.** Harness uses Qwiet's reachability analysis to cut noise and focus on real risk \[[43][43]\].
7. **Index diffs for review tooling.** Meta turns diffs into "diff sketches" that drive lint rules and notifications \[[59][59]\].

One caution on the headline number. Compare the Market measured alignment with a golden set, scored by an LLM judge, on 79 MRs, and the authors call the result directional \[[12][12]\].

### 6.4 Knowledge graphs

1. **SDLC context graph.** Orbit links merge requests, pipelines and vulnerabilities to projects and code \[[13][13]\], and engineers use it to trace changes and investigate incidents \[[98][98]\].
2. **Incident forensics.** A financial services company traced a build-system outage to a CI job that failed 50% of the time \[[2][2]\].
3. **Code, docs and infrastructure in one graph.** codebase-memory-mcp links docs, architecture decisions and Terraform or Kubernetes config to the code \[[8][8]\].
4. **Architecture as data.** Prethink emits FINOS CALM diagrams and an optional knowledge graph \[[76][76]\].
5. **Decisions and team knowledge.** Potpie indexes decisions, source history, team knowledge and workflows \[[48][48]\].
6. **Facts that change over time.** Graphiti gives every fact a validity window and traces it back to the source episodes \[[20][20]\].
7. **An org-wide fact store for code.** Meta's Glean serves code navigation, search, docs and RAG for AI coding assistants \[[59][59]\].
8. **Mixed corpora.** Graphify merges code, PDFs and images, and tags each edge as extracted, inferred or ambiguous \[[44][44]\].

---

## 7. How much to trust the numbers

Most of them come from vendors. Orbit, CodeGraph, Augment and codebase-memory-mcp all publish their own benchmarks \[[2][2], [7][7], [8][8], [40][40]\]. I found one public customer A/B test: Compare the Market ran baseline, Orbit, RAG and Orbit plus RAG on 79 real MRs \[[12][12]\].

Corpus size matters as well. Graphify's token reduction was about 1x on a 6-file corpus and 71.5x on 52 files \[[44][44]\].

**My read:** star counts measure attention, not production use. Graphify passed 149k stars within about seven and a half months of its creation in April 2026 \[[44][44]\], so treat stars as a weak signal.

---

## 8. How I'd decide (my read)

Score each option on these questions:

| Criterion | What to ask |
| --- | --- |
| Precision | Compiler-grade (SCIP, LST, CodeQL) or tree-sitter heuristics? |
| Scope | Code only, or code plus MRs, pipelines and deployments? |
| Freshness | Updates on every commit or file save, or scheduled re-indexing? |
| Access control | Are results permission-aware across repos? |
| Agent ergonomics | How many tools, and how long are their descriptions? Some clients truncate long ones \[[72][72]\]. |
| Deployment and license | When can we self-host, and on what commercial terms? |
| Cost per query | Graph calls add latency and spend \[[12][12]\]. |

Then work through these in order:

1. **Build the eval harness first.** Reuse Compare the Market's four-arm design (no context, graph, RAG, both) on real MRs \[[12][12]\].
2. **Pick the base layer.** If the code lives on GitLab, trial Orbit Remote. If it spans hosts, trial Sourcegraph. Keep codebase-memory-mcp or CodeGraph as a local, MIT-licensed baseline.
3. **Pick the campaign layer.** Pilot Moderne on one JVM migration and count merged PRs and blocked changes.
4. **Check licenses early.** GitNexus is noncommercial \[[45][45]\]. CodeQL's CLI terms restrict private code \[[31][31]\]. Orbit uses the GitLab EE license \[[23][23]\].
5. **Confirm self-hosting dates.** Orbit Self-Managed and Dedicated come after GA \[[2][2]\], and Sourcegraph Self Hosted is on request \[[22][22]\].

**Next actions**

- [ ] Ask GitLab for the Orbit Self-Managed date and its RBAC model.
- [ ] Run the four-arm MR review eval on 50 to 100 internal MRs.
- [ ] Pick one campaign, such as a Java or Spring upgrade, for a Moderne pilot.
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
