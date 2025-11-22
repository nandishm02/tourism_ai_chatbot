import requests
from typing import Optional

def get_weather(lat: float, lon: float) -> Optional[str]:
    """
    Fetches current weather and forecast for given coordinates using Open-Meteo API.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "precipitation_probability"],
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        temp = current.get("temperature_2m")
        precip_prob = current.get("precipitation_probability", 0)
        
        if temp is not None:
            return f"currently {temp}°C with a chance of {precip_prob}% to rain"
        return "Weather data unavailable."
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None
