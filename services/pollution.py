import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_pollution_data(lat: float, lon: float) -> dict:
    """
    Fetch real-time air pollution data for a given location.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        dict: Pollution metrics (AQI and pollutants)
    """
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Pollution API error: {response.text}")
    
    data = response.json()
    pollution = data["list"][0]
    
    return {
        "aqi": pollution["main"]["aqi"],  # 1 to 5
        "components": pollution["components"]  # dict of CO, NO2, O3, PM2.5, etc.
    }