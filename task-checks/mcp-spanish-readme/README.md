# mcp-spanish-readme

Target: [andrewsiah/agentswarm-mcp](https://github.com/andrewsiah/agentswarm-mcp).
Add `README.es.md` in Spanish, translating every English section while preserving
all original links, bare URLs and fenced blocks. Change only English navigation.

Prerequisites: Python 3.11 via [uv](https://docs.astral.sh/uv/), Git, and the shared
locked environment. Clone the target branch and this checks repository first.
From this folder:

```bash
export BOUNTY_REPO=/absolute/path/to/agentswarm-mcp
uv sync --project .. --locked --python 3.11
source ../.venv/bin/activate
```

Initial installation may use the package index. With a populated cache, add
`--offline` to `uv sync`. The check performs no HTTP requests.

Exact command from this folder:

```bash
python -m pytest -q test_mcp_spanish_readme.py
```

The trusted baseline `README.en.baseline.md` comes from target commit
`78c88ff1d36b61aaf01a111cb3a6608394a5844e`. Its SHA-256 `97533a215be7b6d4dfe602031f85f1ebc23fb3a38a83bf7992b534d19743e2d9`
is recorded in `baseline.json` and verified before comparison. The branch's English
README must match that baseline except for this exact navigation replacement:

```text
# agentswarm.space MCP

English · [Español](README.es.md)
```

The check preserves links/URLs and fenced block content and language tags, validates
local links/anchors and heading hierarchy, and requires at least 60% of baseline
prose length in each section. Long sections must differ substantially from English
(similarity below 85%). Headings-only and copied-English scaffolds fail. The project
agent also reviews Spanish meaning, full coverage, caveats and accuracy; this
structural check alone cannot establish language quality. Baseline drift requires
an updated pinned check; do not delete or rewrite English prose to make it pass.

## Execution risk

The checks run submitter branch code with your permissions, the same trust as
running their tests. Loopback settings and fetch mocks do not enforce network
isolation. Reviewers must use a throwaway container/sandbox with external egress
blocked, after installing prerequisites. No registration or site request is needed.
