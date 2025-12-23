# Compliance Agent: Handles HR, visa, labor law, and medical compliance
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
# Assuming search_web returns a string summary or search results
search_web = import_from_path('search_web', os.path.join(root, 'app', 'utils', 'web_search.py')).search_web

class ComplianceAgent:
    def _is_domestic(self, nationality, country):
        """
        Helper to determine if travel is domestic.
        """
        if not nationality or not country:
            return False
            
        nat = nationality.lower().strip()
        cnt = country.lower().strip()
        
        # Direct match or common demonyms
        # You can expand this map or use a library like pycountry for robustness in the future
        mappings = {
            "india": "indian", "usa": "american", "united states": "american",
            "uk": "british", "united kingdom": "british", "germany": "german",
            "france": "french", "china": "chinese", "japan": "japanese"
        }
        
        # Check if country matches nationality directly or via mapping
        if nat in cnt or cnt in nat: 
            return True
        if mappings.get(cnt) == nat:
            return True
            
        return False

    def process(self, country=None, city=None, planned_stay=None, nationality=None, gender=None, health_conditions=None, **kwargs):
        # 1. Extract Attributes from both named params and kwargs
        health_condition = health_conditions or kwargs.get('health_condition', None)  # Accept both spellings
        gender = gender or kwargs.get('gender', None)
        
        # Default planned_stay if missing
        days = int(planned_stay) if planned_stay else 7
        
        is_domestic = self._is_domestic(nationality, country)
        location_str = f"{city}, {country}" if city else country

        # 2. Build the Search Query using Prompt Engineering Logic
        queries = []

        # --- SCENARIO A: DOMESTIC TRAVEL ---
        if is_domestic:
            base_query = (
                f"Official domestic travel compliance rules for {nationality} citizen traveling to {location_str}. "
                f"IGNORE visa, immigration, and work permits. "
            )
            
            if days < 30:
                # Short Term Domestic: Focus on ID, GST, Security
                queries.append(base_query + 
                    "Focus on: Accepted Government ID proofs for airport/hotel (Aadhar/DL), "
                    "GST invoice requirements for hotel business stays, "
                    "and any state-specific entry permits (e.g. Inner Line Permit if applicable)."
                )
            else:
                # Long Term Domestic: Focus on State domicile rules? (Rare, but possible)
                queries.append(base_query + 
                    "Focus on: Long-term rental agreement norms for visitors, "
                    "local business registration requirements if setting up an office."
                )

        # --- SCENARIO B: INTERNATIONAL TRAVEL ---
        else:
            base_query = (
                f"Official business travel compliance for {nationality} citizen entering {country}. "
            )
            
            if days < 90:
                # Short Term Intl: Visa, Invitation Letters
                queries.append(base_query + 
                    f"Focus on: Business Visa requirements for {days} days stay, "
                    "Invitation letter requirements, Passport validity rules (6 months rule), "
                    "and Return ticket requirements."
                )
            else:
                # Long Term Intl: Work Permit, Tax Residency
                queries.append(base_query + 
                    f"CRITICAL: Check Tax Residency rules (183-day rule) for {country}, "
                    "Long-term Work Permit (not Business Visa) requirements, "
                    "Social Security contribution mandates for expats."
                )

        # --- SPECIAL COMPLIANCE: MEDICAL & GENDER ---
        # This fixes the missing "Diabetes" check
        if health_condition and health_condition.lower() != "none":
            queries.append(
                f"Airport security and customs regulations for carrying {health_condition} medicines/equipment "
                f"(like insulin/syringes) into {country}. Prescription requirements."
            )
            
        # Optional: Gender specific laws (e.g. Middle East restrictions, though less common now)
        if gender and gender.lower() == "female" and not is_domestic:
             queries.append(
                 f"Female business traveler legal restrictions or dress code laws for {country} business meetings."
             )

        # 3. Combine queries and execute
        # We combine them to get a holistic answer from the web search tool
        final_query = " | ".join(queries)
        
        print(f"DEBUG: Agent Generated Query -> {final_query}") # Helpful for your Hackathon demo
        
        return search_web(final_query, 'detailed')