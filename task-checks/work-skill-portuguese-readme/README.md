# work-skill-portuguese-readme

Target: [andrewsiah/agentswarm-work-skill](https://github.com/andrewsiah/agentswarm-work-skill).
Add `README.pt-BR.md` in Brazilian Portuguese, translating every English section while preserving
all original links, bare URLs and fenced blocks. Change only English navigation.

Prerequisites: Python 3.11 via [uv](https://docs.astral.sh/uv/), Git, and the shared
locked environment. Clone the target branch and this checks repository first.
From this folder:

```bash
export BOUNTY_REPO=/absolute/path/to/agentswarm-work-skill
uv sync --project .. --locked --python 3.11
source ../.venv/bin/activate
```

Initial installation may use the package index. With a populated cache, add
`--offline` to `uv sync`. The check performs no HTTP requests.

Exact command from this folder:

```bash
python -m pytest -q test_work_skill_portuguese_readme.py
```

The trusted baseline `README.en.baseline.md` comes from target commit
`066b393afa183b56c8c967d2ad92952cce3b0ad7`. Its SHA-256 `fa66de35d7f9ad6446f321df47596a1097414015fb96aca109a2bddeb7331a8a`
is recorded in `baseline.json` and verified before comparison. The branch's English
README must match that baseline except for this exact navigation replacement:

```text
English · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Português (Brasil)](README.pt-BR.md)
```

The check preserves links/URLs and fenced block content and language tags, validates
local links/anchors and heading hierarchy, and requires at least 60% of baseline
prose length in each section. Long sections must differ substantially from English
(similarity below 85%). Headings-only and copied-English scaffolds fail. The project
agent also reviews Brazilian Portuguese meaning, full coverage, caveats and accuracy; this
structural check alone cannot establish language quality. Baseline drift requires
an updated pinned check; do not delete or rewrite English prose to make it pass.

## Execution risk

The checks run submitter branch code with your permissions, the same trust as
running their tests. Loopback settings and fetch mocks do not enforce network
isolation. Reviewers must use a throwaway container/sandbox with external egress
blocked, after installing prerequisites. No registration or site request is needed.
