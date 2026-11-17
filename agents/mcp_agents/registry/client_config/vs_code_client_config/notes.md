**.vscode/mcp.json**
{
  "servers": {
    "task2-server": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}

### How to import into VS Code

- Open your project folder in VS Code.

- Open the Command Palette using Ctrl + Shift + P.

- Search for MCP: Open Workspace Folder Configuration.

- Paste the Client Config above.

- Save the file.

- Open the MCP Servers section.

- Start customer-support.

- Approve the server if prompted.

*Alternatively, use `MCP: Add Server` and `select HTTP`, then enter the endpoint.*


## Test your MCP tools in Codex

**Test 1: Order status**

```
Use the task2-server MCP server.

Call get_order_status with order_id = "ORD-1001".

Tell me the order status.

```

**Test 2: Knowledge base search**
```
Use the task2-server MCP server.

Call search_kb with question =
"How can I return a product?"

Show me the response.
```

**Test 3: Discover available tools**
```
Inspect the customer-support MCP server.

List all available tools, their input parameters,
and explain when each tool should be used.
```
