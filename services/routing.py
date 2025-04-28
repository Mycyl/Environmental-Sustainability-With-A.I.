import os
import folium
import requests
from openrouteservice import convert
from dotenv import load_dotenv  # We will use the polyline library to decode the geometry

load_dotenv()
ORS_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")

def get_route(start_coords: tuple, end_coords: tuple, profile="driving-car", plot=False) -> dict:
    url = f"https://api.openrouteservice.org/v2/directions/{profile}"
    headers = {"Authorization": ORS_API_KEY}
    body = {
        "coordinates": [list(start_coords), list(end_coords)]
    }

    response = requests.post(url, json=body, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print(f"Response content: {response.text}")
        return None

    # Parse the response JSON
    data = response.json()

    # Check if 'routes' key exists in the response
    if 'routes' not in data:
        print("Error: 'routes' key is missing in the response.")
        print(f"Response data: {data}")
        return None

    # Extract the route and its details
    route = data["routes"][0]["summary"]
    encoded_polyline = data["routes"][0]["geometry"]
    coordinates = convert.decode_polyline(encoded_polyline)["coordinates"]

    # If plotting is enabled, create a map
    if plot:
        latlon_coords = [[lat, lon] for lon, lat in coordinates]  # convert lon-lat to lat-lon
        m = folium.Map(location=latlon_coords[0], zoom_start=14)
        folium.PolyLine(latlon_coords, color="blue", weight=5).add_to(m)
        folium.Marker(latlon_coords[0], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(latlon_coords[-1], tooltip="End", icon=folium.Icon(color="red")).add_to(m)
        m.save("route_map.html")
        print("✅ Map saved to 'route_map.html'")

    # Return route details
    return {
        "distance_meters": route["distance"],
        "duration_seconds": route["duration"],
        "coordinates": coordinates
    }
