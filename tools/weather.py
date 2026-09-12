import requests
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a city.

    Use this tool when the user asks about current weather,
    temperature, wind speed, or weather conditions for a destination.
    """

    try:
        # Step 1: Convert city name to coordinates
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_response = requests.get(
            geo_url,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if "results" not in geo_data:
            return f"Could not find the location: {city}"

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]
        location_name = location["name"]

        # Step 2: Get current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_response = requests.get(
            weather_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                "timezone": "auto"
            },
            timeout=10
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data["current"]

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind_speed = current["wind_speed_10m"]

        return (
            f"Current weather in {location_name}: "
            f"Temperature {temperature}°C, "
            f"Humidity {humidity}%, "
            f"Wind speed {wind_speed} km/h."
        )

    except requests.RequestException as e:
        return f"Weather API error: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"