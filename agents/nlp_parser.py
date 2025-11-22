import spacy
from typing import Tuple, Optional

class NLPParser:
    def __init__(self):
        """Initialize spaCy NLP model."""
        try:
            # Try to load the model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Model not installed, provide helpful error
            print("ERROR: spaCy model 'en_core_web_sm' not found.")
            print("Please install it by running:")
            print("  python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def parse(self, user_input: str) -> Tuple[Optional[str], str]:
        """
        Parse user input to extract location and intent.
        
        Returns:
            (location, intent) where intent is "Weather", "Places", or "Both"
        """
        if not self.nlp:
            return None, "Places"
        
        # Process the text with spaCy
        doc = self.nlp(user_input.lower())
        
        # Extract location using Named Entity Recognition
        location = self._extract_location(doc, user_input)
        
        # Determine intent based on keywords
        intent = self._determine_intent(doc)
        
        return location, intent
    
    def _extract_location(self, doc, original_text: str) -> Optional[str]:
        """Extract location from spaCy doc using NER."""
        # Look for GPE (Geopolitical Entity) or LOC (Location) entities
        locations = []
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                locations.append(ent.text)
        
        if locations:
            # Return the first location found (usually the most relevant)
            # Capitalize properly for geocoding
            return locations[0].title()
        
        # Fallback 1: Look for words after common location prepositions
        # This handles "going to bangalore", "visiting mumbai", etc.
        location_prepositions = ["to", "in", "at", "from", "near"]
        common_verbs = ["travel", "visit", "go", "going", "come", "coming", "move", "moving", "fly", "flying", "drive", "driving"]
        words = original_text.lower().split()
        
        for i, word in enumerate(words):
            if word in location_prepositions and i + 1 < len(words):
                # Get the next word after the preposition
                potential_location = words[i + 1]
                # Remove punctuation
                potential_location = potential_location.strip('.,!?;:')
                # Skip if it's a common verb or too short
                if len(potential_location) > 2 and potential_location not in common_verbs:
                    return potential_location.title()
        
        # Fallback 2: Look for capitalized words in original text
        words = original_text.split()
        for word in words:
            # Check if word is capitalized and not a common word
            if word and word[0].isupper() and len(word) > 2:
                # Skip common words that might be capitalized
                skip_words = {"I", "I'm", "I'll", "What's", "Tell", "Show", "Plan", "My", "The", "A", "An"}
                if word not in skip_words and not word.endswith("'s"):
                    return word
        
        # Fallback 3: Look for any word that might be a location
        # Check if any word (when capitalized) could be a valid location
        # This is a last resort for fully lowercase queries like "bangalore"
        for word in words:
            word_clean = word.strip('.,!?;:').lower()
            # Skip very short words and common words
            if len(word_clean) > 3 and word_clean not in [
                "going", "visit", "plan", "trip", "weather", "what", "where",
                "when", "want", "need", "like", "show", "tell", "about"
            ]:
                # Return it capitalized - geocoding will validate if it's real
                return word_clean.title()
        
        return None
    
    def _determine_intent(self, doc) -> str:
        """Determine user intent based on keywords."""
        text = doc.text.lower()
        
        # Weather keywords
        weather_keywords = [
            "weather", "temperature", "rain", "forecast", "climate",
            "hot", "cold", "sunny", "cloudy", "humid", "temp"
        ]
        
        # Places keywords
        places_keywords = [
            "visit", "trip", "plan", "attractions", "places", "see",
            "go", "tour", "travel", "explore", "sightseeing", "destination",
            "going", "vacation", "holiday"
        ]
        
        has_weather = any(keyword in text for keyword in weather_keywords)
        has_places = any(keyword in text for keyword in places_keywords)
        
        if has_weather and has_places:
            return "Both"
        elif has_weather:
            return "Weather"
        elif has_places:
            return "Places"
        else:
            # Default to Places if no specific keywords found
            return "Places"
