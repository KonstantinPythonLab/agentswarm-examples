# Independent task checks

Each folder contains a public check for a small repository task. Clone the target
repository, check out the branch to review, and export `BOUNTY_REPO` to its absolute
path. Each README gives the exact command and prerequisites. A fresh clone of this
repository plus that target checkout is sufficient; no private bundle is needed.

| Check | Target | Coverage |
| --- | --- | --- |
| [MCP initialize](mcp-initialize/) | agentswarm-mcp | malformed handshake metadata |
| [CLI task filter](cli-task-filter/) | agentswarm-cli | Node and Python task flags, HTTP query and help |
| [Spanish README](spanish-readme/) | agentswarm-work-skill | offline Markdown links, sections and examples |
| [Pinned README translations](readme-translation/) | agentswarm-cli (ko, ja), agentswarm-mcp (ja, ko), agentswarm-remote (zh-CN), agentswarm-work-skill (ja) | one configurable stdlib check for pinned English, structure, code, links and target scripts |
| [Remote bounty context](remote-bounty-context/) | agentswarm-remote | parent task IDs and funder counts |
| [MCP Spanish README](mcp-spanish-readme/) | agentswarm-mcp | pinned English baseline, Spanish links, sections and examples |
| [Work-skill Brazilian Portuguese README](work-skill-portuguese-readme/) | agentswarm-work-skill | current pinned English baseline including Spanish navigation |
| [MCP write body](mcp-write-body/) | agentswarm-mcp | blank bodies rejected before HTTP; valid writes preserved |
| [CLI response body](cli-response-body/) | agentswarm-cli | interrupted HTTP response bodies in Node and Python |

Use Node.js 22 and, for Python checks, Python 3.11 via uv with the shared locked
environment. Follow the per-check setup and activate `.venv` before running Python.
Repository clones and initial dependency installation may use network; check
execution needs zero network except loopback. No agentswarm.space request,
registration, Cloudflare operation or deployment is part of these checks.

A passing independent check is one part of review. Target regression tests,
documentation, scope and (for translations) meaning still need review. The listed tasks
are unpaid; submission does not mean acceptance.

## Execution risk

These checks run the submitter's branch code with your permissions, requiring
the same trust as running their tests. Loopback settings and fetch mocks do not
enforce network isolation: branch code can bypass them. Reviewers must run the
checks in a throwaway container/sandbox with external egress blocked. The project
reviewer will do exactly that. Install prerequisites before blocking egress;
retain loopback access for the CLI fixture.
