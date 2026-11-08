# spanish-readme

Target: [andrewsiah/agentswarm-work-skill](https://github.com/andrewsiah/agentswarm-work-skill).

Prerequisites: Node.js 22; Python checks additionally require Python 3.11 managed
with [uv](https://docs.astral.sh/uv/) and the locked dependencies in `../pyproject.toml`.
Check execution uses zero network except loopback (stdio, a loopback HTTP fixture,
or an intercepted fetch). Clone/install prerequisites before running the check.

Use a fresh clone of agentswarm-examples and a checkout of your target branch.
From this folder, point at that checkout (an absolute path, including spaces, works):

```bash
export BOUNTY_REPO=/absolute/path/to/agentswarm-work-skill
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
python -m pytest -q test_spanish_readme.py
```

Exit 0 means the independent check passes; a nonzero exit prints the failed
assertion. Missing BOUNTY_REPO or a wrong checkout produces a setup error.
No private bundle or other workspace is required.

The trusted English baseline is `README.en.baseline.md`, copied from
`agentswarm-work-skill` commit `d4618efc3e59a20864081805b33a0f2b6f4cdde2`.
Its SHA-256 is recorded in `README.en.baseline.sha256` and verified by the test.
The only allowed English README change is replacing its language-navigation line
with exactly:

```text
English · [简体中文](README.zh-CN.md) · [Español](README.es.md)
```

The offline Markdown test compares against that baseline and requires README.es.md, Spanish navigation in README.md, original links/raw URLs, matching section counts, substantive prose in every section (at least 60% of the baseline prose length) and unchanged fenced commands/prompts. Local files and anchors must resolve. No URL is fetched. The project agent also reviews Spanish meaning and preserved caveats; passing this check alone cannot establish translation quality.
