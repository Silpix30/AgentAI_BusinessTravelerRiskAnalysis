# Accommodation Agent: Handles hotel/rental recommendations with Safety & Budget Logic
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
 
class AccommodationAgent:
    def process(self, country=None, city=None, planned_stay=None, nationality=None, gender=None, budget_range=None, purpose=None, **kwargs):
        """
        Recommends accommodation while enforcing safety standards for business travelers.
        Includes a 'Sanity Check' for low budgets.
        """
        # 1. Parse Inputs & Defaults
        gender = gender.lower() if gender else "male"
        purpose = purpose if purpose else "Business"
        location = f"{city}, {country}" if city else country
        
        # 2. Budget Safety Logic (The "Anti-Motel 6" Check)
        # We check if the user is trying to book extremely cheap hotels in expensive/risky regions
        is_low_budget = False
        if budget_range:
            # Simple check: if max budget mentioned is 50, 40, or 30 dollars
            if any(price in str(budget_range) for price in ["0-50", " 50", "$50", "40", "30"]):
                is_low_budget = True
 
        # Check if country is generally expensive/requires higher safety standards
        is_developed_nation = False
        if country and country.lower() in ["usa", "us", "united states", "uk", "london", "canada", "france", "germany"]:
            is_developed_nation = True
 
        # 3. Define Safety Rules based on Profile
        safety_instruction = ""
        risk_warning_prefix = ""
 
        if gender == "female":
            safety_instruction = (
                "CRITICAL SAFETY CRITERIA: "
                "1. Must have 24-hour front desk and security. "
                "2. AVOID properties with 'Exterior Corridors' (rooms opening directly to parking lot). "
                "3. Prefer hotels with 'Women-only floors' or key-card access elevators. "
                "4. Location must be in a safe, busy district, not highway exits."
            )
            # TRIGGER THE WARNING MODE if budget is low + female + developed nation
            if is_low_budget and is_developed_nation:
                query = (
                    f"Safety risks of staying in hotels under $50 in {location} for a solo female traveler. "
                    f"Is it safe to stay in cheap motels in {city}? "
                    f"Are there any safe hostels with female-only dorms or Airbnb Superhosts in this price range? "
                    f"Explain why business travelers should increase their budget."
                )
                risk_warning_prefix = (
                    "⚠️ **CRITICAL BUDGET WARNING:**\n"
                    f"Your budget ({budget_range}) is **too low** for a safe business-standard hotel in {country}. "
                    "Most options in this range are highway motels or unverified rentals which may pose safety risks (exterior doors, lack of security). "
                    "**Recommendation:** Please increase budget to $100+ for safety, or consider the specific hostels/Airbnbs listed below.\n\n"
                )
        
        else: # Male / General
            safety_instruction = "Ensure property is in a safe area with good transport connectivity."
            if is_low_budget and is_developed_nation:
                risk_warning_prefix = "⚠️ **Note:** Your budget is very low for this city. Options may be limited to hostels or motels far from the center.\n\n"
 
        # 4. Construct the Main Search Query (If no warning override triggered)
        if not risk_warning_prefix or "Safety risks" not in locals().get('query', ''):
            # Normal Recommendation Mode
            query = (
                f"Recommend top rated safe business accommodation in {location} for a {nationality} {gender} traveler. "
                f"Purpose: {purpose}. "
                f"Budget: {budget_range}. "
                f"{safety_instruction} "
                f"Prioritize locations near {city} business districts (e.g. Downtown). "
                f"List 3 specific options with pros/cons."
            )
 
        # 5. Execute
        # We always use 'detailed' to get safety reviews, unless it's a very short stay check
        search_result = search_web(query, "detailed")
        
        return f"{search_result}"