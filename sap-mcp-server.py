from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
from starlette.responses import PlainTextResponse


# Initialize FastMCP server for tools (SSE)
mcp = FastMCP("sap_tools")

# Constants
SAP_ES5_DEMO_SYSTEM_URL= "https://sapes5.sapdevcenter.com/"
SAP_LIST_SALES_ORDERS_URL_FRAGMENT = f"{SAP_ES5_DEMO_SYSTEM_URL}sap/opu/odata/sap/ZSOCDS_SRV/SEPM_I_SalesOrder_E"

async def make_salesorders_list_request(url: str) -> dict[str, Any] | None:
    """Make a request to the SAP API with proper error handling."""
    headers = {

    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None



@mcp.tool()
async def get_salesorders_list(top: int) -> object:
    print(f"Top received in mcp get_salesorders_list: {top}")
    """Get a list of sales orders."""
    salesorders = await make_salesorders_list_request(f"{SAP_LIST_SALES_ORDERS_URL_FRAGMENT}?$top={top}&$format=json")
    print(f"Sales orders received: {salesorders}")
    if salesorders is None:
        return {"error": "Failed to fetch sales orders."}
    return salesorders

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )
        # Return a response to avoid NoneType error
        return PlainTextResponse("SSE connection closed.")

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server  # noqa: WPS437

    import argparse
    
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
