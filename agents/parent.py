import os
import google.generativeai as genai
from agents.geocoding import get_coordinates
from agents.weather import get_weather
from agents.places import get_places
from dotenv import load_dotenv

load_dotenv()

class ParentAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in .env")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-lite')

    def process_message(self, user_input: str) -> str:
        """
        Orchestrates the request using LLM for intent parsing.
        """
        if not self.model:
            return "Error: LLM API key not configured. Please set GEMINI_API_KEY in .env."

        # 1. Parse Intent with LLM
        prompt = f"""
        Analyze the following user input: "{user_input}"
        
        Determine the User's Intent strictly:
        - "Weather": If user asks about temperature, rain, weather, etc.
        - "Places": If user asks to "plan my trip", "visit", "attractions", "places to go", etc.
        - "Both": ONLY if user explicitly asks for BOTH weather and places.
        
        Extract the Location (City).
        
        Output format:
        Location: [City Name]
        Intent: [Weather/Places/Both]
        
        If location is missing, return "Location: None".
        """
        
        try:
            response = self.model.generate_content(prompt)
            llm_output = response.text
            with open("parent.log", "a") as f:
                f.write(f"DEBUG: LLM Output:\n{llm_output}\n")
            
            # Simple parsing of LLM output
            location = None
            intent = "Both"
            
            for line in llm_output.split('\n'):
                if line.startswith("Location:"):
                    location = line.split(":", 1)[1].strip()
                elif line.startswith("Intent:"):
                    intent = line.split(":", 1)[1].strip()
            
            with open("parent.log", "a") as f:
                f.write(f"DEBUG: Parsed Location: '{location}', Intent: '{intent}'\n")

            if not location or location == "None":
                return "I couldn't identify the location you want to visit. Please specify a city."

            # 2. Get Coordinates
            coords = get_coordinates(location)
            if not coords:
                with open("parent.log", "a") as f:
                    f.write(f"DEBUG: get_coordinates failed for '{location}'\n")
                return f"I couldn't find the location '{location}'. Please check the spelling or try a major city."
            
            lat, lon, osm_id, osm_type = coords
            
            # 3. Call Agents based on Intent
            response_parts = []
            
            if "Weather" in intent or "Both" in intent:
                weather_info = get_weather(lat, lon)
                if weather_info:
                    response_parts.append(f"In {location} it's {weather_info}.")
            
            if "Places" in intent or "Both" in intent:
                places = get_places(lat, lon, osm_id, osm_type)
                if places:
                    places_list = "\n".join(places)
                    response_parts.append(f"In {location} these are the places you can go:\n{places_list}")
                else:
                    response_parts.append(f"I couldn't find any specific tourist attractions in {location}.")

            return "\n\n".join(response_parts)

        except Exception as e:
            return f"Error processing request: {str(e)}"
