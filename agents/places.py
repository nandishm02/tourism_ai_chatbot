import requests
from typing import List, Optional

def get_places(lat: float, lon: float, osm_id: Optional[int] = None, osm_type: Optional[str] = None, radius: int = 5000) -> List[str]:
    """
    Fetches tourist attractions near the given coordinates or within a specific area using Overpass API.
    If osm_id and osm_type are provided, it attempts to search within that area.
    Otherwise, it falls back to a radius search (default 5km).
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    area_id = None
    if osm_id and osm_type:
        if osm_type == 'relation':
            area_id = osm_id + 3600000000
        elif osm_type == 'way':
            area_id = osm_id + 2400000000
            
    if area_id:
        # Search within the area
        overpass_query = f"""
        [out:json];
        area({area_id})->.searchArea;
        (
          node["tourism"="attraction"](area.searchArea);
          way["tourism"="attraction"](area.searchArea);
          relation["tourism"="attraction"](area.searchArea);
          node["leisure"="park"](area.searchArea);
        );
        out center 10;
        """
    else:
        # Fallback to radius search
        overpass_query = f"""
        [out:json];
        (
          node["tourism"="attraction"](around:{radius},{lat},{lon});
          way["tourism"="attraction"](around:{radius},{lat},{lon});
          relation["tourism"="attraction"](around:{radius},{lat},{lon});
          node["leisure"="park"](around:{radius},{lat},{lon});
        );
        out center 10;
        """

    try:
        response = requests.post(overpass_url, data=overpass_query, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        places = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            # Prefer English name, fallback to local name
            name = tags.get("name:en", tags.get("name"))
            if name:
                # Clean up name: Title case and remove extra whitespace
                clean_name = name.strip().title()
                # Simple filter: Skip if name seems to be purely non-ASCII (optional, but user asked for English)
                # For now, relying on name:en is usually enough, but let's ensure we don't get duplicates
                if clean_name not in places:
                    places.append(clean_name)
        
        return places[:10] # Return top 10
    except Exception as e:
        print(f"Error fetching places: {e}")
        return []
