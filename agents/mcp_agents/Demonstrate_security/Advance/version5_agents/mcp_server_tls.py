import logging
import time
from collections import deque
from typing import Annotated

import jwt
from pydantic import AnyHttpUrl, Field, StringConstraints

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings

from version4_TLS.config import ISSUER, RESOURCE

# LOGGING--------

from contextlib import contextmanager
from version4_TLS.logging_setup import log_detail

# Use it inside each tool body
@contextmanager
def guarded(context: str):
    try:
        yield                                   # The yield keyword turns this function into a context manager generator. 
                                                # When it is used in :-- with guarded("some_action"):, Python pauses inside this try block, 
                                                # jumps out to execute the code placed inside the with block, and then returns.
    
    except ToolError:                           # This handles a known, expected error type,  (a mcp exception named ToolError)
        raise                                   # ready to be handled by a higher layer of the application
    
    except Exception as e:                      #This is the global fallback catcher. If any other unexpected bug or crash occurs 
                                                # (like a database disconnect, a NullPointer, or a math error), this block catches it (Exception as e).
        ref = log_detail(e, context)            # detail to the file only

        raise ToolError(f"Internal error. Reference: {ref}") from None  # secure way to raise a modified, user-safe error while completely wiping away the internal technical crash history (traceback).
                                                                        #It is used to prevent Information Leakage
                                                                        # from None : Completely hide the original traceback history from this point forward
#--------------------------

#====================================same as version3 rate limit + JWT token=================================================
import sys
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("audit.log"),  # Guarantees you see logs even in subprocess tests
    ],
    force=True,  # Overrides any earlier logging setup
)
audit = logging.getLogger("audit")

MAX_TODOS = 100

from pathlib import Path

# 1. Get the folder where THIS python file lives (version1/)
CURRENT_DIR = Path(__file__).resolve().parent
# 2. Go up one level (.parent) and into version2_JWT/public.pem
KEY_PATH = CURRENT_DIR.parent / "version2_JWT" / "public.pem"
PUBLIC_KEY = open(KEY_PATH).read()          # fail closed if missing

# ---------- input validation (2.2) ----------
Title = Annotated[str, StringConstraints(
    strip_whitespace=True, min_length=1, max_length=100,
    pattern=r"^[^\x00-\x1f\x7f]+$",
)]

TodoId = Annotated[int, Field(ge=1, le=1_000_000)]

# ---------- authentication: JWT verification (2.4) ----------
class JwtVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            claims = jwt.decode(
                token, PUBLIC_KEY,
                algorithms=["RS256"],
                audience=RESOURCE, issuer=ISSUER,
                options={"require": ["exp", "iat", "sub", "aud", "iss"]},
            )
        except jwt.InvalidTokenError as e:
            audit.warning("token rejected: %s", type(e).__name__)
            return None
        return AccessToken(
            token=token,
            client_id=claims["sub"], # user id, e.g. "alice" or "bob"
            scopes=claims.get("scope", "").split(),
            resource=claims["aud"],
        )

mcp = MCPServer(
    "Todo",
    token_verifier=JwtVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(ISSUER),
        resource_server_url=AnyHttpUrl(RESOURCE),
        required_scopes=["todo:read"],
        validate_token_resource=True,
    ),
)

# ---------- rate limiting (v3) ----------
# sliding window rate limiter—a mechanism 
# used to control how many times an action (like an API request or login attempt) can happen within a rolling timeframe.
# allows a maximum number of limit calls within any window of seconds, tracked independently for each key (such as a user ID or IP address)
class SlidingWindowLimiter:
    """Allow at most `limit` calls per `window` seconds, per key."""
    def __init__(self, 
                 limit: int, 
                 time_frame: float):
        
        self.limit = limit # Stores the maximum allowed calls 
        
        self.time_frame = time_frame # Stores the time frame in seconds during which the calls are counted
        
        self._hits: dict[str, deque[float]] = {}
        # self._hits={
        #     "user_alice": deque([1042.15, 1043.80]),
        #     "user_bob": deque([1044.02])
        # }

    def check(self, key: str) -> float:
        """Return 0.0 if allowed (and record the call), else seconds to wait."""
        now = time.monotonic() # time.monotonic() to get a reliable timestamp that cannot jump backward if the system clock changes
        
        hits = self._hits.setdefault(key, deque()) # Looks up key in self._hits. If it exists, it grabs that user's existing deque of timestamps. If it doesn't exist yet, it creates a brand-new empty deque(), saves it under key, and returns it.

        # Remove timestamps that are outside the current sliding window
        #       eg your window is 10 seconds (self.window = 10.0), and the current time is now = 100.0.
        #       suppose a user previously made calls at 85.0, 88.0, and 94.0
        
        #       hits = deque([85.0, 88.0, 94.0])
        #       hits[0] = 85.0, which is less than now - self.window = 100.0 - 10.0 = 90.0, REMOVE it from the deque.
        #       Now hits = deque([88.0, 94.0]), and hits[0] = 88.0, which is still less than 90.0, REMOVE it as well.
        #       Now hits = deque([94.0]), and hits[0] = 94.0, which is greater than 90.0, so we stop removing.
        while hits and hits[0] <= now - self.time_frame:
            hits.popleft()

        # Wait time calculation: 
        # If the number of remaining timestamps in hits is greater than or equal to the limit, 
        # it means the user has exceeded the allowed number of calls within the sliding window. 
        # In this case, it calculates how long the user must wait before making another call. 
        # The wait time is determined by taking the oldest timestamp in hits (hits[0]), 
        # adding the window duration (self.time_frame), and subtracting the current time (now). 
        # This gives the time remaining until the oldest call falls outside the sliding window. 
        # The function returns this wait time, ensuring that it is at least 1.0 seconds to avoid returning a negative or zero value.
        
        # • self.limit = 3 (max 3 calls allowed)
        # • self.time_frame = 10.0 (10-second window)
        # • now = 100.0 (current time)
        # • hits = deque([92.0, 95.0, 98.0]) (3 active calls remain after the while loop cleanup)
        if len(hits) >= self.limit: # if number of calls in the current window is greater than or equal to the limit, 
            return max(hits[0] + self.time_frame - now, 1.0) # calculate how long to wait 92.0 + 10.0 - 100.0 = 2.0 seconds to wait before the next call is allowed.
        
        hits.append(now)
        
        return 0.0
    
read_limiter = SlidingWindowLimiter(limit=60, time_frame=60)    # 60 reads/minute/user
write_limiter = SlidingWindowLimiter(limit=10, time_frame=60)   # 10 writes/minute/user

# ---------- identity + rate limit + authorization (v2 + v3) ----------
def _require(scope: str, # "todo:write", "todo:read"
             limiter: SlidingWindowLimiter) -> str:
    
    tok = get_access_token() # Retrieve the access token from the current request context. This token contains information about the authenticated user and their permissions.
    
    if tok is None:
        raise ToolError("Not authenticated.")
    
    userid = tok.client_id

    try:
        retry_after = limiter.check(userid)
    except Exception:
        audit.exception("rate limiter failed; denying request")   # fail closed
        raise ToolError("Service temporarily unavailable.")
    
    if retry_after:
        audit.warning("RATE_LIMITED user=%s scope=%s retry_after=%.0fs",
                      userid, scope, retry_after)
        
        raise ToolError(f"Rate limit exceeded. Retry after {retry_after:.0f} seconds.")


    if scope not in tok.scopes:
        audit.warning("DENIED user=%s needs=%s", userid, scope)
        raise ToolError(f"Insufficient scope: '{scope}' required.")
    
    return userid

# ---------- per-user state ----------
todos: dict[str, dict[int, str]] = {}
next_ids: dict[str, int] = {}

# ---------- tools ----------

"""Add a todo item (1-100 characters, single line). Needs todo:write."""
@mcp.tool()
async def add_todo(title: Title) -> dict:
 
    with guarded("add_todo"):
        user = _require("todo:write", write_limiter)
        user_todos = todos.setdefault(user, {})
        
        if len(user_todos) >= MAX_TODOS:
            raise ToolError(f"Todo limit of {MAX_TODOS} reached.")
        
        todo_id = next_ids.get(user, 1)
        next_ids[user] = todo_id + 1
        user_todos[todo_id] = title
        
        audit.info("add_todo user=%s id=%s", user, todo_id)
        
        return {"id": todo_id, "title": title}


"""List your todo items. Needs todo:read."""
@mcp.tool()
async def list_todos() -> list[dict]:
   
    with guarded("list_todo"):
        user = _require("todo:read", read_limiter)
        user_todos = todos.get(user, {})
        
        audit.info("list_todos user=%s", user)
    
        # return [{"id": todo_id, "title": title} for todo_id, title in user_todos.items()]
        return 1


"""Remove one of your todo items by id. Needs todo:write."""
@mcp.tool()
async def remove_todo(todo_id: TodoId) -> str:
    
    with guarded("list_todo"):
        user = _require("todo:write", write_limiter)
        user_todos = todos.get(user, {})
        
        if todo_id not in user_todos:
            raise ToolError(f"No todo with id {todo_id}. Call list_todos first.")
        
        audit.info("remove_todo user=%s id=%s", user, todo_id)
        
        return f"Removed: {user_todos.pop(todo_id)}"

if __name__ == "__main__":
    # mcp.run(
    #     transport="streamable-http",
    #     host="127.0.0.1",
    #     port=8000,
    #     max_request_body_size=16 * 1024,
    # )
   
# ================version 4 TLS========================
    import uvicorn

    app = mcp.streamable_http_app(
        host="127.0.0.1",
        max_request_body_size=16 * 1024,
    )
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        ssl_keyfile="version4_TLS/certs/key.pem",
        ssl_certfile="version4_TLS/certs/cert.pem",
    )

# Design choices
# Order of checks: identity, then rate limit, then scope. Every attempt by a user counts, even denied ones, so a user can’t probe endlessly for free.
# Separate buckets. Writes (10/min) are tighter than reads (60/min), because writes change state. Exhausting writes doesn’t block listing.
# time.monotonic() is used instead of wall-clock time, so system clock changes can’t reset or extend a window.
# No lock is needed. check() has no await in it, and our tools are async, so on one event loop it runs atomically. In v2 a plain def tool would run in a worker thread and could race, which is why we kept tools async.
# Failure messages are generic (“Service temporarily unavailable”). The detail goes to the log.