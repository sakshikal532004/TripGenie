import sys
from pathlib import Path

# Add TripGenie project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from mcp.server.mcpserver import MCPServer

from tools.weather import get_weather
from tools.currency import convert_currency
from tools.places import search_attractions
from tools.calculator import calculate


mcp = MCPServer(
    name="TripGenie MCP Server"
)


@mcp.tool()
def weather(city: str) -> str:
    """
    Get current weather information for a city.
    """
    return get_weather.invoke({
        "city": city
    })


@mcp.tool()
def currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> str:
    """
    Convert an amount from one currency to another.
    """
    return convert_currency.invoke({
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency
    })


@mcp.tool()
def places(
    destination: str,
    interest: str
) -> str:
    """
    Find attractions matching an interest in a destination.
    """
    return search_attractions.invoke({
        "destination": destination,
        "interest": interest
    })


@mcp.tool()
def calculator(expression: str) -> str:
    """
    Perform a mathematical calculation.
    """
    return calculate.invoke({
        "expression": expression
    })


if __name__ == "__main__":
    mcp.run()