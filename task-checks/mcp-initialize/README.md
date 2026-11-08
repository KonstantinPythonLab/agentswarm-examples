# mcp-initialize

Target: [andrewsiah/agentswarm-mcp](https://github.com/andrewsiah/agentswarm-mcp).

Prerequisites: Node.js 22; Python checks additionally require Python 3.11 managed
with [uv](https://docs.astral.sh/uv/) and the locked dependencies in `../pyproject.toml`.
Check execution uses zero network except loopback (stdio, a loopback HTTP fixture,
or an intercepted fetch). Clone/install prerequisites before running the check.

Use a fresh clone of agentswarm-examples and a checkout of your target branch.
From this folder, point at that checkout (an absolute path, including spaces, works):

```bash
export BOUNTY_REPO=/absolute/path/to/agentswarm-mcp
```

Exact check command, from this folder:

```bash
node --test mcp-init.test.mjs
```

Exit 0 means the independent check passes; a nonzero exit prints the failed
assertion. Missing BOUNTY_REPO or a wrong checkout produces a setup error.
No private bundle or other workspace is required.

The 15 stdio tests require malformed supplied metadata to return -32602, keep ping usable, and preserve valid/omitted metadata and unknown-version fallback. The subprocess base URL is loopback. Also add named regression tests in the target repository and run `node --test` there.

Negotiation is checked for all versions supported at target commit
`78c88ff1d36b61aaf01a111cb3a6608394a5844e`: `2024-11-05`, `2025-03-26`,
`2025-06-18` and `2025-11-25`. Unknown versions must still fall back to `2025-06-18`.
