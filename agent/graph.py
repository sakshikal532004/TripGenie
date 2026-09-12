import sqlite3

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

from backend.config import GROQ_API_KEY

from agent.state import AgentState
from agent.finalizer import create_final_plan

from tools.calculator import calculate
from tools.weather import get_weather
from tools.currency import convert_currency
from tools.places import search_attractions

from rag.retriever import retrieve_travel_info

from mcp_server.langchain_tools import mcp_tools


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=GROQ_API_KEY,
    temperature=0
)


# ============================================================
# TOOLS
# ============================================================

tools = [
    calculate,
    get_weather,
    convert_currency,
    search_attractions,

    # RAG
    retrieve_travel_info,

    # MCP tools
    *mcp_tools,
]


# Give tools to LLM
llm_with_tools = llm.bind_tools(tools)


# ============================================================
# AGENT NODE
# ============================================================

def agent_node(state: AgentState):

    system_message = SystemMessage(
        content=(
            "You are TripGenie, an AI travel planning agent.\n\n"

            "Your job is to help users plan trips using "
            "the available tools.\n\n"

            "Available tools:\n"
            "- calculate: mathematical calculations\n"
            "- get_weather: current weather information\n"
            "- convert_currency: currency conversion\n"
            "- search_attractions: real attractions and places\n"
            "- retrieve_travel_info: travel knowledge base / RAG search\n"
            "- mcp_weather: weather through the MCP server\n"
            "- mcp_currency: currency conversion through the MCP server\n"
            "- mcp_places: attractions through the MCP server\n"
            "- mcp_calculator: calculations through the MCP server\n\n"

            "Tool rules:\n"
            "- Use calculate whenever a mathematical calculation is required.\n"
            "- Use get_weather whenever current weather information is requested.\n"
            "- Use convert_currency whenever currency conversion is requested.\n"
            "- Use search_attractions when attractions or places are requested.\n"
            "- Use retrieve_travel_info for destination knowledge and travel tips.\n"
            "- Use MCP tools when MCP access is needed.\n\n"

            "Do not invent current information when a tool is available.\n"
            "Use tools only when necessary."
        )
    )

    # Keep only the most recent messages to control token usage.
    recent_messages = state["messages"][-6:]

    response = llm_with_tools.invoke(
        [system_message] + recent_messages
    )

    return {
        "messages": [response]
    }


# ============================================================
# FINALIZER NODE
# ============================================================

def finalizer_node(state: AgentState):

    final_plan = create_final_plan(
        state["messages"]
    )

    return {
        "final_plan": final_plan
    }


# ============================================================
# TOOL NODE
# ============================================================

tool_node = ToolNode(tools)


# ============================================================
# CREATE GRAPH
# ============================================================

graph_builder = StateGraph(AgentState)

graph_builder.add_node(
    "agent",
    agent_node
)

graph_builder.add_node(
    "tools",
    tool_node
)

graph_builder.add_node(
    "finalizer",
    finalizer_node
)


# ============================================================
# EDGES
# ============================================================

graph_builder.add_edge(
    START,
    "agent"
)


def route_after_agent(state: AgentState):

    last_message = state["messages"][-1]

    if (
        hasattr(last_message, "tool_calls")
        and last_message.tool_calls
    ):
        return "tools"

    return "finalizer"


graph_builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools": "tools",
        "finalizer": "finalizer"
    }
)


graph_builder.add_edge(
    "tools",
    "agent"
)

graph_builder.add_edge(
    "finalizer",
    END
)


# ============================================================
# MEMORY
# ============================================================

conn = sqlite3.connect(
    "tripgenie_memory.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn)

checkpointer.setup()


# ============================================================
# COMPILE GRAPH
# ============================================================

graph = graph_builder.compile(
    checkpointer=checkpointer
)