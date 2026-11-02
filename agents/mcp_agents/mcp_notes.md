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
python app.py

--------Terminal 3:
test:
poweshell use 'curl.exe' instead of `curl'
curl --get http://localhost:8080/ask --data-urlencode "message=Create a task called Prepare lecture notes"
curl --get http://localhost:8080/ask --data-urlencode "message=List my tasks"
curl --get http://localhost:8080/ask --data-urlencode "message=Complete the task Prepare lecture notes"
```

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
