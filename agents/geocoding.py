import requests
from typing import Optional, Tuple

def get_coordinates(place_name: str) -> Optional[Tuple[float, float, Optional[int], Optional[str]]]:
    """
    Fetches coordinates and OSM details for a given place name using Nominatim API.
    Returns: (latitude, longitude, osm_id, osm_type)
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "TourismAgent/1.0 (me@example.com)" 
    }
    params = {
        "q": place_name,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data:
            result = data[0]
            lat = float(result["lat"])
            lon = float(result["lon"])
            osm_id = int(result.get("osm_id")) if result.get("osm_id") else None
            osm_type = result.get("osm_type")
            return lat, lon, osm_id, osm_type
        else:
            print(f"Geocoding: No data found for {place_name}.")
            return None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None
