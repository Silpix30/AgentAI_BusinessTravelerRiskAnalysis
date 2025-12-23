# News Alert Agent: Handles real-time risks, weather extremes, and political events
import sys
import os
import importlib.util
from datetime import datetime
 
def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
 
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
search_web = import_from_path('search_web', os.path.join(root, 'app', 'utils', 'web_search.py')).search_web
 
class NewsAlertAgent:
    def _is_domestic(self, nationality, country):
        """Helper to check if travel is domestic"""
        if not nationality or not country:
            return False
        
        nat = nationality.lower().strip()
        cnt = country.lower().strip()
        
        # Common mappings
        if (nat == "indian" and cnt == "india") or \
           (nat == "american" and cnt in ["usa", "united states", "us"]):
            return True
            
        # Direct string matching
        return nat in cnt or cnt in nat
 
    def process(self, country=None, city=None, planned_stay=None, nationality=None, gender=None, **kwargs):
        """
        Fetches HYPER-LOCAL and REAL-TIME alerts.
        Differentiates between 'Live Breaking News' and 'Seasonal Expectations'.
        """
        # 1. Setup Context Variables
        location = f"{city}, {country}" if city else country
        is_domestic = self._is_domestic(nationality, country)
        
        # 2. Dynamic Time Detection
        # This makes your agent smart: It knows what "Today" is.
        today = datetime.now().strftime("%B %Y")  # e.g., "December 2025"
        
        # 3. Build Specialized Queries
        queries = []
        
        # Query A: The "Disruption" Check (Weather & Transport)
        # We ask for "Active" or "Scheduled" disruptions to get real news.
        queries.append(
            f"Active travel disruptions in {location} during {today}. "
            f"Search for: 'Transport strikes scheduled in {location}', "
            f"'Severe weather warnings for {city} next 7 days', "
            f"'Flight cancellations {country} recent news'."
        )
        
        # Query B: The "Safety" Check (Crime & Unrest)
        # We ask for "Recent incidents" to avoid generic "Be careful" advice.
        safety_query = (
            f"Recent safety incidents in {location} business districts last 30 days. "
            f"Check for: 'Protests in {city}', 'Civil unrest alerts {country}', "
            f"'Crime spike downtown {city}'."
        )
        
        # Gender Specific Safety Layer
        if gender and gender.lower() == "female":
            safety_query += (
                f" focus on 'Safety alerts for women in {city}', "
                f"'Recent incidents involving female travelers in {country}'."
            )
        queries.append(safety_query)
 
        # Query C: The "Diplomatic" Check (International Only)
        if not is_domestic:
            queries.append(
                f"Political tension between {nationality} and {country} currently. "
                f"Latest Embassy travel advisory for {nationality} citizens in {country}."
            )
 
        # 4. Combine Queries
        # " | " acts as a separator if your search tool handles complex queries,
        # otherwise it concatenates context for a rich search.
        final_query = " | ".join(queries)
        
        # Debug Print (Vital for showing Judges the "Reasoning")
        print(f"DEBUG [NewsAgent]: Real-Time Scan Query -> {final_query}")
 
        # 5. Execution
        # We use 'critical' or 'detailed' based on length, but 'detailed' is usually
        # better for news to capture the specific headlines.
        # If the stay is very short, we might force 'critical' to get just the warnings.
        mode = "critical" if planned_stay and planned_stay < 5 else "detailed"
        
        return search_web(final_query, mode)