import requests
from geopy.distance import geodesic

def score_address(address):
    """
    Given an address, this function calculates a score based on nearby amenities
    within 1000 meters, and returns the total score.

    Parameters:
        address (str): The address to geocode and find nearby locations for scoring.

    Returns:
        int: The total score for the address based on nearby amenities.
    """
    # 1. Convert the address to coordinates (Geocoding)
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "MyGeocodingApp/1.0 (meforpresident38@gmail.com)"
    }
    
    response = requests.get(nominatim_url, params=params, headers=headers)
    
    # Check response
    try:
        response.raise_for_status()
        location_data = response.json()
    except (requests.exceptions.HTTPError, ValueError) as err:
        print(f"Error fetching location: {err}")
        return 0

    # Check if location data is available
    if location_data:
        location_data = location_data[0]
        lat, lon = float(location_data["lat"]), float(location_data["lon"])
        #print(f"Address coordinates: Latitude: {lat}, Longitude: {lon}")

        # 2. Find nearby locations
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
          node(around:1000,{lat},{lon})[shop=supermarket];
          node(around:1000,{lat},{lon})[shop=convenience];
          node(around:1000,{lat},{lon})[shop=variety_store];
          node(around:1000,{lat},{lon})[shop=general];
          node(around:1000,{lat},{lon})[shop=greengrocer];
          node(around:1000,{lat},{lon})[shop=department_store];
          node(around:1000,{lat},{lon})[public_transport=stop_position][bus=yes];
          node(around:1000,{lat},{lon})[railway=station];
          node(around:1000,{lat},{lon})[leisure=park];
          node(around:1000,{lat},{lon})[amenity=fast_food];
          node(around:1000,{lat},{lon})[amenity=ice_cream];
          node(around:1000,{lat},{lon})[building=supermarket];
          node(around:1000,{lat},{lon})[leisure=garden];
          node(around:1000,{lat},{lon})[place=square];
          node(around:1000,{lat},{lon})[amenity=library];
          node(around:1000,{lat},{lon})[amenity=pharmacy];
          node(around:1000,{lat},{lon})[shop=cosmetics];
          node(around:1000,{lat},{lon})[amenity=school];
          node(around:1000,{lat},{lon})[amenity=kindergarten];
          node(around:1000,{lat},{lon})[amenity=university];
          node(around:1000,{lat},{lon})[education=centre];
          node(around:1000,{lat},{lon})[landuse=education];
        );
        out;
        """
        
        overpass_response = requests.get(overpass_url, params={"data": query})
        
        # Check Overpass API response
        if overpass_response.ok:
            nearby_locations = overpass_response.json()["elements"]
            last_location = {}
            total_score = 0

            # 3. Calculate distance and score based on distance thresholds
            for place in nearby_locations:
                tags = place.get("tags", {})
                place_type = (
                    "Supermarket" if tags.get("shop") == "supermarket" else
                    "Convenience Store" if tags.get("shop") == "convenience" else
                    "General Store" if tags.get("shop") == "general" else
                    "Variety Store" if tags.get("shop") == "variety_store" else
                    "Greengrocer" if tags.get("shop") == "greengrocer" else
                    "Department Store" if tags.get("shop") == "department_store" else
                    "Bus Stop" if tags.get("public_transport") == "stop_position" and tags.get("bus") == "yes" else
                    "Train Station" if tags.get("railway") == "station" else
                    "Fast Food" if tags.get("amenity") == "fast_food" else
                    "Ice Cream" if tags.get("amenity") == "ice_cream" else
                    "Market" if tags.get("building") == "supermarket" else
                    "Garden" if tags.get("leisure") == "garden" else
                    "Square" if tags.get("place") == "square" else
                    "Library" if tags.get("amenity") == "library" else
                    "Pharmacy" if tags.get("amenity") == "pharmacy" else
                    "Cosmetics Store" if tags.get("shop") == "cosmetics" else
                    "School" if tags.get("amenity") == "school" else
                    "Kindergarten" if tags.get("amenity") == "kindergarten" else
                    "University" if tags.get("amenity") == "university" else
                    "Education Area" if tags.get("landuse") == "education" else
                    "Education Centre" if tags.get("education") == "centre" else
                    "Unknown"
                )

                place_coords = (place["lat"], place["lon"])
                distance = geodesic((lat, lon), place_coords).meters

                # Check distance from last location of the same type
                prev_distance = (
                    geodesic(last_location[place_type], place_coords).meters
                    if place_type in last_location else float("inf")
                )
                
                # Apply scoring
                if distance <= 1000 and prev_distance > 90:
                    score = 10 if distance <= 200 else 8 if distance <= 500 else 5 if distance <= 750 else 3
                    total_score += score
                    last_location[place_type] = place_coords

            #print(f"Total Score: {total_score}")
            return total_score
        else:
            print("error1")
            print("Nearby locations API call failed.")
            return 0
    else:
        print("error2")
        print("Address not found or invalid.")
        return 0

# Example usage
address = "baden wurtemberg"
score = score_address(address)
print("Final Score:", score)
