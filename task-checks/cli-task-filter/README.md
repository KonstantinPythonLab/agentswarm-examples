# cli-task-filter

Target: [andrewsiah/agentswarm-cli](https://github.com/andrewsiah/agentswarm-cli).

Prerequisites: Node.js 22; Python checks additionally require Python 3.11 managed
with [uv](https://docs.astral.sh/uv/) and the locked dependencies in `../pyproject.toml`.
Check execution uses zero network except loopback (stdio, a loopback HTTP fixture,
or an intercepted fetch). Clone/install prerequisites before running the check.

Use a fresh clone of agentswarm-examples and a checkout of your target branch.
From this folder, point at that checkout (an absolute path, including spaces, works):

```bash
export BOUNTY_REPO=/absolute/path/to/agentswarm-cli
```

For this Python check, prepare the shared environment from this folder:

```bash
uv sync --project .. --locked --python 3.11
source ../.venv/bin/activate
```

The first dependency install may need a package index; use a populated uv cache
and `uv sync --offline --project .. --locked --python 3.11` for offline setup.
The check itself has no external network dependency.

Exact check command, from this folder:

```bash
python -m pytest -q test_cli_task_filter.py
```

Exit 0 means the independent check passes; a nonzero exit prints the failed
assertion. Missing BOUNTY_REPO or a wrong checkout produces a setup error.
No private bundle or other workspace is required.

The six tests run both binaries against a local HTTP fixture: tasks --task must send type=task&task=post_parent; retired --mission must exit 2 before HTTP; task help must name --task. No target package installation is required: Python uses the checkout through PYTHONPATH. Also update README examples and both repository test suites, and run those suites.
