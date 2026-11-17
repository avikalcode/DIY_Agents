import os
import anyio
import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

URL = "http://127.0.0.1:8000/mcp"
TOKEN = os.environ.get("TODO_TOKEN_ALICE")   # set this in the client terminal

async def main():
    if not TOKEN:
        raise SystemExit("Set TODO_TOKEN_ALICE first")

    # headers = {"Authorization": f"Bearer {TOKEN}"}
    headers = {"X-Access-Token": TOKEN}  # custom header for token authentication

    # Using the "Authorization" header is the standard way to send a bearer token in HTTP requests. However, in this case, we are using a custom header "X-Access-Token" to send the token. This is a design choice and can be used for various reasons, such as avoiding conflicts with other authentication mechanisms or simply following a specific API design.
    async with httpx2.AsyncClient(headers=headers, timeout=httpx2.Timeout(15.0)) as http:
        
        transport = streamable_http_client(URL, http_client=http)
        
        async with Client(transport) as client:

            # 1. add
            r = await client.call_tool("add_todo", {"title": "Learn MCP"})
            print("add     :", r.structured_content)
            r = await client.call_tool("add_todo", {"title": "Add security"})
            print("add     :", r.structured_content)

            # 2. list
            r = await client.call_tool("list_todos", {})
            print("list    :", r.structured_content)

            # 3. remove
            r = await client.call_tool("remove_todo", {"todo_id": 1})
            print("remove  :", r.content)

            # 4. remove a missing id -> tool error, not a crash
            r = await client.call_tool("remove_todo", {"todo_id": 99})
            print("missing :", r.is_error, r.content)

            # 5. list again
            r = await client.call_tool("list_todos", {})
            print("list    :", r.structured_content)

anyio.run(main)