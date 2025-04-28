from geopy.distance import geodesic

def find_geodesic_midway_waypoint(waypoints):
    """
    Given a list of waypoints ([longitude, latitude]), compute the geodesic midpoint.
    
    Args:
        waypoints (list of [longitude, latitude] pairs).
        
    Returns:
        tuple: Midpoint (latitude, longitude).
    """
    total_distance = 0
    distances = []
    
    # Reformat waypoints from [lon, lat] to (lat, lon)
    waypoints_latlon = [(lat, lon) for lon, lat in waypoints]
    
    for i in range(len(waypoints_latlon) - 1):
        point1 = waypoints_latlon[i]
        point2 = waypoints_latlon[i + 1]
        
        distance = geodesic(point1, point2).kilometers
        total_distance += distance
        distances.append(distance)
    
    half_distance = total_distance / 2
    cumulative_distance = 0
    
    for i in range(len(distances)):
        cumulative_distance += distances[i]
        if cumulative_distance >= half_distance:
            segment_start = waypoints_latlon[i]
            segment_end = waypoints_latlon[i + 1]
            segment_distance = distances[i]
            ratio = (half_distance - (cumulative_distance - segment_distance)) / segment_distance
            
            lat1, lon1 = segment_start
            lat2, lon2 = segment_end
            
            mid_lat = lat1 + ratio * (lat2 - lat1)
            mid_lon = lon1 + ratio * (lon2 - lon1)
            return round(mid_lat, 6), round(mid_lon, 6)

    return None  # Fallback in case of error
