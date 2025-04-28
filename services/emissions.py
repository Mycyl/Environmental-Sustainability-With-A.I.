import os
import requests
from dotenv import load_dotenv

load_dotenv()
CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")

def estimate_diesel_emissions(distance: float, region: str = "US") -> dict:
    """
    Estimate CO2 emissions from diesel fuel consumption using the Climatiq API.

    Args:
        fuel_liters (float): Amount of diesel fuel in liters.
        region (str): UN location code for the fuel source (optional, defaults to global if not provided).

    Returns:
        dict: Response from Climatiq API with CO2e estimate and metadata.
    """
    url = "https://api.climatiq.io/data/v1/estimate"
    
    # Use a general diesel activity ID
    activity_id = "fuel-type_diesel"
    data_version = "^3"

    # Construct the body of the request
    json_body = {
        "emission_factor": {
		"activity_id": "passenger_vehicle-vehicle_type_car-fuel_source_diesel-engine_size_na-vehicle_age_2007_to_2022-vehicle_weight_na",
		"source": "EPA",
		"region": "US",
		"year": 2025,
		"source_lca_activity": "fuel_combustion",
		"data_version": "^0",
		"allowed_data_quality_flags": [
			"partial_factor"
		]
	},
        "parameters":
            {
            "distance": distance,
            "distance_unit": "km"
            }
        }
    
    # Add region only if provided
    if region:
        json_body["emission_factor"]["region"] = region

    headers = {
        "Authorization": f"Bearer {CLIMATIQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=json_body, headers=headers)

    if response.status_code != 200:
        print(f"Error response: {response.text}")
        raise Exception(f"Climatiq API error: {response.text}")

    if response.status_code != 200:
        raise Exception(f"Climatiq API error: {response.text}")

    return response.json()

# Example Usage:
distance = 10  # in liters
print(estimate_diesel_emissions(distance))  # No region provided, using global default
