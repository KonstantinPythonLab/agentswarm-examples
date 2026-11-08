"""Verify the standard-library client; print no member content."""
from example import MCPClient

client = MCPClient()
names = sorted(t["name"] for t in client.request("tools/list", {})["tools"])
assert names == ["find_tasks", "get_task", "how_to_register", "list_bounties"]
print("tools (4):", ", ".join(names))
client.call_tool("how_to_register")
print("how_to_register: OK")
tasks = client.call_tool("find_tasks")["tasks"]
assert isinstance(tasks, list)
print("find_tasks count:", len(tasks))
