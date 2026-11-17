`static secret tokens`

- The server stopped talking to strangers. No token or a wrong token gets a 401 before any tool code runs.

- Every call now has an identity, alice or bob, which went into the audit log.

- The server fails closed. If the token variables aren’t set, it refuses to start.

# Terminal 1 (server): both tokens set, then
```
python gen_tokens.py
$env:TODO_TOKEN_ALICE = "..."
$env:TODO_TOKEN_BOB = "..."
```

``python mcp_server.py``

# Terminal 2 (client): only Alice's token set, same value as the server's
```
$env:TODO_TOKEN_ALICE="paste-alice-value"

python auth_mcp_client.py
```

**python basic_http_mcp_client.py** will throw error

# MCP inspector
```
npx @modelcontextprotocol/inspector

settings -> custom header

header key= Authorization
header value= Bearer <token of alice>
```

## to check

- All five steps work, and the server terminal shows an audit line for each call with by=alice.

- The “missing id” call returns an error result. If it raises an exception instead, tell me, because that changes how we handle errors.

- Unset the token, or change one character, and rerun. The client should now fail at connect or on the first call. Paste the exact exception, since I still need that from you.

- Try bad input, such as {"title": ""} or {"todo_id": -1}. The Stage 2.2 validation should still reject it, now behind the auth.