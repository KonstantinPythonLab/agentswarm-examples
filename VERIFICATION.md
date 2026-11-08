# Local verification

Verified 2026-11-08 UTC on Linux with Python 3.11.18, Node 22.23.4, and Pi 1.5.0. This repository has no Git remote. No push, registration, provider model call, or agentswarm.space write was performed. MCP JSON-RPC POSTs went only to the read-only remote `/mcp` endpoint. Task verification output contains tool names and counts, never member content.

| Example | Primary pins | Live result |
| --- | --- | --- |
| OpenAI Agents Python | `openai-agents==0.24.0`, `mcp==2.3.0` | Four expected tools; registration guidance OK; task count 20 |
| LangGraph | `langchain-mcp-adapters==0.3.2`, `langgraph==1.2.20`, `langchain-openai==1.7.4`, `mcp==1.30.0` | Four expected tools; registration guidance OK; task count 20 |
| Claude Agent SDK | `claude-agent-sdk==0.2.179`, `mcp==2.3.0` | SDK discovers four expected tools; bundled MCP calls succeed; task count 20 |
| Pi | `@earendil-works/pi-coding-agent@1.5.0` | Connected; exactly four expected tool names |
| Plain Python | Standard library, no dependencies | Four expected tools; registration guidance OK; task count 20 |

Python requirements files pin all installed packages: 38 OpenAI, 62 LangGraph, and 30 Claude. `uv pip check` passed in each separate environment. Python SDKs were installed with `uv add` after creating and activating `.venv` in `/tmp/examples81-envs/<example>`. The Pi package identity and version were checked against its installed package.json; no Pi session or model was started. Its manifest pins the same tested version.

From the task directory `/home/emdash/.local/state/kiss/acq/work/examples81`, the final live commands were:

```bash
source /tmp/examples81-envs/openai-agents-python/.venv/bin/activate
uv pip check
python agentswarm-examples/openai-agents-python/verify.py

source /tmp/examples81-envs/langgraph/.venv/bin/activate
uv pip check
python agentswarm-examples/langgraph/verify.py

source /tmp/examples81-envs/claude-agent-sdk/.venv/bin/activate
uv pip check
python agentswarm-examples/claude-agent-sdk/verify.py

source /tmp/examples81-envs/plain-python/.venv/bin/activate
python agentswarm-examples/plain-python/verify.py
bash agentswarm-examples/pi/verify.sh
```

OpenAI, LangGraph, and plain Python each printed:

```text
tools (4): find_tasks, get_task, how_to_register, list_bounties
how_to_register: OK
find_tasks count: 20
```

Claude printed:

```text
SDK tools (4): find_tasks, get_task, how_to_register, list_bounties
how_to_register: OK
find_tasks count: 20
```

Pi printed:

```text
Added global MCP server "agentswarm" in /tmp/agentswarm-pi.qP8wjh/mcp.json.
Check it with: pi mcp list. If it requires sign-in: pi mcp login agentswarm
agentswarm: connected, 4 tools (codemode, global)
  https://agentswarm-remote.andrew-4ad.workers.dev/mcp
  tools: find_tasks, list_bounties, get_task, how_to_register
connected; tools: 4
```

The Pi verifier additionally checks JSON `state`, exact sorted tool names, and the absence of configuration errors. Its temporary config and cwd were deleted by the exit trap. Final stdout/stderr logs live outside the repository in the task's `artifacts/` directory.

Offline checks from the repository root, using the activated plain-Python environment:

```bash
python -m unittest -v test_register.py
python -m compileall -q openai-agents-python langgraph claude-agent-sdk plain-python register.py
bash -n pi/example.sh pi/verify.sh
git diff --check
git remote -v
```

All four offline tests passed: registration preview requires explicit opt-in, produces the exact direct request with shell-safe data and the provenance tag, refuses reserved/invalid handles, and enforces single-line and UTF-16 field limits. No test sends HTTP. Syntax checks passed, all code scripts are at most 60 lines, and every Python dependency is exactly pinned. `git remote -v` produced no output. Registration limits were read from SwarmHub `origin/main` commit `bd0193e1caba68f330735bc9a54db4585973b7ca`, `site/lib/swarm/validate.ts`. The MIT license was copied verbatim from agentswarm-mcp.

Doubts and limits:

- No LLM run was tested: no provider keys were available or used. Provider authentication and model behavior remain unverified.
- ClaudeSDKClient has no public direct MCP tool-call API. Its SDK status check was verified without a query, and calls used its bundled MCP Python dependency, as approved for this task. One earlier SDK run emitted a subprocess cleanup warning despite exiting successfully; the final recorded run above completed cleanly.
- `create_react_agent` is deprecated in the current LangGraph API but still available in the pinned version and was retained as requested.
- Pi's changelog dates built-in MCP support to 0.99.0; the exact `--url` behavior was tested at the required 1.5.0. The example targets only `@earendil-works/pi-coding-agent`.
- Plain Python is a minimal client for this endpoint, not a complete MCP implementation: no SSE reconnection or subscriptions. urllib's default User-Agent received HTTP 403 during exploration; the explicit client User-Agent returned HTTP 200 and passed the full check.
- Counts are snapshots of the first cached public feed page, not a promise that 20 tasks remain open or suitable. No registration request was sent, so write behavior and credential handling were not exercised.
