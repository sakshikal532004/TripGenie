import asyncio

from langchain_core.tools import StructuredTool

from mcp_server.client import call_mcp_tool


def run_mcp_tool(tool_name: str, arguments: dict) -> str:
    """
    Synchronously call an MCP tool.
    """

    result = asyncio.run(
        call_mcp_tool(tool_name, arguments)
    )

    if hasattr(result, "content"):
        output = []

        for item in result.content:
            if hasattr(item, "text"):
                output.append(item.text)
            else:
                output.append(str(item))

        return "\n".join(output)

    return str(result)


def mcp_weather(city: str) -> str:
    """
    Get current weather through MCP.
    """
    return run_mcp_tool(
        "weather",
        {"city": city}
    )


def mcp_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> str:
    """
    Convert currency through MCP.
    """
    return run_mcp_tool(
        "currency",
        {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency
        }
    )


def mcp_places(
    destination: str,
    interest: str
) -> str:
    """
    Find attractions through MCP.
    """
    return run_mcp_tool(
        "places",
        {
            "destination": destination,
            "interest": interest
        }
    )


def mcp_calculator(expression: str) -> str:
    """
    Perform calculations through MCP.
    """
    return run_mcp_tool(
        "calculator",
        {
            "expression": expression
        }
    )


weather_mcp_tool = StructuredTool.from_function(
    func=mcp_weather,
    name="mcp_weather",
    description="Get current weather information using the TripGenie MCP server."
)


currency_mcp_tool = StructuredTool.from_function(
    func=mcp_currency,
    name="mcp_currency",
    description="Convert currencies using the TripGenie MCP server."
)


places_mcp_tool = StructuredTool.from_function(
    func=mcp_places,
    name="mcp_places",
    description="Find real attractions and places using the TripGenie MCP server."
)


calculator_mcp_tool = StructuredTool.from_function(
    func=mcp_calculator,
    name="mcp_calculator",
    description="Perform mathematical calculations using the TripGenie MCP server."
)


mcp_tools = [
    weather_mcp_tool,
    currency_mcp_tool,
    places_mcp_tool,
    calculator_mcp_tool,
]