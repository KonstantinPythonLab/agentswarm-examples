# remote-bounty-context

Target: [andrewsiah/agentswarm-remote](https://github.com/andrewsiah/agentswarm-remote).

Prerequisites: Node.js 22; Python checks additionally require Python 3.11 managed
with [uv](https://docs.astral.sh/uv/) and the locked dependencies in `../pyproject.toml`.
Check execution uses zero network except loopback (stdio, a loopback HTTP fixture,
or an intercepted fetch). Clone/install prerequisites before running the check.

Use a fresh clone of agentswarm-examples and a checkout of your target branch.
From this folder, point at that checkout (an absolute path, including spaces, works):

```bash
export BOUNTY_REPO=/absolute/path/to/agentswarm-remote
```

Exact check command, from this folder:

```bash
node --test remote-bounties.test.mjs
```

Exit 0 means the independent check passes; a nonzero exit prints the failed
assertion. Missing BOUNTY_REPO or a wrong checkout produces a setup error.
No private bundle or other workspace is required.

The two fixtures require list_bounties to retain underTaskId and funders, including explicit nulls, while preserving paidBy. fetch and the cache API are replaced in memory; the fixture URL is only compared as text and no external HTTP request is sent. Also add named regression tests in the target repository and run `node --test` there. No Cloudflare build or deployment is needed.

The fixture stores Cache API writes and serves them to a fresh worker module. It
checks the live response, serialized cache projection and later cache-hit response
for both fields, including explicit nulls, without a second upstream fetch.
