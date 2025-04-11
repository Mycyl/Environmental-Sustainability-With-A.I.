import os
import requests
from dotenv import load_dotenv

load_dotenv()
ORS_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")

def get_route(start_coords: tuple, end_coords: tuple, profile="driving-car") -> dict:
    """
    Fetch route data (distance, duration, geometry) from OpenRouteService API.
    
    Args:
        start_coords (tuple): (longitude, latitude)
        end_coords (tuple): (longitude, latitude)
        profile (str): routing profile ('driving-car', 'cycling-regular', etc.)
    
    Returns:
        dict: Route information including distance (meters) and duration (seconds)
    """
    url = f"https://api.openrouteservice.org/v2/directions/{profile}"
    headers = {"Authorization": ORS_API_KEY}
    body = {
        "coordinates": [list(start_coords), list(end_coords)],
        "format": "geojson"
    }

    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"OpenRouteService error: {response.text}")
    
    data = response.json()
    route = data["features"][0]["properties"]["summary"]

    return {
        "distance_meters": route["distance"],
        "duration_seconds": route["duration"],
        "geojson": data  # Optional: return full geometry for map rendering
    }