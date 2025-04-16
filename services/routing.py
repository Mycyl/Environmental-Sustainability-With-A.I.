import os
import requests
from dotenv import load_dotenv
import folium
import openrouteservice  # This is the key fix
from openrouteservice import convert

load_dotenv()
ORS_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")

def get_route(start_coords: tuple, end_coords: tuple, profile="driving-car", plot=False) -> dict:
    url = f"https://api.openrouteservice.org/v2/directions/{profile}"
    headers = {"Authorization": ORS_API_KEY}
    body = {
        "coordinates": [list(start_coords), list(end_coords)]
    }

    response = requests.post(url, json=body, headers=headers)
    data = response.json()

    route = data["routes"][0]["summary"]
    encoded_polyline = data["routes"][0]["geometry"]
    coordinates = convert.decode_polyline(encoded_polyline)["coordinates"]

    if plot:
        latlon_coords = [[lat, lon] for lon, lat in coordinates]  # convert lon-lat to lat-lon
        m = folium.Map(location=latlon_coords[0], zoom_start=14)
        folium.PolyLine(latlon_coords, color="blue", weight=5).add_to(m)
        folium.Marker(latlon_coords[0], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(latlon_coords[-1], tooltip="End", icon=folium.Icon(color="red")).add_to(m)
        m.save("route_map.html")
        print("✅ Map saved to 'route_map.html'")

    return {
        "distance_meters": route["distance"],
        "duration_seconds": route["duration"],
        "coordinates": coordinates
    }

# Test call
print(get_route((151.2093, -33.8688), (151.2152, -33.8671), plot=True))