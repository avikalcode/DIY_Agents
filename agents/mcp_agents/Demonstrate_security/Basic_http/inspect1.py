import json
import anyio
from mcp import Client

async def main():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        for t in (await client.list_tools()).tools:
            print("NAME       :", t.name)
            print("DESCRIPTION:", t.description)
            print("INPUT      :", json.dumps(t.input_schema, indent=2))
            print("OUTPUT     :", json.dumps(t.output_schema, indent=2))
            print("-" * 40)

anyio.run(main)

'''
output:
{
  "type": "object",
  "properties": { "todo_id": { "type": "integer", "title": "Todo Id" } },
  "required": ["todo_id"]
}
'''