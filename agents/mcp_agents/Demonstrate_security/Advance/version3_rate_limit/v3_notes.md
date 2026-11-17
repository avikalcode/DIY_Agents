# quick launch
```
cd Advance
python -m version3_rate_limit.mcp_server_v3
python -m version3_rate_limit.mcp_client_rate_tests_v3

```
## For MCP Inspector
npx @modelcontextprotocol/inspector http://127.0.0.1:8000/mcp --header "Authorization: Bearer <your JWT>"

OR
npx @modelcontextprotocol/inspector

- Transport Type	Streamable HTTP

- URL	http://127.0.0.1:8000/mcp

-- **Get a token for the Inspector**

server now rejects calls without a JWT. From the folder with get_et_token.py and private.pem:

```
cd advance
python -c "from version2.get_jwt_token import make_token; print(make_token('alice', ['todo:read','todo:write']))"
```
- Authentication / custom headers -	an `Authorization` header with the value `Bearer <your JWT>`

# Design choices

- A per-user sliding-window limit, separate buckets for reads and writes

- fails closed: if the limiter breaks, the request is denied

- use a deque, so expired hits are removed from the front cheaply

Order of checks: identity, then rate limit, then scope. Every attempt by a user counts, even denied ones, so a user can’t probe endlessly for free.

Separate buckets. Writes (10/min) are tighter than reads (60/min), because writes change state. Exhausting writes doesn’t block listing.

time.monotonic() is used instead of wall-clock time, so system clock changes can’t reset or extend a window.

No lock is needed. check() has no await in it, and our tools are async, so on one event loop it runs atomically. In v2 a plain def tool would run in a worker thread and could race, which is tools are kept async.

Failure messages are generic (“Service temporarily unavailable”). The detail goes to the log.

