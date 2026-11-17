##  Generate Registry Config

A registry configuration is different from a client configuration.

- Client Config tells an MCP client how to connect.

- Registry Config describes your MCP server so that a compatible registry or discovery service can list it.

The standardized MCP Registry manifest is called `server.json`

```

{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "com.abc/task2-server",
  "title": "task2 MCP Server",
  "description": "MCP server for customer order status and knowledge base searches.",
  "version": "1.0.0",
  "remotes": [
    {
      "type": "streamable-http",
      "url": "https://YOUR_PUBLIC_DOMAIN/mcp"
    }
  ]
}

```

Replace com.abc with a namespace you own and replace YOUR_PUBLIC_DOMAIN with your deployed server's hostname.

'**Important:** This is a registry manifest template, not a working connection to your current localhost server.

The official MCP Registry requires a publicly accessible remote server URL. 127.0.0.1 cannot be used as a published remote endpoint. 

For local development, use the Client Config instead.'

## How to import Registry Config into VS Code
There are two different scenarios.

### Scenario A: Your server is only running locally
Do not use Registry Config.

Instead:

1. Open VS Code.

2. Run MCP: Add Server.

3. Choose HTTP.

4. Enter http://127.0.0.1:8010/mcp.

Save and start the server.

### Scenario B: Your server is deployed publicly
If you deploy your MCP server to a public HTTPS endpoint:

1. Host your `server.json` manifest in your project.

2. Publish the manifest to a compatible MCP registry.

3. Verify your registry namespace and server metadata.

------- Open VS Code.

- Run MCP: Browse MCP Servers.

- Find your published server in the available registry or gallery.

- Select Install and review its connection details.

The official registry has a publishing process and namespace verification requirements. Merely creating server.json does not publish your server.

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

customer-support-mcp/
│
├── server2.py
├── main.py
├── requirements.txt
├── server.json
│
└── .vscode/
    └── mcp.json

