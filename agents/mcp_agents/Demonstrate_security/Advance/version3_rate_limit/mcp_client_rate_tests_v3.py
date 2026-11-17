import anyio
import httpx2
from contextlib import asynccontextmanager
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from version2_JWT.config import RESOURCE
from version2_JWT.get_jwt_token import make_token

@asynccontextmanager
async def connect(token):
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx2.AsyncClient(headers=headers, timeout=httpx2.Timeout(15.0)) as http:
        async with Client(streamable_http_client(RESOURCE, http_client=http)) as c:
            yield c

async def main():
    RW = ["todo:read", "todo:write"]

    print("alice: 12 rapid writes (limit is 10/min)")
    async with connect(make_token("alice", RW)) as c:
        for i in range(1, 15):
            r = await c.call_tool("add_todo", {"title": f"item {i}"})
            status = "ok " if not r.is_error else "ERR"
            print(f"  write {i:2d}: {status} {'' if not r.is_error else r.content[0].text}") # If the call succeeded, it prints nothing after ok ; if it failed (because Alice hit the rate limit), it extracts and prints the error text from r.content[0].text (e.g., "Rate limit exceeded, retry in 60s").

        print("alice: reads still work (separate bucket)")
        r = await c.call_tool("list_todos", {})
        print("  list is_error =", r.is_error)
        

    print("bob: unaffected by alice's limit")
    async with connect(make_token("bob", RW)) as c:
        r = await c.call_tool("add_todo", {"title": "bob's item"})
        print("  bob write is_error =", r.is_error)

anyio.run(main)