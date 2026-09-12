import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server.server"],
)


async def call_mcp_tool(tool_name: str, arguments: dict):
    """
    Call a tool from the TripGenie MCP server.
    """

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments
            )

            return result


async def list_mcp_tools():
    """
    Get all tools available from the MCP server.
    """

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.list_tools()

            return result.tools


if __name__ == "__main__":

    tools = asyncio.run(list_mcp_tools())

    print("MCP tools available:")

    for tool in tools:
        print(f"- {tool.name}")