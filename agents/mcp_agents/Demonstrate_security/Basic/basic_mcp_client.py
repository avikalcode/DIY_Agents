
import anyio

from mcp import Client # Client is a context manager that handles the connection to the MCP server. 
                       # It ensures that the connection is properly established and closed when done.

from basic_mcp_server import basic_server

# 1. Connects  2. List tools # 3. Call tool
async def main() -> None:
    async with Client(basic_server) as client: # # Approach 3: Using async with statement directly with Client
        tools_result = await client.list_tools()
        for tool in tools_result.tools:
            print(
                f"Tool: {tool.name}, Description: {tool.description}, "
                f"schema: {tool.input_schema}"
            )

        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Result of add(5, 3): {result}")
        print("content:", result.content)
        print("structured:", result.structured_content)


if __name__ == "__main__":
    anyio.run(main)

# from collections.abc import AsyncGenerator
# from contextlib import asynccontextmanager

# -----------Approach 1: Create a client instance to connect to the basic_server
# @asynccontextmanager
# async def getClient() -> AsyncGenerator[Client, None]:
#     async with Client(basic_server) as client:
#         yield client

# -----------Approach 2: Create a client instance to connect to the basic_server
## async def getClient():
##     client = Client(basic_server)
##     await client.__aenter__()
##     return client

#---------------async functions to simulate tasks------------------------
# Function 1: Simulates fetching data from an API
# async def fetch_data():
#     print("Fetch task: Starting API request...")
#     await anyio.sleep(2)  # Simulates network delay without blocking the event loop
#     print("Fetch task: Data retrieved successfully!")
#     return {"data": "sample"}

# Function 2: Simulates processing an image file
# async def process_image():
#     print("Process task: Starting image optimization...")
#     await anyio.sleep(1)  # Simulates processing time
#     print("Process task: Image optimized!")

# -------------------function that connects to the server, lists available tools, and calls a specific tool (add) with parameters.
#async def main() -> None:
    # ============approach 1 commented out, but it can be used as an alternative to connect to the server and call the tool.
    #  async with   getClient() as client: # # Approach 3: Using async with statement directly with Client
    #         tools_result = await client.list_tools()
    #         for tool in tools_result.tools:
    #             print(
    #                 f"Tool: {tool.name}, Description: {tool.description}, "
    #                 f"schema: {tool.input_schema}"
    #             )
    
    #         result = await client.call_tool("add", {"a": 5, "b": 3})
    #         print(f"Result of add(5, 3): {result}")
    #         print("content:", result.content)
    #         print("structured:", result.structured_content)

    # =======approach 2 are commented out, but they can be used as alternatives to connect to the server and call the tool.
    # client = await getClient()
    # try:
    #     tools_result = await client.list_tools()                                               # mcp
    #     for tool in tools_result.tools:
    #         print(f"Tool: {tool.name}, Description: {tool.description}, schema: {tool.input_schema}")

    #     # result = await client.invoke("add", a=5, b=3)
    #     result = await client.call_tool("add", {"a": 5, "b": 3})
    #     print(f"Result of add(5, 3): {result}")
    #     print("content:", result.content)
    #     print("structured:", result.structured_content)
    # finally:
    #     await client.__aexit__(None, None, None)

    # ============functions fetch_data and process_image are commented out, but they can be used to simulate concurrent tasks.
    # start_time = anyio.current_time()
    
    # # Create a task group to run functions concurrently
    # async with anyio.create_task_group() as tg:
    #     tg.start_soon(fetch_data)
    #     tg.start_soon(process_image)
        
    # # The block context manager automatically blocks until both tasks finish
    # execution_time = anyio.current_time() - start_time
    # print(f"\nAll tasks completed in {execution_time:.2f} seconds!")