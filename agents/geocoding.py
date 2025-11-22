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
        "limit": 5, 
        "osm_tag": ["place:city", "boundary:administrative"]
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "features" in data and data["features"]:
            def score_feature(feature):
                props = feature["properties"]
                score = 0
                country_code = props.get("countrycode", "").upper()
                if country_code == "IN":  # India
                    score += 10000
                elif country_code in ["US", "GB", "CN", "BR", "DE", "FR", "JP"]:  # Major countries
                    score += 5000
                elif country_code in ["AU", "NZ"]:  # Deprioritize Australia/NZ for Indian city names
                    score -= 5000
                type_map = {'R': 300, 'W': 200, 'N': 100}
                score += type_map.get(props.get("osm_type"), 0)
                admin_level = props.get("admin_level")
                if admin_level:
                    try:
                        score += (20 - int(admin_level)) * 10  
                    except:
                        pass

                population = props.get("population")
                if population:
                    try:
                        score += min(int(population) / 10000, 100)  # Cap at 100
                    except:
                        pass
                
                return score
            
            # Sort features by score
            sorted_features = sorted(data["features"], key=score_feature, reverse=True)
            feature = sorted_features[0]
            
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
