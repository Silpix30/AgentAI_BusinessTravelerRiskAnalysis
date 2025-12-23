# Language & Culture Agent: Focuses on Business Nuance, Etiquette, and Cultural Intelligence
import sys
import os
import importlib.util
 
def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
 
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
search_web = import_from_path('search_web', os.path.join(root, 'app', 'utils', 'web_search.py')).search_web
 
class LanguageGuideAgent:
    def _is_same_language_context(self, nationality, country):
        """
        Helper to detect English-to-English travel (e.g., Indian to USA/UK).
        Prevents the agent from translating 'Hello' to 'Hello'.
        """
        if not nationality or not country:
            return False
            
        nat = nationality.lower().strip()
        cnt = country.lower().strip()
        
        # List of primary English-speaking business contexts
        # You can expand this list (e.g. Singapore, Ireland)
        english_origins = ["indian", "american", "british", "australian", "canadian"]
        english_destinations = ["usa", "united states", "us", "uk", "united kingdom", "australia", "canada", "new zealand"]
        
        if nat in english_origins and cnt in english_destinations:
            return True
        return False
 
    def process(self, country=None, city=None, planned_stay=None, nationality=None, **kwargs):
        """
        Provides Cultural Intelligence.
        Mode A: Same Language -> Focus on Slang, Etiquette, Tipping.
        Mode B: Foreign Language -> Focus on Business Phrases & Translation.
        """
        # 1. Setup Context
        location = f"{city}, {country}" if city else country
        nationality = nationality if nationality else "Foreign"
        
        is_same_language = self._is_same_language_context(nationality, country)
        
        # Check domestic (fallback logic from your original code)
        is_domestic = False
        if nationality and country:
            nat_lower = nationality.lower().strip()
            cnt_lower = country.lower().strip()
            if nat_lower in cnt_lower or cnt_lower in nat_lower or (nat_lower == "indian" and cnt_lower == "india"):
                is_domestic = True
 
        # 2. Build Specific Queries based on Context
        if is_same_language and not is_domestic:
            # --- MODE A: CULTURAL COACHING (English to English) ---
            # Don't translate. Teach how to 'fit in'.
            query = (
                f"Business etiquette differences between {nationality} and {country} corporate culture. "
                f"Local slang words and 'small talk' topics used in {city} business meetings. "
                f"Tipping culture in {country} for business dinners and taxis. "
                f"What are cultural faux pas or taboos a {nationality} professional should avoid in {country}?"
            )
            
        elif is_domestic:
            # --- MODE B: REGIONAL NUANCE ---
            query = (
                f"Regional business culture in {city} compared to rest of {country}. "
                f"Local language greetings or specific cultural norms for doing business in {city}. "
                f"Dress code and punctuality expectations in {city} corporate offices."
            )
            
        else:
            # --- MODE C: TRANSLATION & BASICS (True International) ---
            query = (
                f"Essential business phrases in local language of {country} for a {nationality} speaker. "
                f"Pronunciation guide for: Greetings, 'Nice to meet you', 'Thank you'. "
                f"Key non-verbal communication tips (eye contact, handshakes) in {country}."
            )
 
        # 3. Execution
        # We always use 'detailed' for culture because nuances require explanation,
        # unless it's a super short trip where we just need 'Critical Do's and Don'ts'.
        mode = "critical" if planned_stay and planned_stay < 5 else "detailed"
        
        print(f"DEBUG [LanguageAgent]: Same Lang? {is_same_language} | Query -> {query}")
        
        return search_web(query, mode)