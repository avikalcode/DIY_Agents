import anyio
from mcp import Client

URL = "http://127.0.0.1:8000/mcp"

async def main():
    async with Client(URL) as client:
        print((await client.list_tools()).tools[0].name)

        # add todo items
        await client.call_tool("add_todo", {"title": "Learn MCP"})
        await client.call_tool("add_todo", {"title": "Add security"})

        # list todo items
        r = await client.call_tool("list_todos", {})
        print("list:", r.structured_content)

        # remove a todo item
        r = await client.call_tool("remove_todo", {"todo_id": 1})
        print("remove:", r.content)

        # mcp server should return an error for a non-existent todo item
        r = await client.call_tool("remove_todo", {"todo_id": 99})
        print("bad id -> is_error:", r.is_error, r.content)

        r = await client.call_tool("list_todos", {})
        print("list:", r.structured_content)

anyio.run(main)