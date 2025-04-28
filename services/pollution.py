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
    print(f"Request URL: {url}")  # Debugging the URL
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")  # Debugging the status code
        print(f"Response Text: {response.text}")  # Debugging the response text
        
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        
        data = response.json()
        pollution = data["list"][0]
        
        # AQI labeling based on OpenWeatherMap's 1-5 scale
        aqi_labels = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        aqi_label = aqi_labels.get(pollution["main"]["aqi"], "Unknown")
        
        return {
            "aqi": pollution["main"]["aqi"],  # 1 to 5
            "aqi_label": aqi_label,  # AQI label (Good, Moderate, etc.)
            "components": pollution["components"]  # dict of CO, NO2, O3, PM2.5, etc.
        }
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching pollution data: {e}")


def calculate_aqi(concentration, breakpoints):
    """
    Calculate AQI based on a given concentration and breakpoints for the pollutant.
    
    Args:
        concentration (float): Concentration of the pollutant (e.g., PM2.5, CO).
        breakpoints (list of tuples): AQI breakpoints for the pollutant. Each tuple should be (C_low, C_high, I_low, I_high).
        
    Returns:
        float: The calculated AQI for the given concentration.
    """
    for C_low, C_high, I_low, I_high in breakpoints:
        if C_low <= concentration <= C_high:
            return ((concentration - C_low) / (C_high - C_low)) * (I_high - I_low) + I_low
    return None  # If concentration is outside of known breakpoints

# Define AQI breakpoints for common pollutants (example values)
aqi_breakpoints = {
    "co": [(0, 4.4, 0, 50), (4.5, 9.4, 51, 100), (9.5, 12.4, 101, 150)],  # Example for CO
    "no": [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150)],  # Example for NO
    "no2": [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150)],  # Example for NO2
    "o3": [(0, 54, 0, 50), (55, 184, 51, 100)],  # Example for O3
    "so2": [(0, 35, 0, 50), (36, 75, 51, 100)],  # Example for SO2
    "pm2_5": [(0, 12, 0, 50), (13, 35.4, 51, 100)],  # Example for PM2.5
    "pm10": [(0, 54, 0, 50), (55, 154, 51, 100)],  # Example for PM10
}
def aqi_pollution_data(lat: float, lon: float) -> dict:
    pollution_data = get_pollution_data(lat, lon)

    aqi_values = {
        pollutant: calculate_aqi(conc, aqi_breakpoints[pollutant])
        for pollutant, conc in pollution_data['components'].items()
        if pollutant in aqi_breakpoints
    }
    overall_aqi = max(v for v in aqi_values.values() if v is not None)

    return pollution_data["aqi"], overall_aqi




