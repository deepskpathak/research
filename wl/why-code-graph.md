# Why we're evaluating a code graph vendor

We're putting AI coding agents to work across our software lifecycle, from writing code to reviewing it. Each agent starts a task knowing almost nothing about the system it's changing. It searches and reads files to rebuild context every time, and it still misses what sits in another repository or in last month's merge request. At our scale that's slow, expensive and risky. We want one shared, structural picture of our code that every agent and engineer can query.

We're evaluating code graph vendors for four uses:

- **Coding agents.** Agents should get precise answers about definitions, callers and dependencies across repositories on demand, not guesses from text search.
- **Toil reduction campaigns.** Before a migration or upgrade starts, we need to find every affected repository and call site and order the changes by dependency. Once it's running, we need to track what's merged and what's blocked.
- **Automated code review.** A reviewer, human or AI, should see what a change can break beyond the diff: the code that calls it, the services it affects, and the tests that cover it.
- **Knowledge graph.** Code should be linked to the work around it: merge requests, pipelines, deployments, ownership and design decisions. One graph should answer questions that today take hours of manual digging.

The graph also has to hold up at our scale. It must index a very large estate quickly and stay current as code changes. It must respect the same permissions as our source systems and run inside our own environment. Answers need to be deterministic and auditable. Any agent should be able to reach it through open interfaces such as MCP and REST. The requirements that follow turn these needs into criteria we'll test against our own code.
