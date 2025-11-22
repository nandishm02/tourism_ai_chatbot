import re
from typing import Tuple, Optional

class NLPParser:
    def __init__(self):
        """Initialize the lightweight regex-based parser."""
        # Common location indicators
        self.location_prepositions = ["to", "in", "at", "from", "near", "around", "about", "for"]
        self.location_verbs = ["visit", "visiting", "go", "going", "travel", "traveling", 
                              "come", "coming", "move", "moving", "fly", "flying", 
                              "drive", "driving", "explore", "exploring", "tour", "touring"]
        
        # Words to skip when looking for locations
        self.skip_words = {
            "i", "i'm", "i'll", "what's", "tell", "show", "plan", "my", "the", "a", "an",
            "going", "visit", "trip", "weather", "what", "where", "when", "want", "need",
            "like", "tell", "about", "there", "here", "this", "that", "these", "those",
            "me", "you", "we", "they", "it", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would", "should", "could",
            "can", "may", "might", "must", "shall", "and", "or", "with"
        }
        
        # Intent keywords
        self.weather_keywords = [
            "weather", "temperature", "rain", "forecast", "climate",
            "hot", "cold", "sunny", "cloudy", "humid", "temp", "raining",
            "snowing", "windy", "storm", "precipitation"
        ]
        
        self.places_keywords = [
            "visit", "trip", "plan", "attractions", "places", "see",
            "go", "tour", "travel", "explore", "sightseeing", "destination",
            "going", "vacation", "holiday", "things", "spots", "sites",
            "landmarks", "monuments", "museums", "parks"
        ]
    
    def parse(self, user_input: str) -> Tuple[Optional[str], str]:
        """
        Parse user input to extract location and intent.
        
        Returns:
            (location, intent) where intent is "Weather", "Places", or "Both"
        """
        # Extract location
        location = self._extract_location(user_input)
        
        # Determine intent
        intent = self._determine_intent(user_input)
        
        return location, intent
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text using regex patterns and heuristics."""
        
        # Strategy 1: Look for patterns like "in <Location>", "to <Location>", etc.
        # This handles: "weather in Mumbai", "going to Kerala", "visit Delhi"
        for prep in self.location_prepositions:
            # Pattern: preposition followed by capitalized word(s)
            pattern = rf'\b{prep}\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)'
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                if self._is_valid_location(location):
                    return location
            
            # Pattern: preposition followed by lowercase word (for all-lowercase input)
            # This handles: "going to bangalore", "weather in mumbai"
            pattern_lower = rf'\b{prep}\s+([a-z][a-z]+(?:\s+[a-z]+)*)'
            match = re.search(pattern_lower, text.lower())
            if match:
                raw_location = match.group(1).strip()
                # Check if the first word is a verb or skip word (e.g. "to visit bangalore")
                first_word = raw_location.split()[0]
                if first_word in self.location_verbs or first_word in self.skip_words:
                    # Strip the first word if there are more words
                    parts = raw_location.split()
                    if len(parts) > 1:
                        raw_location = " ".join(parts[1:])
                    else:
                        continue
                
                location = raw_location.title()
                if self._is_valid_location(location):
                    return location
        
        # Strategy 2: Look for patterns like "visit <Location>", "explore <Location>"
        for verb in self.location_verbs:
            # Pattern: verb followed by capitalized word(s)
            pattern = rf'\b{verb}\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)'
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                if self._is_valid_location(location):
                    return location
            
            # Pattern: verb followed by lowercase word
            pattern_lower = rf'\b{verb}\s+([a-z][a-z]+(?:\s+[a-z]+)*)'
            match = re.search(pattern_lower, text.lower())
            if match:
                raw_location = match.group(1).strip()
                # Check if the first word is a skip word
                first_word = raw_location.split()[0]
                if first_word in self.skip_words:
                    parts = raw_location.split()
                    if len(parts) > 1:
                        raw_location = " ".join(parts[1:])
                    else:
                        continue

                location = raw_location.title()
                if self._is_valid_location(location):
                    return location
        
        # Strategy 3: Look for capitalized words (proper nouns)
        # This handles: "What's the weather in Mumbai?"
        words = text.split()
        for i, word in enumerate(words):
            # Clean punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word and len(clean_word) > 2:
                # Check if it's capitalized and not a skip word
                if clean_word[0].isupper() and clean_word.lower() not in self.skip_words:
                    # Check if it's not at the start of a sentence
                    if i > 0 or not self._is_sentence_start_word(clean_word):
                        if self._is_valid_location(clean_word):
                            return clean_word
        
        # Strategy 4: Fallback - look for any word that could be a location
        # This handles fully lowercase queries: "bangalore weather"
        words = text.lower().split()
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word)
            if len(clean_word) > 2 and clean_word not in self.skip_words:
                # Skip obvious non-location words
                if not any(kw in clean_word for kw in self.weather_keywords + self.places_keywords):
                    return clean_word.title()
        
        return None
    
    def _is_valid_location(self, word: str) -> bool:
        """Check if a word could be a valid location name."""
        if not word or len(word) < 2:
            return False
        
        # Remove common punctuation
        clean = word.strip('.,!?;:')
        
        # Skip if it's a skip word
        if clean.lower() in self.skip_words:
            return False
        
        # Skip if it's a weather or places keyword
        if clean.lower() in self.weather_keywords or clean.lower() in self.places_keywords:
            return False
        
        # Skip common sentence starters
        if clean in ["What", "Tell", "Show", "Plan", "How", "Why", "When", "Where"]:
            return False
        
        return True
    
    def _is_sentence_start_word(self, word: str) -> bool:
        """Check if a word is typically used at the start of sentences."""
        sentence_starters = {
            "What", "Tell", "Show", "Plan", "How", "Why", "When", "Where",
            "I", "We", "You", "They", "Can", "Could", "Would", "Should",
            "Is", "Are", "Do", "Does", "Will", "Please"
        }
        return word in sentence_starters
    
    def _determine_intent(self, text: str) -> str:
        """Determine user intent based on keywords."""
        text_lower = text.lower()
        
        # Check for weather keywords
        has_weather = any(keyword in text_lower for keyword in self.weather_keywords)
        
        # Check for places keywords
        has_places = any(keyword in text_lower for keyword in self.places_keywords)
        
        if has_weather and has_places:
            return "Both"
        elif has_weather:
            return "Weather"
        elif has_places:
            return "Places"
        else:
            # Default to Places if no specific keywords found
            return "Places"
