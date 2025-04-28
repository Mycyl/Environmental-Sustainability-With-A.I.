import math
from routing import get_route
from pollution import aqi_pollution_data
from pollution import get_pollution_data
from emissions import estimate_diesel_emissions
from midwaypoint import find_geodesic_midway_waypoint

def score_heuristic(emissions, pollution, distance, high_aqi_area):
    score = 0
    if isinstance(emissions, dict):
        emissions = emissions.get('co2e', 0)
    emission_weight = 0.3
    pollution_weight = 0.3
    distance_weight = 0.2
    aqi_penalty_weight = 0.2
    if emissions < 100:
        score += emission_weight * (1 - math.exp(-emissions / 100)) * 2
    elif emissions < 130:
        score += emission_weight * (1 - math.exp(-emissions / 130)) * 2
    else:
        score += emission_weight * 0.0 * 2  
    if pollution < 50:
        score += pollution_weight * (1 - math.exp(-pollution / 50)) * 2
    elif pollution < 100:
        score += pollution_weight * (1 - math.exp(-pollution / 100)) * 2
    else:
        score += pollution_weight * 0.0 * 2
    if distance < 12:
        score += distance_weight * 2
    elif distance < 16:
        score += distance_weight * ((16 - distance) / 4) * 2
    else:
        score += distance_weight * 0
    if high_aqi_area == 1:
        score -= aqi_penalty_weight * 2
    score = max(0, min(score, 2))
    return score

def high_aqi_area(route):
    midlat, midlon = find_geodesic_midway_waypoint(route)
    aqi_data = get_pollution_data(midlat, midlon)
    return 1 if aqi > 3 else 0  # High AQI area if AQI is greater than 3

def append_text_to_file(file_path, text_to_append):
    try:
        with open(file_path, 'a') as file:
            file.write(text_to_append + '\n')
        print("Text appended to {file_path} successfully.")
    except Exception as e:
        print(e)


start_coords = (51.5007, -0.1246)
end_coords =  (51.5194, -0.1270)

print(f"Start Coords: {start_coords}")
print(f"End Coords: {end_coords}")

route_data = get_route(start_coords, end_coords, "driving-car", False)
print(route_data)
route = route_data["coordinates"]
distance = route_data["distance_meters"] / 1000  # Convert to kilometers
emissions = estimate_diesel_emissions(distance)['co2e'] * 1000  # Convert to grams
print(route)
lat, lon = find_geodesic_midway_waypoint(route)
print(f"Midway Point: {lat}, {lon}")
aqi, pollution = aqi_pollution_data(lat, lon)
high_aqi_area_variable = high_aqi_area(route)
score = score_heuristic(emissions, pollution, distance, high_aqi_area_variable)

csv_string = f"{emissions},{pollution},{distance},{high_aqi_area_variable},{score}"

append_text_to_file("delivery-optimizer/data/data_lin_reg.txt", csv_string)