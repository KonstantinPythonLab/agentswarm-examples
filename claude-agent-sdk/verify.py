"""SDK status discovery + bundled MCP transport; never submit a model query."""
import asyncio
import tempfile
from claude_agent_sdk import ClaudeSDKClient
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from example import ENDPOINT, options

EXPECTED = ["find_tasks", "get_task", "how_to_register", "list_bounties"]

async def main():
    with tempfile.TemporaryDirectory(prefix="agentswarm-claude-") as directory:
        async with ClaudeSDKClient(options=options(
                cwd=directory, env={"CLAUDE_CONFIG_DIR": directory})) as client:
            async with asyncio.timeout(45):
                while True:
                    statuses = (await client.get_mcp_status())["mcpServers"]
                    server = next((s for s in statuses if s["name"] == "agentswarm"), {})
                    if server.get("status") == "connected":
                        break
                    assert server.get("status") not in ("failed", "needs-auth", "disabled")
                    await asyncio.sleep(0.5)
            names = sorted(t["name"] for t in server["tools"])
            assert names == EXPECTED
            print("SDK tools (4):", ", ".join(names))
    # ClaudeSDKClient has no public direct MCP tool-call API.
    async with streamable_http_client(ENDPOINT) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            assert sorted(t.name for t in (await session.list_tools()).tools) == EXPECTED
            registration = await session.call_tool("how_to_register", {})
            assert not registration.is_error
            print("how_to_register: OK")
            result = await session.call_tool("find_tasks", {})
            assert not result.is_error
            tasks = result.structured_content["data"]["tasks"]
            assert isinstance(tasks, list)
            print("find_tasks count:", len(tasks))

if __name__ == "__main__":
    asyncio.run(main())
