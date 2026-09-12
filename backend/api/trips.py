from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from backend.config import GROQ_API_KEY
from agent.graph import graph

from backend.database.database import SessionLocal
from backend.database.models import Trip, Activity


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/trips",
    tags=["Trips"]
)


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# GROQ MODEL FOR FOLLOW-UP QUESTIONS
# ============================================================

ask_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=GROQ_API_KEY,
    temperature=0.3,
    max_tokens=700,
)


# ============================================================
# TRIP REQUEST
# ============================================================

class TripRequest(BaseModel):
    destination: str
    duration_days: int
    travelers: int
    budget: float
    interests: list[str]
    thread_id: str | None = None


# ============================================================
# ASK TRIPGENIE REQUEST
# ============================================================

class AskTripRequest(BaseModel):
    question: str
    destination: str
    duration_days: int
    travelers: int
    budget: float
    itinerary: dict | list | None = None


# ============================================================
# CREATE TRIP / AI TRIP PLANNER
# ============================================================

@router.post("/plan")
def plan_trip(
    request: TripRequest,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Create AI prompt
    # --------------------------------------------------------

    prompt = (
        f"Create a travel plan ONLY for {request.destination}. "
        f"Do not use another destination from previous conversations. "
        f"Trip duration: {request.duration_days} days. "
        f"Travelers: {request.travelers}. "
        f"Total budget: {request.budget} INR. "
        f"Interests: {', '.join(request.interests)}. "
        f"Calculate the budget per person per day, "
        f"check current weather for {request.destination}, "
        f"find attractions in {request.destination} matching the interests, "
        f"and use relevant travel knowledge when available."
    )

    # --------------------------------------------------------
    # Run LangGraph Agent
    # --------------------------------------------------------

    thread_id = request.thread_id or f"trip-{uuid4()}"

    result = graph.invoke(
        {
            "messages": [HumanMessage(content=prompt)],
            "final_plan": None
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    # --------------------------------------------------------
    # Get structured TravelPlan
    # --------------------------------------------------------

    final_plan = result["final_plan"]

    # --------------------------------------------------------
    # Enforce user budget
    # --------------------------------------------------------

    final_plan.estimated_total_cost = request.budget

    # --------------------------------------------------------
    # Save Trip to PostgreSQL
    # --------------------------------------------------------

    trip = Trip(
        destination=final_plan.destination,
        duration_days=final_plan.duration_days,
        travelers=final_plan.travelers,
        budget=final_plan.estimated_total_cost
    )

    db.add(trip)

    db.commit()

    db.refresh(trip)

    # --------------------------------------------------------
    # Save Itinerary Activities
    # --------------------------------------------------------

    for day in final_plan.itinerary:

        for activity in day.activities:

            db_activity = Activity(
                trip_id=trip.id,
                day=day.day,
                time=activity.time,
                activity=activity.activity,
                estimated_cost=activity.estimated_cost
            )

            db.add(db_activity)

    db.commit()

    # --------------------------------------------------------
    # Return Response
    # --------------------------------------------------------

    return {
        "success": True,
        "trip_id": trip.id,
        "thread_id": thread_id,
        "data": final_plan.model_dump()
    }


# ============================================================
# ASK TRIPGENIE
# ============================================================

@router.post("/ask")
def ask_tripgenie(
    request: AskTripRequest
):

    itinerary_text = str(request.itinerary)

    prompt = f"""
You are TripGenie, an AI travel assistant.

The user already has this travel plan:

Destination: {request.destination}
Duration: {request.duration_days} days
Travelers: {request.travelers}
Budget: ₹{request.budget}

Current itinerary:
{itinerary_text}

User's question:
{request.question}

Answer the user's question specifically about this trip.

IMPORTANT:
- Keep the answer concise and useful.
- Keep the destination unchanged.
- Use the existing itinerary as context.
- Give practical travel-planning advice.
- Do not invent current weather information.
- Do not claim that you changed the itinerary unless you actually changed it.
- Use simple and friendly language.
"""

    response = ask_llm.invoke(prompt)

    return {
        "success": True,
        "answer": response.content
    }


# ============================================================
# GET ALL TRIPS
# ============================================================

@router.get("/")
def get_trips(
    db: Session = Depends(get_db)
):

    trips = db.query(Trip).all()

    result = []

    for trip in trips:

        result.append({
            "id": trip.id,
            "destination": trip.destination,
            "duration_days": trip.duration_days,
            "travelers": trip.travelers,
            "budget": trip.budget
        })

    return {
        "success": True,
        "count": len(result),
        "trips": result
    }


# ============================================================
# GET SINGLE TRIP
# ============================================================

@router.get("/{trip_id}")
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Find Trip
    # --------------------------------------------------------

    trip = (
        db.query(Trip)
        .filter(Trip.id == trip_id)
        .first()
    )

    if not trip:

        return {
            "success": False,
            "message": "Trip not found"
        }

    # --------------------------------------------------------
    # Get Activities
    # --------------------------------------------------------

    activities = (
        db.query(Activity)
        .filter(Activity.trip_id == trip.id)
        .order_by(
            Activity.day,
            Activity.id
        )
        .all()
    )

    # --------------------------------------------------------
    # Group Activities by Day
    # --------------------------------------------------------

    itinerary = {}

    for activity in activities:

        if activity.day not in itinerary:

            itinerary[activity.day] = []

        itinerary[activity.day].append({

            "time": activity.time,

            "activity": activity.activity,

            "estimated_cost": activity.estimated_cost

        })

    # --------------------------------------------------------
    # Return Complete Trip
    # --------------------------------------------------------

    return {

        "success": True,

        "trip": {

            "id": trip.id,

            "destination": trip.destination,

            "duration_days": trip.duration_days,

            "travelers": trip.travelers,

            "budget": trip.budget,

            "itinerary": itinerary

        }

    }