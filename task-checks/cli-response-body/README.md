# cli-response-body

Target: [andrewsiah/agentswarm-cli](https://github.com/andrewsiah/agentswarm-cli), observed on
main `312c4cace9fb0de0398805c31f16825c3afd5063`.

Both Node and Python CLIs must classify interrupted successful (2xx) HTTP response-body reads as network errors (exit 7), print a diagnostic, and avoid partial success output or automatic retries. Preserve healthy JSON responses and HTTP status exit codes. Add named regression tests in both builds. Scope is body-read error handling only.

Prerequisites: Git and Node.js 22. The CLI check additionally uses Python 3.11
via [uv](https://docs.astral.sh/uv/) with the shared locked dependencies.
Clone the checks and target branch before running. From this folder:

```bash
export BOUNTY_REPO=/absolute/path/to/agentswarm-cli
uv sync --project .. --locked --python 3.11
source ../.venv/bin/activate
```

Initial dependency installation may need a package index. With a populated cache,
add `--offline` to `uv sync`. Check execution uses only a loopback fixture with
fresh values and dummy identity data; it makes no live site requests.

Exact command from this folder:

```bash
python -m pytest -q test_cli_response_body.py
```

Exit 0 means all independent assertions pass; a nonzero exit names the regression.
Missing BOUNTY_REPO is a setup error. No private files are required. The check runs
the actual target process against a controlled local HTTP server and verifies
successful controls alongside failure cases. Target tests and scope are also
reviewed. Correct fixes should take under an hour; no deployment is needed.

## Execution risk

These checks run submitter branch code with your permissions, the same trust as
running their tests. Loopback settings and fetch mocks do not enforce network
isolation. Reviewers must run in a throwaway container/sandbox with external egress
blocked and loopback enabled, after installing prerequisites. No real API keys,
registration or live agentswarm.space calls are needed.
