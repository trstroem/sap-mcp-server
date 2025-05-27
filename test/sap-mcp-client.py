
from MCPClient import MCPClient

async def get_salesorders_list(client, top):
    try:
        await client.connect_to_sse_server(server_url="http://localhost:8080/sse")
        result = await client.session.call_tool("get_salesorders_list", {"top": top})
        content = result.content
        print(content)
    finally:
        await client.cleanup()
    return content

if __name__ == "__main__":
    import asyncio
    client = MCPClient()
    asyncio.run(get_salesorders_list(client, top=2))
   