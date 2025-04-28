import sys
import os
import time
from pprint import pprint

# Allow imports from the root folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

# Import your services
from services.routing import get_route
from services.pollution import get_pollution_data
from services.emissions import estimate_grid_emissions

# -------------------- CONFIG -------------------- #

# Simulation settings
start_location = (151.2093, -33.8688)  # Example: Sydney center
end_location = (151.2152, -33.8671)    # Example: Nearby destination
energy_capacity_kwh = 50.0             # EV battery capacity
initial_energy = 40.0                  # Starting energy in kWh
region_code = "AU"                     # Region code for emissions (Australia)

# Pollution thresholds
MAX_ALLOWED_AQI = 3  # 1 (good) to 5 (very bad)

# Charge strategy
MIN_CHARGE_THRESHOLD = 15  # If below 15 kWh, "recharge"

# -------------------- SIMULATION LOOP -------------------- #

def evaluate_route(route_info):
    """
    Evaluates the route based on pollution, energy consumption, and emissions.
    """
    total_pollution = 0
    total_emissions_grams = 0
    current_energy = initial_energy
    coordinates = route_info["coordinates"]
    step_distance_km = 0.5  # Assume 0.5km between points for simplicity
    energy_consumed_per_km = 0.2  # kWh/km (example for a Tesla Model 3)
    
    for idx, (lon, lat) in enumerate(coordinates):
        try:
            # Check pollution at current location
            pollution_data = get_pollution_data(lat, lon)
            aqi = pollution_data["aqi"]
            total_pollution += aqi
        except Exception as e:
            print(f"⚠️ Pollution data fetch failed: {e}")
            aqi = 5  # Assume worst case if API fails
            total_pollution += aqi
        
        # Simulate energy use per step
        energy_used = energy_consumed_per_km * step_distance_km
        current_energy -= energy_used
        
        # Estimate emissions
        try:
            emissions_response = estimate_grid_emissions(energy_used, region_code)
            emissions = emissions_response["co2e"] * 1000  # Convert to grams
            total_emissions_grams += emissions
        except Exception as e:
            print(f"⚠️ Emissions estimation failed: {e}")

        # If energy low, "recharge" (fake instant recharge for now)
        if current_energy <= MIN_CHARGE_THRESHOLD:
            current_energy = energy_capacity_kwh  # Recharge to full
            time.sleep(1)  # simulate charging time
    
    return total_pollution, total_emissions_grams, current_energy

def find_best_route():
    """
    Evaluates multiple routes and picks the best one based on pollution, emissions, and energy.
    """
    # Fetch multiple routes (e.g., 3 routes to compare)
    print("📍 Fetching routes...")
    route_options = []
    for i in range(3):  # Fetch 3 different routes for comparison
        route_info = get_route(start_location, end_location, profile="driving-car", plot=True)
        route_options.append(route_info)
    
    # Evaluate each route
    best_route = None
    best_pollution = float('inf')
    best_emissions = float('inf')
    
    for idx, route_info in enumerate(route_options):
        print(f"\n--- Evaluating route {idx + 1} ---")
        total_pollution, total_emissions_grams, final_energy = evaluate_route(route_info)
        
        print(f"🌫️ Total pollution for route {idx + 1}: {total_pollution}")
        print(f"♻️ Total emissions for route {idx + 1}: {total_emissions_grams:.2f} grams CO2e")
        print(f"🔋 Final energy for route {idx + 1}: {final_energy:.2f} kWh")
        
        # Check if this route is better
        if total_pollution < best_pollution or (total_pollution == best_pollution and total_emissions_grams < best_emissions):
            best_pollution = total_pollution
            best_emissions = total_emissions_grams
            best_route = route_info
    
    print("\n✅ Best route found!")
    pprint(best_route)
    return best_route

# -------------------- MAIN -------------------- #

def simulate_drive():
    print("🚗 Starting EV simulation...\n")
    
    # Step 1: Find the best route based on pollution and emissions
    best_route = find_best_route()

    # Step 2: Simulate the drive on the best route
    print("🚗 Simulating drive on the best route...")
    total_pollution, total_emissions_grams, current_energy = evaluate_route(best_route)

    print("\n✅ Simulation complete!")
    print(f"📈 Total emissions for best route: {total_emissions_grams:.2f} grams CO2e")
    print(f"🔋 Final energy level for best route: {current_energy:.2f} kWh")

simulate_drive()