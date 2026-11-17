import logging
from typing import Annotated

import jwt
from pydantic import AnyHttpUrl, Field, StringConstraints

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings

from .config import ISSUER, RESOURCE

logging.basicConfig(level=logging.INFO)
audit = logging.getLogger("audit")

MAX_TODOS = 100
# PUBLIC_KEY = open("public.pem").read()          # fail closed if missing

from pathlib import Path

# 1. Get the folder where THIS python file lives (version2_JWT/)
CURRENT_DIR = Path(__file__).resolve().parent
# 2. Go up one level (.parent) and into version2_JWT/public.pem
KEY_PATH = CURRENT_DIR / "public.pem"
PUBLIC_KEY = open(KEY_PATH).read()          # fail closed if missing

# ---------- input validation  ----------
Title = Annotated[str, StringConstraints(
    strip_whitespace=True, min_length=1, max_length=100,
    pattern=r"^[^\x00-\x1f\x7f]+$",
)]

TodoId = Annotated[int, Field(ge=1, le=1_000_000)]

# Client sends:  POST /mcp   Authorization: Bearer <JWT>
#         │
#         ▼
# 1. SDK auth layer (from token_verifier= and auth=)
#    └─ reads the Authorization header
#    └─ calls JwtVerifier.verify_token(token)      ← AUTHENTICATION POINT
#         ├─ returns None  → 401, request stops here
#         └─ returns AccessToken (who + scopes)
#    └─ checks required_scopes=["todo:read"]       ← baseline gate
#    └─ checks token's resource == server URL      ← validate_token_resource=True
#         │
#         ▼
# 2. The tool runs (add_todo / list_todos / remove_todo)
#    └─ _require("todo:write")                     ← AUTHORIZATION POINT
#         ├─ missing scope → ToolError, tool stops
#         └─ ok → returns the user's name for per-user data

# ---------- authentication: JWT verification ----------
# extract the 
# -- claims from the JWT token, 
# -- verify the signature, 
# -- and check the standard claims (exp, iat, sub, aud, iss) 
# to ensure the token is valid and not expired. 
# If valid, return an AccessToken object with the relevant information.
class JwtVerifier(TokenVerifier):
    
    async def verify_token(self, token: str) -> AccessToken | None:
        
        try:
            claims = jwt.decode(
                token, 
                PUBLIC_KEY,
                algorithms=["RS256"],                 # pinned: no "none", no HS256 tricks
                audience=RESOURCE, 
                issuer=ISSUER,     # minted by the auth server, not the client
                options={"require": 
                            [
                                "exp",  # xpiration time, 
                                "iat",  # issued at time, , aud -- , iss -- 
                                "sub",  # subject (user ID)
                                "aud",  # audience (intended recipient)
                                "iss"   # issuer (who issued the token)
                            ]
                        },   # fail closed if any of these claims are missing
                                                                            
            )

        except jwt.InvalidTokenError as e:
            audit.warning("token rejected: %s", type(e).__name__)  # reason logged, never the token
            return None
        
        return AccessToken(
            token=token,
            client_id=claims["sub"],
            scopes=claims.get("scope", "").split(),
            resource=claims["aud"],
        )

# ---------defining the MCPServer with authentication settings, including the token verifier and required scopes
# 1. Unauthenticated Request: An MCP client tries to call a tool on "Todo" without a token.
# 2. Discovery: The MCP server blocks the request (401) and uses AuthSettings to tell the client: "Go get a token from ISSUER specifically for RESOURCE with the todo:read scope."
# 3. Authentication: The user logs into ISSUER, which signs a JWT (e.g., using RS256) containing aud: RESOURCE and scope: "todo:read".
# 4. Verification: The client retries the MCP request with the JWT. JwtVerifier() verifies the signature against ISSUER's public key, confirms aud == RESOURCE, checks for "todo:read", and grants access.
mcp = MCPServer(
    "Todo",
    token_verifier=JwtVerifier(),   # Plugs in the verification logic (like RS256 signature verification). 
                                    # When a client sends a request with Authorization: Bearer <token>, 
                                    # the mcp serve uses this JwtVerifier to validate the token.
                                    # -  decodes the JWT, 
                                    # - checks its expiration, 
                                    # - and verifies its cryptographic signature using the Authorization Server's public key
    
    auth=AuthSettings( # Configures the OAuth security rules and automatically exposes a standard metadata endpoint (/.well-known/oauth-protected-resource) so MCP clients know how to authenticate.
        issuer_url=AnyHttpUrl(ISSUER), # Identifies the trusted Authorization Server (e.g., Auth0, Keycloak, Okta) that minted the token. If a client connects without a token, the MCP server returns a 401 Unauthorized response pointing the client to this URL to log in.
        resource_server_url=AnyHttpUrl(RESOURCE), # Defines the canonical public URL of this specific MCP server (e.g., https://api.example.com/mcp). 
        required_scopes=["todo:read"], # Sets the baseline permission level. Every incoming JWT must contain "todo:read" inside its scope claim, or the request is rejected (typically with an HTTP 403 insufficient scope error).
        validate_token_resource=True, # It checks the JWT's aud (audience) claim to ensure the token was specifically issued for this Todo server (RESOURCE) and isn't a stolen or reused token meant for a different API.
    ),
)

# ---------- authorization: per-tool scopes (2.4) ----------
# calles by each tool to check if the current request has a valid access token and whether it includes the required scope for the requested operation.
# If the token is missing or does not have the necessary scope, it raises a ToolError, effectively denying access to the operation. 
# This ensures that only authorized users can perform specific actions based on their granted permissions.
def _require(scope: str) -> str:
    tok = get_access_token() # get the AccessToken object from the request context, which was set by the JwtVerifier during token verification
    
    if tok is None:
        raise ToolError("Not authenticated.")
    
    if scope not in tok.scopes:
        audit.warning("DENIED user=%s needs=%s", tok.client_id, scope)
        raise ToolError(f"Insufficient scope: '{scope}' required.")
    
    return tok.client_id

# ---------- per-user state ----------
todos: dict[str, dict[int, str]] = {}
next_ids: dict[str, int] = {}

# todos    = {"alice": {1: "Buy milk"}}
# next_ids = {"alice": 2}

# todos    = {"alice": {1: "Buy milk", 2: "Call dentist"}}
# next_ids = {"alice": 3}

# todos    = {
#     "alice": {1: "Buy milk", 2: "Call dentist"},
#     "bob":   {1: "Learn MCP"},
# }
# next_ids = {"alice": 3, "bob": 2}

# ---------- tools ----------
@mcp.tool()
async def add_todo(title: Title) -> dict:
    """Add a todo item (1-100 characters, single line). Needs todo:write."""
    userid = _require("todo:write")

    # setdefault only uses {} when the key is missing. If the user already exists, it ignores the {} and returns the dict that’s already stored.
    user_todos  = todos.setdefault(userid, {})
    
    if len(user_todos) >= MAX_TODOS:
        raise ToolError(f"Todo limit of {MAX_TODOS} reached.")
    
    tid = next_ids.get(userid, 1)
    
    next_ids[userid] = tid + 1
    
    user_todos[tid] = title
    
    audit.info("add_todo user=%s id=%s", userid, tid)
    
    return {"id": tid, "title": title}


@mcp.tool()
async def list_todos() -> list[dict]:
    """List your todo items. Needs todo:read."""
    userid = _require("todo:read")
    user_todos = todos.get(userid, {})
    audit.info("list_todos user=%s", userid)

    #return [{"id": i, "title": t} for i, t in todos.get(userid, {}).items()]
    return [{"id": todo_id, "title": title} for todo_id, title in user_todos.items()]

    # [{"id": 2, "title": "Call dentist"}, {"id": 3, "title": "Pay rent"}]
    # client gets a CallToolResult : which has the data in two forms
    #   1. result.structured_content => {"result": [{"id": 2, "title": "Call dentist"}, {"id": 3, "title": "Pay rent"}]}
    #   2. result.content is a list of content blocks. The same data arrives as JSON text in a TextContent, which is what an LLM reads
    #   [{"type": "text", "text": "[{\"id\": 2, \"title\": \"Call dentist\"}, {\"id\": 3, \"title\": \"Pay rent\"}]"}]
    #   [TextContent(type="text", text='[{"id": 2, "title": "Call dentist"}, ...]')]

    # How to read it in  client
    #    r = await client.call_tool("list_todos", {})

    #   print(r.is_error)               # False
    #   print(r.structured_content)     # {"result": [...]}   (likely wrapped)

    #   items = r.structured_content["result"]
    #   for item in items:
    #       print(item["id"], item["title"])

@mcp.tool()
async def remove_todo(todo_id: TodoId) -> str:
    """Remove one of your todo items by id. Needs todo:write."""
    userid = _require("todo:write")
    user_todos  = todos.get(userid, {})
    
    if todo_id not in user_todos:
        raise ToolError(f"No todo with id {todo_id}. Call list_todos first.")
    
    audit.info("remove_todo user=%s id=%s", userid, todo_id)
    
    return f"Removed: {user_todos.pop(todo_id)}"

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
        max_request_body_size=16 * 1024,
    ) 