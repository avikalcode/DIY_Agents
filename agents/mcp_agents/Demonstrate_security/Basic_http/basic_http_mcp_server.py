# Expected differences
# Empty title, control characters, and negative id: rejected.
# 100 KB title: rejected, probably as an HTTP 413 from the body limit before it reaches your code. The client may raise an exception instead of returning is_error.
# Flood: stops at 100 todos. The remaining requests fail with the limit message.
# Injection text: still accepted. That’s correct for now, and Level 3 handles it.

from typing import Annotated
from pydantic import Field, StringConstraints

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

MAX_TODOS = 100
MAX_TITLE_LENGTH = 100

# Annotated type for the title parameter with constraints on length, whitespace, and allowed characters.
Title = Annotated[
    str,
    StringConstraints(
        max_length=MAX_TITLE_LENGTH,
        min_length=1,
        strip_whitespace=True,
        pattern=r"^[^\x00-\x1f\x7f]+$", # \x00-\x1f : A range of hexadecimal values representing ASCII control characters (from 0x00 to 0x1F). This includes unprintable codes like Null (\x00), Backspace (\x08), Tab (\x09), Line Feed/Newline (\x0A), and Carriage Return (\x0D).
        )
]

#annotated type for the todo_id parameter with constraints on its value (between 1 and 1,000,000).
TodoId = Annotated[int, Field(ge=1, le=1_000_000)]

mcp = MCPServer("Todo")

todos: dict[int, str] = {}   # in-memory store: id -> title
next_id = 1

# ==========without INPUT VALIDATION=============
# @mcp.tool()
# async def add_todo(title: str) -> dict:
#     """Add a todo item and return it."""
#     global next_id
#     todo = {"id": next_id, "title": title}
#     todos[next_id] = title
#     next_id += 1
#     return todo

# ==========with INPUT VALIDATION=============
@mcp.tool()
async def add_todo(title: Title) -> dict:
    """Add a todo item (1-100 characters, single line)."""
    global next_id
    if len(todos) >= MAX_TODOS:
        raise ToolError(f"Todo limit of {MAX_TODOS} reached.")
    todo = {"id": next_id, "title": title}
    todos[next_id] = title
    next_id += 1
    return todo


@mcp.tool()
async def list_todos() -> list[dict]:
    """List all todo items."""
    return [{"id": i, "title": t} for i, t in todos.items()]

@mcp.tool()
# async def remove_todo(todo_id: int) -> str:
async def remove_todo(todo_id: TodoId) -> str:
    """Remove a todo item by its id."""
    if todo_id not in todos:
        raise ToolError(f"No todo with id {todo_id}. Call list_todos first.")
    
    title = todos.pop(todo_id)
    
    return f"Removed: {title}"

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http", 
        host="127.0.0.1", 
        port=8000,
        max_request_body_size=16 * 1024,   # 16 KiB; SDK default is 4 MiB
        )