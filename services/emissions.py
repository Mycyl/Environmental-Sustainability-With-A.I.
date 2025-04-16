import os
import requests
from dotenv import load_dotenv

load_dotenv()
CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")

def estimate_grid_emissions(energy_kwh: float, region: str) -> dict:
    """
    Estimate CO2 emissions from electricity generation using the Climatiq API.

    Args:
        energy_kwh (float): Amount of electricity in kilowatt-hours (kWh).
        region (str): UN location code for the electricity source (default is "AU").

    Returns:
        dict: Response from Climatiq API with CO2e estimate and metadata.
    """
    url = "https://api.climatiq.io/data/v1/estimate"
    activity_id = "electricity-supply_grid-source_residual_mix"
    data_version = "^3"

    json_body = {
        "emission_factor": {
            "activity_id": activity_id,
            "data_version": data_version,
            "region": region,
        },
        "parameters": {
            "energy": energy_kwh,
            "energy_unit": "kWh"
        }
    }

    headers = {
        "Authorization": f"Bearer {CLIMATIQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=json_body, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Climatiq API error: {response.text}")

    return response.json()

