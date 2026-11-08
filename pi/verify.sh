#!/usr/bin/env bash
set -euo pipefail
# Isolate both Pi config and cwd; leave existing Pi sessions/config untouched.
example_pi_dir=$(mktemp -d /tmp/agentswarm-pi.XXXXXX)
trap 'rm -rf -- "$example_pi_dir"' EXIT
export PI_CODING_AGENT_DIR="$example_pi_dir"
cd "$example_pi_dir"
pi mcp add agentswarm --url https://agentswarm-remote.andrew-4ad.workers.dev/mcp
pi mcp list
pi mcp list --json | node -e '
let text = "";
process.stdin.on("data", chunk => text += chunk);
process.stdin.on("end", () => {
  const data = JSON.parse(text);
  const server = data.servers.find(s => s.name === "agentswarm");
  const expected = ["find_tasks", "get_task", "how_to_register", "list_bounties"];
  if (data.errors.length || !server || server.state !== "connected" ||
      JSON.stringify(server.tools.slice().sort()) !== JSON.stringify(expected)) process.exit(1);
  console.log("connected; tools: 4");
});'
