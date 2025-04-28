import random
import requests
from openrouteservice import Client
import os
from dotenv import load_dotenv

# Initialize OpenRouteService client
load_dotenv()
ORS_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")  # Replace with your actual API key
client = Client(key=ORS_API_KEY)

# Urban city centers with known coordinates
urban_cities = {
    "Paris": (151.2093, -33.8688)
}

def random_point_near(lat, lon, max_offset=0.02):
    """Generate a random point near a given lat/lon within a smaller range."""
    delta_lat = random.uniform(-max_offset, max_offset)
    delta_lon = random.uniform(-max_offset, max_offset)
    return (lat + delta_lat, lon + delta_lon)

def check_if_routable(lat, lon, search_radius=2000):
    """Check if the point is near a valid road by using isochrones."""
    try:
        result = client.isochrones(
            locations=[[lon, lat]], 
            range_type='time', 
            range=[1200],  # This is a 20-minute reachable area (in seconds)
            profile='driving-car'
        )
        if result['features'][0]['geometry'] is not None:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error in checking route: {e}")
        return False

def generate_routes(n_routes=10):
    """Generate random routes for a set number of routes."""
    routes = []
    for _ in range(n_routes):
        city = random.choice(list(urban_cities.keys()))
        base_lat, base_lon = urban_cities[city]

        start_point = (base_lat, base_lon)
        end_point = random_point_near(base_lat, base_lon)

        # Ensure the start and end points are near a road
        while not check_if_routable(start_point[0], start_point[1], search_radius=2000):
            print(f"Start point {start_point} not routable. Adjusting...")
            start_point = random_point_near(base_lat, base_lon)

        while not check_if_routable(end_point[0], end_point[1], search_radius=2000):
            print(f"End point {end_point} not routable. Adjusting...")
            end_point = random_point_near(base_lat, base_lon)

        routes.append({
            "city": city,
            "start_lat": round(start_point[0], 6),
            "start_lon": round(start_point[1], 6),
            "end_lat": round(end_point[0], 6),
            "end_lon": round(end_point[1], 6)
        })
    return routes

def get_route(start_coords, end_coords, profile="driving-car"):
    """Get route from OpenRouteService API."""
    try:
        print(f"Requesting route from {start_coords} to {end_coords}")
        route_data = client.directions(
            coordinates=[start_coords, end_coords],
            profile=profile,
            format='geojson'
        )
        
        # Check if the response contains valid route data
        if 'features' in route_data and len(route_data['features']) > 0:
            return route_data['features'][0]['geometry']['coordinates']
        else:
            print(f"No route found between {start_coords} and {end_coords}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
        return None
    except KeyError as e:
        print(f"KeyError occurred: {e}")
        return None

# Test route generation
routes = generate_routes(5)
for route in routes:
    print(route)

    start_coords = (route["start_lat"], route["start_lon"])
    end_coords = (route["end_lat"], route["end_lon"])

    route_data = get_route(start_coords, end_coords)
    
    if route_data:
        print(f"Route coordinates: {route_data}")
    else:
        print(f"Failed to generate route from {start_coords} to {end_coords}")
