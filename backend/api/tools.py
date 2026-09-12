from fastapi import APIRouter
from pydantic import BaseModel

from tools.weather import get_weather
from tools.currency import convert_currency
from tools.places import search_attractions
from tools.calculator import calculate


router = APIRouter(
    prefix="/api/tools",
    tags=["AI Tools"]
)


# ---------------- REQUEST MODELS ----------------

class WeatherRequest(BaseModel):
    city: str


class CurrencyRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


class PlacesRequest(BaseModel):
    destination: str
    interest: str


class CalculatorRequest(BaseModel):
    expression: str


# ---------------- WEATHER ----------------

@router.post("/weather")
def weather(request: WeatherRequest):

    result = get_weather.invoke({
        "city": request.city
    })

    return {
        "success": True,
        "data": result
    }


# ---------------- CURRENCY ----------------

@router.post("/currency")
def currency(request: CurrencyRequest):

    result = convert_currency.invoke({
        "amount": request.amount,
        "from_currency": request.from_currency,
        "to_currency": request.to_currency
    })

    return {
        "success": True,
        "data": result
    }


# ---------------- PLACES ----------------

@router.post("/places")
def places(request: PlacesRequest):

    result = search_attractions.invoke({
        "destination": request.destination,
        "interest": request.interest
    })

    return {
        "success": True,
        "data": result
    }


# ---------------- CALCULATOR ----------------

@router.post("/calculate")
def calculator(request: CalculatorRequest):

    result = calculate.invoke({
        "expression": request.expression
    })

    return {
        "success": True,
        "data": result
    }