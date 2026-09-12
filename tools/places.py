import requests
from langchain_core.tools import tool


@tool
def search_attractions(destination: str, interest: str) -> str:
    """
    Search for real attractions and places in a destination
    based on a user's interest.
    """

    try:
        interest = interest.lower().strip()

        # Step 1: Find destination coordinates
        geocode_url = "https://nominatim.openstreetmap.org/search"

        location_response = requests.get(
            geocode_url,
            params={
                "q": destination,
                "format": "json",
                "limit": 1,
            },
            headers={
                "User-Agent": "TripGenie/1.0",
            },
            timeout=10,
        )

        location_response.raise_for_status()

        location_data = location_response.json()

        if not location_data:
            return f"Could not locate destination: {destination}."

        latitude = float(location_data[0]["lat"])
        longitude = float(location_data[0]["lon"])

        # Step 2: Select OpenStreetMap category
        if "shopping" in interest or "shop" in interest:
            osm_query = f"""
[out:json][timeout:25];
(
  node["shop"](around:30000,{latitude},{longitude});
  way["shop"](around:30000,{latitude},{longitude});
);
out center tags;
"""

        elif "beach" in interest:
            osm_query = f"""
[out:json][timeout:25];
(
  node["natural"="beach"](around:30000,{latitude},{longitude});
  way["natural"="beach"](around:30000,{latitude},{longitude});
);
out center tags;
"""

        elif "museum" in interest:
            osm_query = f"""
[out:json][timeout:25];
(
  node["tourism"="museum"](around:30000,{latitude},{longitude});
  way["tourism"="museum"](around:30000,{latitude},{longitude});
);
out center tags;
"""

        elif "fort" in interest:
            osm_query = f"""
[out:json][timeout:25];
(
  node["historic"="fort"](around:30000,{latitude},{longitude});
  way["historic"="fort"](around:30000,{latitude},{longitude});
  node["historic"="castle"](around:30000,{latitude},{longitude});
  way["historic"="castle"](around:30000,{latitude},{longitude});
);
out center tags;
"""

        elif "park" in interest:
            osm_query = f"""
[out:json][timeout:25];
(
  node["leisure"="park"](around:30000,{latitude},{longitude});
  way["leisure"="park"](around:30000,{latitude},{longitude});
);
out center tags;
"""

        elif "restaurant" in interest or "food" in interest:
            osm_query = f"""
[out:json][timeout:25];
(
  node["amenity"="restaurant"](around:30000,{latitude},{longitude});
  way["amenity"="restaurant"](around:30000,{latitude},{longitude});
  node["amenity"="cafe"](around:30000,{latitude},{longitude});
  way["amenity"="cafe"](around:30000,{latitude},{longitude});
);
out center tags;
"""

        else:
            osm_query = f"""
[out:json][timeout:25];
(
  node["tourism"="attraction"](around:30000,{latitude},{longitude});
  way["tourism"="attraction"](around:30000,{latitude},{longitude});
  node["tourism"="viewpoint"](around:30000,{latitude},{longitude});
  way["tourism"="viewpoint"](around:30000,{latitude},{longitude});
);
out center tags;
"""

        # Step 3: Query Overpass API
        overpass_url = "https://overpass-api.de/api/interpreter"

        response = requests.post(
            overpass_url,
            data=osm_query,
            headers={
                "User-Agent": "TripGenie/1.0",
            },
            timeout=40,
        )

        response.raise_for_status()

        data = response.json()
        elements = data.get("elements", [])

        if not elements:
            return (
                f"No attractions found for "
                f"{interest} in {destination}."
            )

        # Step 4: Format results
        results = []
        seen_names = set()

        for place in elements:
            tags = place.get("tags", {})
            name = tags.get("name")

            if not name:
                continue

            name_key = name.lower()

            if name_key in seen_names:
                continue

            seen_names.add(name_key)

            lat = place.get("lat")
            lon = place.get("lon")

            if lat is None or lon is None:
                center = place.get("center", {})
                lat = center.get("lat")
                lon = center.get("lon")

            results.append(
                f"- {name} "
                f"(lat: {lat}, lon: {lon})"
            )

            if len(results) >= 5:
                break

        if not results:
            return (
                f"No named attractions found for "
                f"{interest} in {destination}."
            )

        return (
            f"Attractions related to '{interest}' "
            f"in {destination}:\n"
            + "\n".join(results)
        )

    except requests.RequestException as e:
        return f"Places API error: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"