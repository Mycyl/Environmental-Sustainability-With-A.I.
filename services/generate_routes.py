import requests
import random
import time
import csv
import os

# CONFIGURATION
ORS_API_KEY = 'YOUR_ORS_API_KEY'  # <-- Replace with your API key
NUM_ROUTES_NEEDED = 100  # How many successful routes you want
OUTPUT_CSV = 'routes_data.csv'
WAIT_TIME_SECONDS = 1  # Wait between tries to avoid rate-limiting

# Area to pick random coordinates (example: Sydney area)
LAT_MIN, LAT_MAX = -34.0, -33.7
LON_MIN, LON_MAX = 151.0, 151.3

# Functions
def random_coord():
    """Generate a random (lat, lon) coordinate in the specified bounding box."""
    lat = random.uniform(LAT_MIN, LAT_MAX)
    lon = random.uniform(LON_MIN, LON_MAX)
    return lat, lon

def request_route(start_lat, start_lon, end_lat, end_lon):
    """Request a route from OpenRouteService."""
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    body = {
        "coordinates": [
            [start_lon, start_lat],  # Note: OpenRouteService uses (lon, lat) format
            [end_lon, end_lat]
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    return response

def parse_route(response_json):
    """Extract distance and duration from a valid route response."""
    distance_meters = response_json['features'][0]['properties']['summary']['distance']
    duration_seconds = response_json['features'][0]['properties']['summary']['duration']
    return distance_meters, duration_seconds

# MAIN
def main():
    collected_routes = []
    attempts = 0

    while len(collected_routes) < NUM_ROUTES_NEEDED:
        start_lat, start_lon = random_coord()
        end_lat, end_lon = random_coord()

        print(f"Trying route from ({start_lat}, {start_lon}) to ({end_lat}, {end_lon})...")

        response = request_route(start_lat, start_lon, end_lat, end_lon)
        attempts += 1

        if response.status_code == 200:
            route_json = response.json()
            try:
                distance, duration = parse_route(route_json)
                collected_routes.append({
                    'start_lat': start_lat,
                    'start_lon': start_lon,
                    'end_lat': end_lat,
                    'end_lon': end_lon,
                    'distance_meters': distance,
                    'duration_seconds': duration
                })
                print(f"Success! ({len(collected_routes)}/{NUM_ROUTES_NEEDED}) collected.")
            except Exception as e:
                print(f"Failed to parse route: {e}")
        else:
            print(f"Failed: status {response.status_code} ({response.text[:100]})")

        time.sleep(WAIT_TIME_SECONDS)

    # Save to CSV
    with open(OUTPUT_CSV, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=collected_routes[0].keys())
        writer.writeheader()
        writer.writerows(collected_routes)

    print(f"\nDone! {len(collected_routes)} routes saved to '{OUTPUT_CSV}' after {attempts} attempts.")

if __name__ == "__main__":
    main()