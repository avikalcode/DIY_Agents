
# Connect to MCP server.
# Discover tools (list_tools()).
# Send user query to an LLM.
# LLM chooses the best tool and arguments.
# Call the MCP tool.
# Return result.
# Optionally loop until no more tools are needed.

import asyncio
import json
from openai import OpenAI

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_SERVER_URL = "http://localhost:8081/mcp"

client = OpenAI()

MODEL = "gpt-4.1-mini"

# -------get tool information dynamically
async def get_mcp_tools(session):
    response = await session.list_tools()

    tools = []

    for tool in response.tools:
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                },
            }
        )

    return tools


# -------agent Loop-----------
async def agent_loop(session, available_tools, user_query):

    messages = [
        {
            "role": "user",
            "content": user_query
        }
    ]

    while True:

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=available_tools,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Convert assistant message to dict for history
        messages.append(
            assistant_message.model_dump(
                exclude_none=True
            )
        )

        # if the llm response do not have tools calls then return
        if not assistant_message.tool_calls:
            return assistant_message.content

        # if llm response has tool call : Execute all tool calls
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads( tool_call.function.arguments)

            print( f"\n[Calling Tool] {tool_name}" )
            print( f"[Arguments] {arguments}" )

            # ---MCP Client calls the server tools remotely
            result = await session.call_tool(tool_name, arguments)

            tool_output = "\n".join(
                item.text
                for item in result.content
                if hasattr(item, "text")
            )

            print(f"[Result] {tool_output}")
            
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_output,
                }
            )

            
            # #---------final response sent to LLM so that it can give readable statememt by sending all response from query from tool message and tool output
            # final_response = client.chat.completions.create(
            #     model=MODEL,
            #     messages=[
            #         {
            #             "role": "user",
            #             "content": query
            #         },
            #         message,
            #         {
            #             "role": "tool",
            #             "tool_call_id": tool_call.id,
            #             "content": tool_output
            #         }
            #     ]
            # )



# --main----------
async def main():

    async with streamable_http_client(MCP_SERVER_URL) as (
        read_stream,
        write_stream,
        # _
    ): 
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            available_tools = await get_mcp_tools(session)
            
            print("\nConnected to MCP Server")
            print("\nAvailable Tools:")
            for tool in available_tools:
                print(f" - {tool['function']['name']}")

            
            while True:
                query = input("\nUser > ")
                if query.lower() in ["exit", "quit" ]:
                    break

                answer = await agent_loop(session, available_tools, query,)
                print("\nAssistant >", answer)
                   


# ---------start
if __name__ == "__main__":
    # mcp.run(transport="streamable-http")
    asyncio.run(main())