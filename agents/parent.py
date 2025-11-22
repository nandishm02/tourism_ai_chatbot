from agents.geocoding import get_coordinates
from agents.weather import get_weather
from agents.places import get_places
from agents.nlp_parser import NLPParser

class ParentAgent:
    def __init__(self):
        """Initialize the parent agent with NLP parser."""
        self.parser = NLPParser()

    def process_message(self, user_input: str) -> str:
        """
        Orchestrates the request using regex-based NLP for intent parsing.
        """
        # 1. Parse Intent and Location with NLP
        location, intent = self.parser.parse(user_input)
        
        if not location:
            return "I couldn't identify the location you want to visit. Please specify a city."

        # 2. Get Coordinates
        coords = get_coordinates(location)
        if not coords:
            return f"I couldn't find the location '{location}'. Please check the spelling or try a major city."
        
        lat, lon, osm_id, osm_type = coords
        
        # 3. Call Agents based on Intent
        response_parts = []
        
        if intent == "Weather" or intent == "Both":
            weather_info = get_weather(lat, lon)
            if weather_info:
                response_parts.append(f"In {location} it's {weather_info}.")
        
        if intent == "Places" or intent == "Both":
            places = get_places(lat, lon, osm_id, osm_type)
            if places:
                places_list = "\n".join(places)
                response_parts.append(f"In {location} these are the places you can go:\n{places_list}")
            else:
                response_parts.append(f"I couldn't find any specific tourist attractions in {location}.")

        return "\n\n".join(response_parts)
