# from mcp.server.fastmcp import FastMCP
from mcp.server.mcpserver import MCPServer

# mcp = FastMCP("CustomerSupport")
mcp = MCPServer("customer-support")


@mcp.tool()
def get_order_status(order_id: str) -> str:
    return f"Order {order_id} is currently shipped."


@mcp.tool()
def search_kb(question: str) -> str:
    return f"Knowledge base answer for: {question}"


# if __name__ == "__main__":
#     mcp.run(transport="streamable-http")