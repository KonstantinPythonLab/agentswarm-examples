"""Use the adapter's session without invoking the graph or model."""
import asyncio
from example import mcp_client

async def main():
    client = mcp_client()
    tools = await client.get_tools()
    names = sorted(t.name for t in tools)
    assert names == ["find_tasks", "get_task", "how_to_register", "list_bounties"]
    print("tools (4):", ", ".join(names))
    async with client.session("agentswarm") as session:
        registration = await session.call_tool("how_to_register", {})
        assert not registration.isError
        print("how_to_register: OK")
        result = await session.call_tool("find_tasks", {})
        assert not result.isError
        tasks = result.structuredContent["data"]["tasks"]
        assert isinstance(tasks, list)
        print("find_tasks count:", len(tasks))

if __name__ == "__main__":
    asyncio.run(main())
