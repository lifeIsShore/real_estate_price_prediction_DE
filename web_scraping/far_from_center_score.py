import requests
from geopy.distance import geodesic

def get_coordinates_from_zip(zip_code, country="Germany"):
    """
    Retrieves coordinates based on a postal code.

    Parameters:
        zip_code (str): Postal code.
        country (str): Country name (default: Germany).

    Returns:
        tuple: (latitude, longitude) or None (if not found).
    """
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "postalcode": zip_code,
        "country": country,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "DistanceCalculator/1.0 (meforpresident38@gmail.com)"
    }
    
    response = requests.get(nominatim_url, params=params, headers=headers)
    if response.ok:
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            print(f"No coordinates found for postal code '{zip_code}'.")
            return None
    else:
        print(f"Geocoding error: {response.status_code}")
        return None

def get_zip_from_address(address):
    """
    Retrieves the postal code from an address.

    Parameters:
        address (str): Address text.

    Returns:
        str: Postal code or None.
    """
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "DistanceCalculator/1.0 (meforpresident38@gmail.com)"
    }
    
    response = requests.get(nominatim_url, params=params, headers=headers)
    if response.ok:
        data = response.json()
        if data:
            return data[0].get("display_name", "").split(",")[-2].strip()
        else:
            print(f"No postal code found for address '{address}'.")
            return None
    else:
        print(f"Geocoding error: {response.status_code}")
        return None

def calculate_distance_address_to_city_center(address, country="Germany"):
    """
    Calculates the distance between the address coordinates and the city center in the same postal area.

    Parameters:
        address (str): Address text.
        country (str): Country name (default: Germany).

    Returns:
        float: Distance (km) or None.
    """
    # Get the postal code of the address
    zip_code = get_zip_from_address(address)
    if not zip_code:
        print(f"Postal code could not be retrieved for address: {address}")
        return None

    # Get city center coordinates (from the same postal code)
    city_center_coords = get_coordinates_from_zip(zip_code, country)
    if not city_center_coords:
        print(f"City center coordinates could not be retrieved for postal code: {zip_code}")
        return None

    # Get address coordinates
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "DistanceCalculator/1.0 (meforpresident38@gmail.com)"
    }
    
    response = requests.get(nominatim_url, params=params, headers=headers)
    if response.ok:
        data = response.json()
        if data:
            address_coords = float(data[0]["lat"]), float(data[0]["lon"])
        else:
            print(f"No coordinates found for address: {address}")
            return None
    else:
        print(f"Geocoding error: {response.status_code}")
        return None

    # Calculate distance
    distance_km = geodesic(address_coords, city_center_coords).kilometers
    return round(distance_km, 2)


# Example usage
address = "Prenzlauer Berg,  Berlin (10437)"  # Specify the city center address
distance = calculate_distance_address_to_city_center(address)

if distance is not None:
    print(f"Distance between '{address}' and city center: {distance} km.")
else:
    print("Distance could not be calculated.")
