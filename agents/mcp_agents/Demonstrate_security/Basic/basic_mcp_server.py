# from mcp.server.fastmcp import FastMCP
from mcp.server.mcpserver import MCPServer

# mcp = FastMCP("Demo")
basic_server = MCPServer("Demo")

@basic_server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    basic_server.run(transport="stdio")