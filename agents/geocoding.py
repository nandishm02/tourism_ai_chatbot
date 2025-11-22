import requests
from typing import Optional, Tuple

def get_coordinates(place_name: str) -> Optional[Tuple[float, float, Optional[int], Optional[str]]]:
    """
    Fetches coordinates and OSM details for a given place name using Photon API (Komoot).
    Returns: (latitude, longitude, osm_id, osm_type)
    """
    url = "https://photon.komoot.io/api/"
    params = {
        "q": place_name,
        "limit": 1,
        "osm_tag": ["place:city", "boundary:administrative"]
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "features" in data and data["features"]:
            feature = data["features"][0]
            props = feature["properties"]
            coords = feature["geometry"]["coordinates"]
            
            lat = coords[1]
            lon = coords[0]
            osm_id = props.get("osm_id")
            osm_type_char = props.get("osm_type")
            
            # Map Photon type char to full name
            type_map = {'R': 'relation', 'W': 'way', 'N': 'node'}
            osm_type = type_map.get(osm_type_char, osm_type_char)
            
            return lat, lon, osm_id, osm_type
        else:
            print(f"Geocoding: No data found for {place_name}.")
            return None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None
