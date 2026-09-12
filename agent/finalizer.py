import json
import re

from langchain_groq import ChatGroq
from pydantic import ValidationError

from backend.config import GROQ_API_KEY
from backend.schemas import TravelPlan


# ============================================================
# GROQ MODEL
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=GROQ_API_KEY,
    temperature=0,
    max_tokens=4000,
)

json_llm = llm.bind(
    response_format={"type": "json_object"}
)


# ============================================================
# FINAL TRAVEL PLAN GENERATOR
# ============================================================

def create_final_plan(messages):

    # --------------------------------------------------------
    # Extract useful messages
    # --------------------------------------------------------

    useful_messages = []
    user_request = ""

    for message in messages:

        message_type = getattr(message, "type", "")
        content = getattr(message, "content", "")

        # Get the first human request
        if message_type == "human" and not user_request:
            user_request = str(content)

        # Keep human + tool results
        if message_type in ["human", "tool"]:

            if isinstance(content, str):

                useful_messages.append(
                    f"{message_type.upper()}: {content[:3000]}"
                )

    context = "\n\n".join(useful_messages)

    # --------------------------------------------------------
    # Extract requested budget
    # --------------------------------------------------------

    requested_budget = None

    budget_match = re.search(
        r"total budget is\s+([\d,]+(?:\.\d+)?)\s+INR",
        user_request,
        re.IGNORECASE
    )

    if budget_match:

        requested_budget = float(
            budget_match.group(1).replace(",", "")
        )

    # --------------------------------------------------------
    # Extract requested destination
    # --------------------------------------------------------

    requested_destination = None

    destination_match = re.search(
        r"Plan a trip to\s+(.+?)\s+for\s+\d+\s+days",
        user_request,
        re.IGNORECASE
    )

    if destination_match:

        requested_destination = (
            destination_match.group(1).strip()
        )

    # --------------------------------------------------------
    # Extract requested duration
    # --------------------------------------------------------

    requested_duration = None

    duration_match = re.search(
        r"for\s+(\d+)\s+days",
        user_request,
        re.IGNORECASE
    )

    if duration_match:

        requested_duration = int(
            duration_match.group(1)
        )

    # --------------------------------------------------------
    # Extract requested travelers
    # --------------------------------------------------------

    requested_travelers = None

    travelers_match = re.search(
        r"for\s+\d+\s+days\s+for\s+(\d+)\s+travelers",
        user_request,
        re.IGNORECASE
    )

    if travelers_match:

        requested_travelers = int(
            travelers_match.group(1)
        )

    # --------------------------------------------------------
    # Safe defaults
    # --------------------------------------------------------

    if requested_duration is None:

        requested_duration = 3

    if requested_travelers is None:

        requested_travelers = 2

    # --------------------------------------------------------
    # Build dynamic day example
    # --------------------------------------------------------

    day_example = []

    for day_number in range(
        1,
        requested_duration + 1
    ):

        day_example.append(
            {
                "day": day_number,
                "activities": [
                    {
                        "time": "Morning",
                        "activity": "Short activity description",
                        "estimated_cost": 2000.0
                    },
                    {
                        "time": "Afternoon",
                        "activity": "Short activity description",
                        "estimated_cost": 2500.0
                    },
                    {
                        "time": "Evening",
                        "activity": "Short activity description",
                        "estimated_cost": 1500.0
                    }
                ]
            }
        )

    json_example = {
        "destination": (
            requested_destination
            or "Destination"
        ),
        "duration_days": requested_duration,
        "travelers": requested_travelers,
        "estimated_total_cost": (
            requested_budget
            if requested_budget is not None
            else 30000.0
        ),
        "itinerary": day_example
    }

    json_example_text = json.dumps(
        json_example,
        indent=4
    )

    # --------------------------------------------------------
    # Final planner prompt
    # --------------------------------------------------------

    prompt = f"""
You are TripGenie, an expert AI travel planner.

Create a realistic and useful travel itinerary using the
user's original request and available tool information.

============================================================
ORIGINAL USER REQUEST
============================================================

{user_request}

============================================================
REQUESTED TRIP DETAILS
============================================================

Destination:
{requested_destination}

Duration:
{requested_duration} days

Travelers:
{requested_travelers}

Budget:
{requested_budget} INR

============================================================
CRITICAL DURATION RULE
============================================================

The user requested EXACTLY {requested_duration} days.

You MUST create EXACTLY {requested_duration} itinerary days.

The itinerary MUST contain:

Day 1
Day 2
...
Day {requested_duration}

NEVER return fewer days.

NEVER return more days.

If the requested duration is 3 days, the itinerary MUST
contain exactly Day 1, Day 2 and Day 3.

If the requested duration is 5 days, the itinerary MUST
contain exactly Day 1, Day 2, Day 3, Day 4 and Day 5.

Every requested day MUST contain exactly 3 activities:

Morning
Afternoon
Evening

============================================================
IMPORTANT RULES
============================================================

1. The destination from the original user request is the
   source of truth.

2. The duration from the original user request is the
   source of truth.

3. The traveler count from the original user request is the
   source of truth.

4. The budget from the original user request is the
   source of truth.

5. NEVER replace the user's budget with a default value.

6. estimated_total_cost must be equal to the requested budget
   when a budget was provided.

7. The destination must NOT be replaced by information from
   an older conversation.

8. Create EXACTLY {requested_duration} itinerary entries.

9. Day numbers MUST start from 1.

10. Day numbers MUST end at {requested_duration}.

11. Create EXACTLY 3 activities for EVERY day.

12. Every day must contain:
    - Morning
    - Afternoon
    - Evening

13. Keep every activity description short and useful.

14. Write activity descriptions as one short sentence.

15. Maximum 12 words per activity description.

16. Avoid long explanations or paragraphs.

17. Use available weather information when provided.

18. Do not invent current weather information.

19. Use attraction information returned by tools when available.

20. Do not invent currency conversion results.

21. Estimated activity costs should NOT be zero unless the
    activity is genuinely free.

22. Use realistic estimated costs for food, transport,
    attractions and activities.

23. Make activities appropriate for the requested destination.

24. Do not use activities from another destination.

25. Return ONLY valid JSON.

26. Do not use markdown.

27. Do not add explanations outside the JSON.

28. Follow the TravelPlan structure exactly.

============================================================
REQUIRED JSON STRUCTURE
============================================================

The following example shows the EXACT number of days
required for this request.

{json_example_text}

============================================================
AVAILABLE TOOL INFORMATION
============================================================

{context}

============================================================
FINAL CHECK BEFORE RETURNING JSON
============================================================

Before returning the JSON, verify:

- Destination = {requested_destination}
- Duration = {requested_duration}
- Travelers = {requested_travelers}
- Budget = {requested_budget} INR
- Number of itinerary days = {requested_duration}
- First day = 1
- Last day = {requested_duration}
- Every day has exactly 3 activities
- No activity description exceeds 12 words
- No markdown
- Valid JSON only
"""

    # --------------------------------------------------------
    # Call Groq
    # --------------------------------------------------------

    response = json_llm.invoke(prompt)

    content = response.content

    # --------------------------------------------------------
    # Normalize response
    # --------------------------------------------------------

    if isinstance(content, list):

        content = "".join(
            item.get("text", "")
            if isinstance(item, dict)
            else str(item)
            for item in content
        )

    content = content.strip()

    # Remove markdown JSON fences
    if content.startswith("```json"):

        content = content[7:]

    elif content.startswith("```"):

        content = content[3:]

    if content.endswith("```"):

        content = content[:-3]

    content = content.strip()

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        data = json.loads(content)

    except json.JSONDecodeError as exc:

        raise ValueError(
            "Groq returned invalid JSON.\n\n"
            f"Response:\n{content}"
        ) from exc

    # --------------------------------------------------------
    # Validate TravelPlan schema
    # --------------------------------------------------------

    try:

        final_plan = TravelPlan.model_validate(data)

    except ValidationError as exc:

        raise ValueError(
            "Groq JSON does not match TravelPlan schema.\n\n"
            f"{exc}"
        ) from exc

    # ========================================================
    # ENFORCE USER REQUEST
    # ========================================================

    # --------------------------------------------------------
    # Enforce destination
    # --------------------------------------------------------

    if requested_destination:

        final_plan.destination = (
            requested_destination
        )

    # --------------------------------------------------------
    # Enforce duration
    # --------------------------------------------------------

    final_plan.duration_days = requested_duration

    # --------------------------------------------------------
    # Enforce travelers
    # --------------------------------------------------------

    final_plan.travelers = requested_travelers

    # --------------------------------------------------------
    # Enforce budget
    # --------------------------------------------------------

    if requested_budget is not None:

        final_plan.estimated_total_cost = (
            requested_budget
        )

    # ========================================================
    # FIX ITINERARY DAY COUNT
    # ========================================================

    current_days = {
        day.day: day
        for day in final_plan.itinerary
    }

    fixed_itinerary = []

    for day_number in range(
        1,
        requested_duration + 1
    ):

        # ----------------------------------------------------
        # Existing day returned by Groq
        # ----------------------------------------------------

        if day_number in current_days:

            day_plan = current_days[day_number]

            # Keep only first 3 activities
            activities = day_plan.activities[:3]

            # ------------------------------------------------
            # Add missing activities if Groq returned fewer
            # ------------------------------------------------

            default_times = [
                "Morning",
                "Afternoon",
                "Evening"
            ]

            while len(activities) < 3:

                activity_index = len(
                    activities
                )

                activities.append(
                    {
                        "time":
                            default_times[
                                activity_index
                            ],
                        "activity":
                            "Explore local attractions and enjoy the destination.",
                        "estimated_cost":
                            500.0
                    }
                )

            # ------------------------------------------------
            # Make sure each activity has a valid time
            # ------------------------------------------------

            for index, activity in enumerate(
                activities
            ):

                if not activity.time:

                    activity.time = (
                        default_times[index]
                    )

            day_plan.activities = activities

            fixed_itinerary.append(
                day_plan
            )

        # ----------------------------------------------------
        # Missing day
        # ----------------------------------------------------

        else:

            from backend.schemas import (
                DayPlan,
                Activity
            )

            fixed_itinerary.append(
                DayPlan(
                    day=day_number,
                    activities=[
                        Activity(
                            time="Morning",
                            activity=(
                                "Explore local attractions "
                                "and enjoy the destination."
                            ),
                            estimated_cost=500.0
                        ),
                        Activity(
                            time="Afternoon",
                            activity=(
                                "Enjoy local food and "
                                "experience the destination."
                            ),
                            estimated_cost=500.0
                        ),
                        Activity(
                            time="Evening",
                            activity=(
                                "Relax and explore "
                                "nearby evening attractions."
                            ),
                            estimated_cost=500.0
                        )
                    ]
                )
            )

    # --------------------------------------------------------
    # Replace itinerary with exact requested days
    # --------------------------------------------------------

    final_plan.itinerary = fixed_itinerary

    # ========================================================
    # REALISTIC ACTIVITY COSTS
    # ========================================================

    total_activity_count = sum(
        len(day.activities)
        for day in final_plan.itinerary
    )

    if (
        requested_budget is not None
        and total_activity_count > 0
    ):

        # Allocate around 60% of trip budget to
        # activities, food and local experiences.

        activity_budget = (
            requested_budget * 0.60
        )

        base_cost = (
            activity_budget /
            total_activity_count
        )

        for day in final_plan.itinerary:

            for activity in day.activities:

                calculated_cost = round(
                    base_cost / 100
                ) * 100

                activity.estimated_cost = float(
                    calculated_cost
                )

    # ========================================================
    # PREVENT ZERO-COST ACTIVITIES
    # ========================================================

    for day in final_plan.itinerary:

        for activity in day.activities:

            activity_text = (
                activity.activity.lower()
            )

            if (
                activity.estimated_cost == 0
                and "free" not in activity_text
                and "walk" not in activity_text
                and "relax" not in activity_text
            ):

                activity.estimated_cost = 500.0

    # ========================================================
    # FINAL SAFETY CHECK
    # ========================================================

    # Make absolutely sure the returned plan contains
    # exactly the requested number of days.

    if len(final_plan.itinerary) != requested_duration:

        raise ValueError(
            f"TripGenie generated "
            f"{len(final_plan.itinerary)} days, "
            f"but the user requested "
            f"{requested_duration} days."
        )

    # Make sure day numbers are sequential.

    expected_days = list(
        range(
            1,
            requested_duration + 1
        )
    )

    actual_days = [
        day.day
        for day in final_plan.itinerary
    ]

    if actual_days != expected_days:

        raise ValueError(
            "TripGenie generated invalid day numbers. "
            f"Expected {expected_days}, "
            f"got {actual_days}."
        )

    return final_plan