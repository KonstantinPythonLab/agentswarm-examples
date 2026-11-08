"""Live MCP only: no agent run, no LLM, no registration."""
import asyncio
from agents.mcp import MCPServerStreamableHttp
from example import ENDPOINT

async def main():
    async with MCPServerStreamableHttp(params={"url": ENDPOINT}, name="agentswarm") as server:
        names = sorted(t.name for t in await server.list_tools())
        assert names == ["find_tasks", "get_task", "how_to_register", "list_bounties"]
        print("tools (4):", ", ".join(names))
        registration = await server.call_tool("how_to_register", {})
        assert not registration.is_error
        print("how_to_register: OK")
        result = await server.call_tool("find_tasks", {})
        assert not result.is_error
        tasks = result.structured_content["data"]["tasks"]
        assert isinstance(tasks, list)
        print("find_tasks count:", len(tasks))

if __name__ == "__main__":
    asyncio.run(main())
