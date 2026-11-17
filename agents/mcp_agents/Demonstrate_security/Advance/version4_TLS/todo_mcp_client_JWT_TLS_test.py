import anyio
import httpx2
from contextlib import asynccontextmanager

from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from .config import RESOURCE # resource server URL for the MCP server
from .get_jwt_token import make_token
from .tls_trust import TLS_CONTEXT
from .logging_setup import report

# Context manager for connecting to the MCP server
@asynccontextmanager
async def connect(token):
    headers = {"Authorization": f"Bearer {token}"}

    # httpx2 is checking against the Windows trust store; 
    # self-signed certificate isn’t in that store, so it’s rejected
    # In tls_check.py it worked because it was passed `verify=ctx` explicitly 
    async with httpx2.AsyncClient(     
        headers=headers,                
        timeout=httpx2.Timeout(15.0),
        # verify=TLS_CONTEXT,             # ---------------> trust our certificate explicitly : 
                                        #                  Alternative: trust it system-wide [ certutil -user -addstore Root certs\cert.pem ]
    ) as http:
        async with Client(streamable_http_client(RESOURCE, http_client=http)) as c:
            yield c

def denied_at(e):
    subs = getattr(e, "exceptions", None)
    if subs:
        for s in subs:
            yield from denied_at(s)
    else:
        yield e
         
# call_tool is a method of the Client class that sends a request to the MCP server to invoke a specific tool with the provided arguments. It returns a response object that contains information about the result of the tool invocation, including whether it was successful or if there was an error.
async def call(clnt, label, tool, args):
    res = await clnt.call_tool(tool, args)

    print(f"  [{label}] is_error={res.is_error} {res.structured_content or res.content}")


async def denied(label, token):
    try:
        async with connect(token) as c:
            await c.call_tool("list_todos", {})
        print(f"[{label}] ALLOWED  <-- unexpected!")
    except Exception as e:
        print(f"[{label}] DENIED at connect: {[type(x).__name__ for x in denied_at(e)]}")

async def main():
    RW = ["todo:read", "todo:write"]
    R=["todo:read"]
    
    # -----------1. Connect as Alice with read+write permissions---------------
    print("1) alice, read+write")
    alice_token_RW = make_token("alice", RW)
    
    try:

        async with connect(alice_token_RW) as client:
            # r = await client.call_tool("add_todo", {"title": "Learn MCP"})
            # print("add     :", r.structured_content)
            await call(client, "add", "add_todo", {"title": "alice secret"})
            
            # r = await client.call_tool("add_todo", {"title": "Add security"})
            # print("add     :", r.structured_content)

            # r = await client.call_tool("list_todos", {})
            # print("list    :", r.structured_content)
            await call(client, "list", "list_todos", {})

            # r = await client.call_tool("remove_todo", {"todo_id": 1})
            # print("remove  :", r.content)

        # ------------2. Connect as Alice with read-only permissions------------
        print("2) alice, read-only token")
        alice_token_R = make_token("alice", R)
        
        async with connect(alice_token_R) as c:
            await call(c, "list", "list_todos", {})
            await call(c, "add", "add_todo", {"title": "should fail"})
            await call(c, "remove", "remove_todo", {"todo_id": 1})

        # ------------3. Connect as Bob with read+write permissions----------------
        print("3) bob, read+write token")
        bob_token_RW = make_token("bob", RW)
        async with connect(bob_token_RW) as c:
            await call(c, "list", "list_todos", {})
            await call(c, "add", "add_todo", {"title": "bob secret"})
            await call(c, "remove", "remove_todo", {"todo_id": 1})

        # ------------4. Connect with bad tokens----------------
        print("4) bad tokens")
        await denied("expired", make_token("alice", RW, ttl=-10))
        await denied("wrong audience", make_token("alice", RW, aud="http://invalid.example/mcp"))
        good = make_token("alice", RW)
        await denied("tampered", good[:-4] + "AAAA")

    except Exception as e:
        report("Could not complete the request. Check the server and your credentials.",
            e, context="list_todos")

anyio.run(main)