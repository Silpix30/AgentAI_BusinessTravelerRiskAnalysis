# Health Agent: Handles health and vaccination requirements


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

class HealthAgent:
    def process(self, country=None, city=None, gender=None, health_conditions=None, nationality=None, planned_stay=None, **kwargs):
        # Determine detail level based on planned stay
        detail_level = "critical" if planned_stay and planned_stay < 10 else "detailed"
        
        # Check if this is domestic travel
        is_domestic = False
        if nationality and country:
            nationality_lower = nationality.lower().strip()
            country_lower = country.lower().strip()
            if (nationality_lower in country_lower or country_lower in nationality_lower or
                (nationality_lower == "indian" and country_lower == "india") or
                (nationality_lower == "american" and country_lower in ["usa", "united states"])):
                is_domestic = True
        
        # Build a query that includes all context for personalized recommendations
        base = f"A {nationality if nationality else 'foreign'} traveler is visiting {city+', ' if city else ''}{country} for {planned_stay if planned_stay else 'several'} days."
        
        if is_domestic:
            base += f" This is DOMESTIC travel within their home country."
        else:
            base += f" This is INTERNATIONAL travel."
        
        details = []
        if gender and gender.lower() in ["female", "male", "other"]:
            details.append(f"Gender: {gender}")
        if health_conditions and health_conditions.lower() not in ["none", ""]:
            details.append(f"Health condition(s): {health_conditions}")
        
        if details:
            base += " Traveler profile: " + ", ".join(details) + "."
            if detail_level == "critical":
                base += (
                    f" You are a medical travel advisor. Provide ONLY the most CRITICAL and essential health recommendations for a {gender} traveler with {health_conditions}. "
                    f"Focus ONLY on: 1) Essential medication needs, 2) Critical dietary warnings, 3) Nearest emergency care, 4) Required vaccinations/documents. "
                    f"Keep it brief and action-oriented."
                )
            else:
                base += (
                    f" You are a medical travel advisor. ONLY provide practical, actionable, and specific recommendations for a traveler with {health_conditions} who identifies as {gender} visiting {country}. "
                    f"Do NOT include any generic travel or health advice. "
                    f"Focus on: 1) Medication and prescription needs, 2) Diet and food safety, 3) Emergency care and hospital access, 4) Vaccination or health documentation, 5) Gender-specific risks or needs, 6) Any travel restrictions or special alerts for this profile. "
                    f"If there is no special advice for this profile, say 'No special advice for this profile.'"
                )
        else:
            if detail_level == "critical":
                base += f" Provide ONLY CRITICAL health information: required vaccinations, health alerts, and emergency contacts. Keep it brief."
            else:
                base += " Please provide general health, vaccination, and travel recommendations, risks, and precautions for this traveler."
        
        base += " Include any region-specific health precautions."
        query = base
        return search_web(query, detail_level)