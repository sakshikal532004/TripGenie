from typing import Annotated, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from backend.schemas import TravelPlan


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    final_plan: Optional[TravelPlan]