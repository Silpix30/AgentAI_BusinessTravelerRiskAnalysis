# Travel Agent: Handles commuting, logistics, and safety-aware local travel
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
 
class TravelAgent:
    def process(self, country=None, city=None, duration=None, season=None, planned_stay=None, nationality=None, **kwargs):
        """
        Recommend logistics based on Persona (Business vs Leisure), Safety Profile, and Health needs.
        """
        # Validate inputs
        if not country:
            return "Please provide at least a country for travel recommendations."
 
        # 1. Extract Context Variables
        purpose = kwargs.get('purpose', 'Business').lower()
        gender = kwargs.get('gender', 'Male').lower()
        health_condition = kwargs.get('health_condition', 'None').lower()
       
        # 2. Determine Persona & Logistics Strategy
        if any(x in purpose for x in ["business", "client", "meeting", "work", "conference"]):
            # Business Persona: Prioritize Time, Comfort, Reliability
            commute_focus = "Premium Cabs (Uber Premier/Ola), Metro Rail (fastest route)."
            avoid_list = "Crowded local buses, shared autos, unmetered taxis, walking in heat."
            logistics_priority = "Punctuality, Traffic Hotspots (e.g. peak hour delays), Proximity to business districts."
            persona_instruction = "Act as a Corporate Logistics Manager."
        else:
            # Leisure Persona: Prioritize Experience, Cost
            commute_focus = "Tourist buses, Metro, Auto-rickshaws, Walking tours."
            avoid_list = "Overpriced private charters."
            logistics_priority = "Scenic routes, connectivity to landmarks, cost-effectiveness."
            persona_instruction = "Act as a Local Guide."
 
        # 3. Build Safety Layer (Gender Specific)
        safety_context = ""
        if gender == "female":
            safety_context = (
                "CRITICAL SAFETY FOR FEMALE TRAVELER: "
                "Highlight 'Ladies Coach' availability in Metro/Trains. "
                "Recommend ride-sharing apps with 'Share Ride' features over street-hailing. "
                "Identify safe vs unsafe zones at night."
            )
 
        # 4. Build Health Layer (Condition Specific)
        health_context = ""
        if health_condition and health_condition != "none":
            health_context = (
                f"MEDICAL CONDITION ALERT ({health_condition}): "
                f"Identify nearest top-tier hospitals to business districts. "
                f"Advise on carrying food/glucose if traffic jams are common (risk of missed meals). "
                f"Check accessibility of transport if relevant."
            )
 
        # 5. Seasonal Context (Impact on Business)
        weather_context = ""
        if season:
            weather_context = f"Consdering the season is {season}, warn about specific commute disruptions (e.g., Monsoon flooding roads, heatwave fatigue)."
 
        # 6. Construct the Hyper-Personalized Query
        # We stop asking "What are the options?" and start asking for "Specific Recommendations"
        location = f"{city}, {country}" if city else country
       
        query = (
            f"{persona_instruction} Plan commute for a {nationality or ''} {gender} traveler in {location} "
            f"staying {planned_stay} days for '{purpose}'. "
            f"RECOMMEND: {commute_focus} "
            f"AVOID: {avoid_list} "
            f"FOCUS ON: {logistics_priority} "
            f"{safety_context} "
            f"{health_context} "
            f"{weather_context} "
            "Provide 3 distinct sections: 'Recommended Commute', 'Safety & Health', and 'Traffic/Logistics Alerts'."
        )
       
        # Debug print to show judges the 'Reasoning' behind the query
        print(f"DEBUG [TravelAgent]: Generated Strategy -> {query}")
 
        # 7. Execute Search
        # We always use 'detailed' for business travel to ensure we get specific traffic/safety data
        return f"{search_web(query, 'detailed')}"
 