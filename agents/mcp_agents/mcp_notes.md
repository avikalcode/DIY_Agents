```
---------Terminal 1: 
cd taskServer
#python3 -m venv .venv
#.venv/bin/activate
pip install -e .
python server.py

------Terminal 2:
cd taskClient
#python3 -m venv .venv
#source .venv/bin/activate
pip install -e .
#cp .env.example .env

server:
python server.py

client
$env:OPENAI_API_KEY= ""
python app.py

--------Terminal 3:
test:
poweshell use 'curl.exe' instead of `curl'
curl --get http://localhost:8080/ask --data-urlencode "message=Create a task called Prepare lecture notes"
curl --get http://localhost:8080/ask --data-urlencode "message=List my tasks"
curl --get http://localhost:8080/ask --data-urlencode "message=Complete the task Prepare lecture notes"
```
## 1.  Generate Client Config and Registry Config

When building or documenting an MCP server for distribution,  provide two JSON schemas before translating them for Codex/Claude.

`Client Config (mcp.json / mcp_config.json)`: The standard portable JSON format used by Visual Studio, VS Code (.vscode/mcp.json), and Cursor.
```
json
{
  "mcpServers": {
    "task2-server": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

`Registry Config (server.json)`: Used to publish metadata to the official MCP Registry. It defines server's unique namespace, remote endpoint, and transport type.
```
json
{
  "name": "io.github.your-org/my-http-server",
  "description": "Remote HTTP MCP server for internal tools",
  "version": "1.0.0",
  "remotes": [
    {
      "transport_type": "streamable-http",
      "url": "https://example.com"
    }
  ]
}
```

## 2. Import from Registry Config or Client Config into Codex
### Option A: Import via CLI (Fastest for Unauthenticated or OAuth Servers)

codex mcp add task2-server --url "https://127.0.0.1/mcp"

**If the HTTP server uses OAuth, authenticate immediately after adding**
codex mcp login task2-server


### Option B: Manual Import into config.toml (Required for Custom Headers)

The codex mcp add command does not support passing custom HTTP headers directly. 

To import a client config that requires a Bearer token or API key, open your config.toml file (accessible via the Codex IDE panel under MCP Settings) and map the JSON fields to a [mcp_servers.<name>] block:

```
[mcp_servers.task2-server]
url = "https://127.0.0.1:8000/mcp"
http_headers = { "Authorization" = "Bearer YOUR_API_TOKEN" }
```
*(Note: If you are also using GitHub Copilot in Visual Studio 2022/2026 alongside Codex, Visual Studio natively reads .mcp.json or .vscode/mcp.json. You can keep your JSON client config for Visual Studio's built-in agent while maintaining `.codex/config.toml` in  the same repository for Codex.)*

## 3. Use HTTP MCP Server Tools in Codex (Visual Studio / VS Code)
Once configured, Codex automatically discovers and loads the remote tools whenever you start a session.

**1. Reload the Extension:** Save your config.toml file. If your IDE session was already open, reload the window or restart the Codex panel so it establishes the Streamable HTTP connection.

**2. Verify Connection and Tools:** Open the Codex chat panel in your IDE and run the slash command /mcp. This displays all active MCP servers, connection statuses, and the specific tools exposed by your HTTP endpoint.

**3. Invoke Tools in Prompts:** Ask Codex to perform a task that requires the external data or action. For example, prompt "Check the latest deployment logs using my-http-server" or explicitly reference the server name.

**4. Approve Execution:** Depending on your Codex approval policy in config.toml, Codex will either execute read-only HTTP tool calls automatically or prompt you in the IDE chat panel to approve the request before sending data to the remote endpoint.

- MCP Server : 

-- Tools

-- Resources (RAG)

-- Prompts

- MCP Client

**Dynamically Service Discovery :** `tools/list` -> Request from MCP client to MCP server to get all tools in MCP server

    MCP client ask MCP server about tools it has in certain format

    MCP server responses in `structured output` with the list of tools `[name + description that describes what tool does]`

    eg 
    ```
    {
        "name":"createTask",
        "description": "Creates a new task",
        "inputSchema": {
            "type":"object",
            "properties""{
                "title":{
                    "type":"string"
                }
            }

        }
    }
        
    MCP client passes that information along with context to LLM

**LLM structure response to Server**
{
    createtask:{
        title" "go to Gym"
    }
}

- Server calls MCP client to call "Create Task" function from MCP remote server

- MCP client calls MCP server , Server respond to MCP Client

- MCP client pass that information to LLM

- LLM pass information that task completyed to host server

`tools/call` -> client to server to invoke mcp function

`tools/list` -> client call to server to list all MCP function task 

# Server Dependency
```
Server Port - 8081

protocol - Streamable HTTP / Stdio

version - 1.0.0

server function name/parameter  annotation :

@McpTool (name = "name of tool", description = "create a new task")
function (@McpToolParam(
    description = "description of the parameter",
    required = true/false
) param1)

```
# Client

```
client port - 8080

server url = http://localhost:8081/mcp
```

## test
```
command : 
- taskServer % npx@modelcontextprotocol/inspector 
        --cli 
        --transport http 
        --method tools/list 

-- taskServer % npx@modelcontextprotocol/inspector 
        --cli 
        --transport http 
```


# Server 2 , Client 2 : Sample Conversation
```pip install mcp
python server2_app.py
```
### usage

```
User > what is the status of order 12345

[Calling MCP Tool] get_order_status
[Arguments] {'order_id': '12345'}

Assistant > Order 12345 is currently shipped.

LLM chooses:
get_order_status(
    order_id="12345"
)

MCP returns:
Order 12345 is currently shipped.

Assistant >
Your order 12345 has been shipped and is currently in transit.
```

### Production Improvement
For a customer-care RAG system building with Pinecone:
```
User
  ↓
OpenAI
  ↓
search_customer_kb
  ↓
MCP Server
  ↓
Pinecone
  ↓
Top K documents
  ↓
OpenAI generates answer
```

- JWT authentication using RS256.

- Public/private key-based authentication.

- User-level identity isolation.

- Scope-based authorization.

- Separate read/write rate limits.

- Input validation using Pydantic.

- Audit logging.

- Per-user limits on todo items.