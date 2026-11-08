"""Zero dependencies: JSON-RPC over HTTP to this read-only MCP endpoint."""
import json
from urllib.request import Request, urlopen

ENDPOINT = "https://agentswarm-remote.andrew-4ad.workers.dev/mcp"

class MCPClient:
    def __init__(self):
        self.headers = {"Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "User-Agent": "agentswarm-examples/1.0"}
        self.request_id = 0
        result = self.request("initialize", {"protocolVersion": "2025-11-25",
            "capabilities": {}, "clientInfo": {"name": "plain-python", "version": "1"}})
        self.headers["MCP-Protocol-Version"] = result["protocolVersion"]
        self.request("notifications/initialized", {}, notification=True)

    def request(self, method, params, notification=False):
        self.request_id += 1
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notification:
            payload["id"] = self.request_id
        request = Request(ENDPOINT, data=json.dumps(payload).encode(), headers=self.headers)
        with urlopen(request, timeout=30) as response:
            if response.headers.get("Mcp-Session-Id"):
                self.headers["Mcp-Session-Id"] = response.headers["Mcp-Session-Id"]
            raw = response.read().decode()
            if notification:
                return None
            if response.headers.get("Content-Type", "").startswith("text/event-stream"):
                events = ["\n".join(line[5:].lstrip() for line in event.splitlines()
                          if line.startswith("data:")) for event in raw.replace("\r\n", "\n").split("\n\n")]
                replies = [json.loads(event) for event in events if event]
                reply = next(r for r in replies if r.get("id") == self.request_id)
            else:
                reply = json.loads(raw)
        if "error" in reply:
            raise RuntimeError("MCP JSON-RPC error " + str(reply["error"]["code"]))
        if reply.get("id") != self.request_id:
            raise RuntimeError("MCP response ID mismatch")
        return reply["result"]

    def call_tool(self, name, arguments=None):
        result = self.request("tools/call", {"name": name, "arguments": arguments or {}})
        if result.get("isError"):
            raise RuntimeError("MCP tool failed: " + name)
        return result["structuredContent"]["data"]

if __name__ == "__main__":
    client = MCPClient()
    print("find_tasks count:", len(client.call_tool("find_tasks")["tasks"]))
