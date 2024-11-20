from geopy.distance import geodesic
import requests

def score_address(address):
    """
    Given an address, this function calculates a score based on nearby amenities
    with more detailed scoring logic.

    Parameters:
        address (str): The address to geocode and find nearby locations for scoring.

    Returns:
        int: The total score for the address based on nearby amenities.
    """
    # Geocoding the address
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "MyGeocodingApp/1.0 (meforpresident38@gmail.com)"}
    response = requests.get(nominatim_url, params=params, headers=headers)

    try:
        response.raise_for_status()
        location_data = response.json()
    except (requests.exceptions.HTTPError, ValueError) as err:
        print(f"Error fetching location: {err}")
        return 0

    if not location_data:
        print("Address not found or invalid.")
        return 0

    # Extracting coordinates
    location_data = location_data[0]
    lat, lon = float(location_data["lat"]), float(location_data["lon"])

    # Overpass API query
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node(around:1000,{lat},{lon})[shop=supermarket];
      node(around:1000,{lat},{lon})[shop=convenience];
      node(around:1000,{lat},{lon})[shop=variety_store];
      node(around:1000,{lat},{lon})[public_transport=stop_position][bus=yes];
      node(around:1000,{lat},{lon})[railway=station];
      node(around:1000,{lat},{lon})[leisure=park];
      node(around:1000,{lat},{lon})[amenity=fast_food];
    );
    out;
    """
    overpass_response = requests.get(overpass_url, params={"data": query})

    if not overpass_response.ok:
        print("Nearby locations API call failed.")
        return 0

    nearby_locations = overpass_response.json()["elements"]
    total_score = 0
    last_location = {}

    # Scoring logic
    for place in nearby_locations:
        tags = place.get("tags", {})
        place_type = (
            "Supermarket" if tags.get("shop") == "supermarket" else
            "Convenience Store" if tags.get("shop") == "convenience" else
            "Variety Store" if tags.get("shop") == "variety_store" else
            "Bus Stop" if tags.get("public_transport") == "stop_position" and tags.get("bus") == "yes" else
            "Train Station" if tags.get("railway") == "station" else
            "Park" if tags.get("leisure") == "park" else
            "Fast Food" if tags.get("amenity") == "fast_food" else
            "Unknown"
        )

        place_coords = (place["lat"], place["lon"])
        distance = geodesic((lat, lon), place_coords).meters

        # Previous distance sadece otobüs ve tren için uygulanır
        prev_distance = (
            geodesic(last_location[place_type], place_coords).meters
            if place_type in last_location and place_type in ["Bus Stop", "Train Station"] else float("inf")
        )

        # Scoring logic
        if distance <= 1000 and (place_type not in ["Bus Stop", "Train Station"] or prev_distance > 90):
            if place_type in ["Supermarket", "Convenience Store", "Variety Store"]:
                if distance <= 100:
                    score = 20
                elif distance <= 300:
                    score = 15
                elif distance <= 600:
                    score = 10
                else:
                    score = 5
            elif place_type in ["Bus Stop", "Train Station"]:
                if distance <= 200:
                    score = 25  # Bonus for very close public transport
                elif distance <= 500:
                    score = 15
                else:
                    score = 10
            elif place_type in ["Park", "Fast Food"]:
                if distance <= 100:
                    score = 10
                elif distance <= 300:
                    score = 7
                else:
                    score = 5
            else:
                score = 3  # Default score for unknown or less critical amenities

            total_score += score
            last_location[place_type] = place_coords

    return total_score

# Example usage
address = "baden baden"
score = score_address(address)
print("Final Score:", score)
