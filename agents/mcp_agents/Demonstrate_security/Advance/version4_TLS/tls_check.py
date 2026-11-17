import socket
import ssl
import httpx2

from .config import RESOURCE
# from version2_JWT.get_jwt_token import make_token # this was using issuer audience as http instead of https, so it was failing to verify the token. The correct one is the one in the same folder as this file.
from .get_jwt_token import make_token

# 1. Does the server present a trusted certificate, and which TLS version?
ctx = ssl.create_default_context(cafile="version4_TLS/certs/cert.pem")

with socket.create_connection(("127.0.0.1", 8000)) as s:
    with ctx.wrap_socket(s, server_hostname="127.0.0.1") as t:
        print("TLS version :", t.version())
        print("Subject     :", t.getpeercert()["subject"])

# 2. Plain HTTP must no longer work
try:
    r = httpx2.get("http://127.0.0.1:8000/mcp", timeout=5)
    print("plain HTTP  : status", r.status_code, "<-- unexpected")
except Exception as e:
    print("plain HTTP  : refused ->", type(e).__name__)

# 3. HTTPS without a token must still be rejected
try:
    r = httpx2.get("https://127.0.0.1:8000/mcp", timeout=5, verify=ctx) # passed verify=ctx explicitly.
    print("HTTPS no token: status", r.status_code)
    print("  WWW-Authenticate:", r.headers.get("www-authenticate"))
except Exception as e:
    print("HTTPS no token: FAILED ->", type(e).__name__, ":", e)

# 4. Raw HTTPS requests: no token vs wrong token vs valid token
good = make_token("alice", ["todo:read", "todo:write"])
for label, headers in [
    ("no token",    {}),
    ("wrong token", {"Authorization": "Bearer not-a-real-token"}),
    ("valid token", {"Authorization": f"Bearer {good}"}),
]:
    try:
        r = httpx2.post(RESOURCE, json={}, headers=headers, timeout=5, verify=ctx)
        print(f"HTTPS {label:12s}: status {r.status_code}")
    except Exception as e:
        print(f"HTTPS {label:12s}: FAILED -> {type(e).__name__}: {e}")

# 4. A real MCP call over HTTPS with the token
import anyio
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

async def mcp_call():
    headers = {"Authorization": f"Bearer {good}"}
    async with httpx2.AsyncClient(
        headers=headers,
        verify=ctx,
        timeout=httpx2.Timeout(15.0)
        ) as http:

        async with Client(streamable_http_client(RESOURCE, http_client=http)) as c:
            tools = await c.list_tools()
            print("MCP tools   :", [t.name for t in tools.tools])
            
            r = await c.call_tool("list_todos", {})
            print("list_todos  : is_error =", r.is_error)

try:
    anyio.run(mcp_call)
except BaseException as e:
    subs = getattr(e, "exceptions", None) or [e]
    for x in subs:
        print("MCP call FAILED ->", type(x).__name__, ":", x)