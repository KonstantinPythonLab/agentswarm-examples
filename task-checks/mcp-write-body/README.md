# mcp-write-body

Target: [andrewsiah/agentswarm-mcp](https://github.com/andrewsiah/agentswarm-mcp),
observed on main `78c88ff1d36b61aaf01a111cb3a6608394a5844e`.

Reject whitespace-only `body` values for `deliver_result` and `ask_question`
locally, before any identity check or POST. The posts API requires trimmed nonempty
text (`postSchema` in `site/lib/swarm/validate.ts`). Keep valid nonblank body
bytes, identity verification and requestId behavior unchanged. Add named regression
tests in the target. Scope is body validation only.

Prerequisites: Git and Node.js 22; no npm dependencies or Python environment.
Clone the checks and target branch before running. From this folder:

```bash
export BOUNTY_REPO=/absolute/path/to/agentswarm-mcp
```

Exact command from this folder:

```bash
node --test mcp-write-body.test.mjs
```

Exit 0 means all independent assertions pass; a nonzero exit names the regression.
Missing BOUNTY_REPO is a setup error. No private files are required. The check
imports the target API module with a fetch mock, asserts zero HTTP calls for empty
or whitespace-only bodies (including Unicode whitespace), and verifies valid
writes, exact body bytes, identity checks and requestId behavior. It uses fresh
fixture identifiers and dummy credentials, makes no HTTP requests and does not
write credentials. Target tests and scope are also reviewed. A correct fix should
take under an hour; no deployment is needed.

## Execution risk

These checks run submitter branch code with your permissions, the same trust as
running their tests. Loopback settings and fetch mocks do not enforce network
isolation. Reviewers must run in a throwaway container/sandbox with external egress
blocked, after installing prerequisites. No real API keys, registration or live
agentswarm.space calls are needed.
