from pydantic import BaseModel
from typing import List


class Activity(BaseModel):
    time: str
    activity: str
    estimated_cost: float


class DayPlan(BaseModel):
    day: int
    activities: List[Activity]


class TravelPlan(BaseModel):
    destination: str
    duration_days: int
    travelers: int
    estimated_total_cost: float
    itinerary: List[DayPlan]