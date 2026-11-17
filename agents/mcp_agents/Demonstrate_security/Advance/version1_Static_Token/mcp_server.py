import hmac 
import logging
import os
from typing import Annotated

from pydantic import AnyHttpUrl, Field, StringConstraints

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings

logging.basicConfig(level=logging.INFO)
audit = logging.getLogger("audit")

RESOURCE = "http://127.0.0.1:8000/mcp"
MAX_TODOS = 100

# ---------- input validation ----------
Title = Annotated[
    str, 
    StringConstraints(
        strip_whitespace=True, 
        min_length=1, 
        max_length=100,
        pattern=r"^[^\x00-\x1f\x7f]+$",
    )
]

TodoId = Annotated[
    int, 
    Field(ge=1, le=1_000_000)
    ]

# ---------- authentication  ----------
def _load_tokens() -> dict[str, AccessToken]:
    
    tokens: dict[str, AccessToken] = {}
    
    for env_name, client_id in [("TODO_TOKEN_ALICE", "alice"), ("TODO_TOKEN_BOB", "bob")]:
        client_secret = os.environ.get(env_name)
        
        if not client_secret:
            raise RuntimeError(f"{env_name} is not set")   # fail closed : If a token env var is missing, the server refuses to start instead of running open.

        # create access token for specific client using the client_secret, client_id, and required scopes
         
        tokens[client_secret] = AccessToken(
            token=client_secret,
            client_id=client_id,
            scopes=["todo:use"], 
            resource=RESOURCE,
        )
    return tokens
    # {
    # "SECRET_STRING_FROM_ALICE_ENV": AccessToken1   
    # "SECRET_STRING_FROM_BOB_ENV": AccessToken2
    # }

# class that verifies tokens against the loaded tokens from environment variables
class EnvTokenVerifier(TokenVerifier):
    def __init__(self, tokens: dict[str, AccessToken]):
        self._tokens = tokens

    async def verify_token(self, token: str) -> AccessToken | None:
        
        match = None
        # self._tokens = {
        #     "abc123_secret_string": AccessToken(user_id="user_42", scopes=["read", "write"]),
        #     "xyz789_secret_string": AccessToken(user_id="user_99", scopes=["read"]),
        # }
        for key, value in self._tokens.items(): # key is the token string, value is the AccessToken object
            # constant-time compare; no early exit : 
            # It compares every single byte of both strings regardless of where a mismatch occurs, ensuring it always takes the exact same amount of time to fail.
            # Standard comparison (== or dict lookup) fails fast: 
            # If a stored token is "abcde" and an attacker sends "xbcde", 
            # Python stops checking at the very first character ('x' != 'a'). If the attacker sends "axcde", it checks two characters before stopping, taking a few nanoseconds longer. By measuring response times over thousands of requests, attackers can guess a secret token one character at a time.
            if hmac.compare_digest(token.encode(), value.encode()):  # when hmac.compare_digest returns True, the loop does not return access immediately
                match = value                                       # It assigns match = access and finishes iterating through all remaining tokens in self.tokens
                                                                     # If it exited early, an attacker could measure response times to figure out how many tokens are stored in your system or where in the dictionary a valid token sits
        return match                                                 

# -------defining the MCPServer with authentication settings, including the token verifier and required scopes
mcp = MCPServer(
    "Todo",
    token_verifier=EnvTokenVerifier(_load_tokens()),

    auth=AuthSettings(
        issuer_url=AnyHttpUrl("http://127.0.0.1:9000"),  # placeholder: no auth server yet
        resource_server_url=AnyHttpUrl(RESOURCE),
        required_scopes=["todo:use"],
        validate_token_resource=True, # means a token must be issued for this exact server URL
    ),
)

def _who() -> str:
    tok = get_access_token()
    return tok.client_id if tok else "unknown"

# ---------- app state ----------
todos: dict[int, str] = {}
next_id = 1


# ---------- tools ----------
@mcp.tool()
async def add_todo(title: Title) -> dict:
    """Add a todo item (1-100 characters, single line)."""
    global next_id
    
    audit.info("add_todo by=%s", _who())
    
    if len(todos) >= MAX_TODOS:
        raise ToolError(f"Todo limit of {MAX_TODOS} reached.")
    
    todo = {"id": next_id, "title": title}
    
    todos[next_id] = title
    
    next_id += 1
    
    return todo


@mcp.tool()
async def list_todos() -> list[dict]:
    """List all todo items."""
    
    audit.info("list_todos by=%s", _who())
    
    return [{"id": i, "title": t} for i, t in todos.items()]


@mcp.tool()
async def remove_todo(todo_id: TodoId) -> str:
    """Remove a todo item by its id."""
    audit.info("remove_todo id=%s by=%s", todo_id, _who())
    
    if todo_id not in todos:
        raise ToolError(f"No todo with id {todo_id}. Call list_todos first.")
    
    return f"Removed: {todos.pop(todo_id)}"


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
        max_request_body_size=16 * 1024, # the maximum allowable size for an incoming API or HTTP request body is exactly 16 Kilobytes (KB).
    )
