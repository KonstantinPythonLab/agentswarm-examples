#!/usr/bin/env bash
set -euo pipefail
# Configure read-only discovery. This does not run a model or register an agent.
pi mcp add agentswarm --url https://agentswarm-remote.andrew-4ad.workers.dev/mcp
pi mcp list
