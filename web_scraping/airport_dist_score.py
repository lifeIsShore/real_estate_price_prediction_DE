import requests
from geopy.distance import geodesic
import math
from tenacity import retry, stop_after_attempt, wait_fixed

# Retry mechanism for API calls
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_coordinates(address):
    """
    Retrieves the latitude and longitude of a given address using Nominatim.
    
    Parameters:
        address (str): The address to geocode.
        
    Returns:
        tuple: (latitude, longitude) if successful, otherwise None.
    """
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "MyGeocodingApp/1.0 (meforpresident38@gmail.com)"}
    response = requests.get(nominatim_url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None

def get_nearest_airport_coordinates(lat, lon):
    """
    Finds the nearest airport to the given coordinates using Overpass API.
    
    Parameters:
        lat (float): Latitude.
        lon (float): Longitude.
        
    Returns:
        tuple: The coordinates of the nearest airport (latitude, longitude), or None if no airport is found.
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node(around:50000,{lat},{lon})[aeroway=aerodrome];
    );
    out;
    """
    response = requests.get(overpass_url, params={"data": query})
    response.raise_for_status()
    data = response.json()

    if not data.get("elements"):
        print("No nearby airport found.")
        return None

    # Return the first airport found
    nearest_airport = data["elements"][0]
    return nearest_airport["lat"], nearest_airport["lon"]

def calculate_airport_distance_log(address):
    """
    Calculates the distance from the given address to the nearest airport
    and applies a logarithmic transformation to scale the result.
    
    Parameters:
        address (str): The address to evaluate.
        
    Returns:
        float: The logarithmically scaled distance to the nearest airport.
    """
    try:
        # Get the coordinates of the address
        address_coords = get_coordinates(address)
        if not address_coords:
            print(f"Could not retrieve coordinates for address: {address}")
            return None

        # Get the coordinates of the nearest airport
        airport_coords = get_nearest_airport_coordinates(*address_coords)
        if not airport_coords:
            print(f"No nearby airport found for address: {address}")
            return None

        # Calculate the distance between the address and the airport
        distance_km = geodesic(address_coords, airport_coords).kilometers

        # Apply logarithmic transformation (add 1 to avoid log(0))
        log_distance = math.log1p(distance_km)  # log1p(x) = log(1 + x)
        return round(log_distance, 4)  # Round for readability

    except Exception as e:
        print(f"Error: {e}")
        return None

'''
address = "Kirchheim, Euskirchen / Kirchheim (53881)"  # Example address
log_distance = calculate_airport_distance_log(address)

if log_distance is not None:
    print(f"The log-scaled distance to the nearest airport for '{address}': {log_distance}")
else:
    print("Could not calculate the airport distance.")
'''              