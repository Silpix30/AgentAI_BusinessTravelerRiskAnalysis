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
Orchestrator = import_from_path('Orchestrator', os.path.join(root, 'app', 'orchestrator.py')).Orchestrator
ComplianceAgent = import_from_path('ComplianceAgent', os.path.join(root, 'app', 'agents', 'compliance_agent.py')).ComplianceAgent
HealthAgent = import_from_path('HealthAgent', os.path.join(root, 'app', 'agents', 'health_agent.py')).HealthAgent
TravelAgent = import_from_path('TravelAgent', os.path.join(root, 'app', 'agents', 'travel_agent.py')).TravelAgent
AccommodationAgent = import_from_path('AccommodationAgent', os.path.join(root, 'app', 'agents', 'accommodation_agent.py')).AccommodationAgent
NewsAlertAgent = import_from_path('NewsAlertAgent', os.path.join(root, 'app', 'agents', 'news_alert_agent.py')).NewsAlertAgent
LanguageGuideAgent = import_from_path('LanguageGuideAgent', os.path.join(root, 'app', 'agents', 'language_guide_agent.py')).LanguageGuideAgent
EmergencyContactAgent = import_from_path('EmergencyContactAgent', os.path.join(root, 'app', 'agents', 'emergency_contact_agent.py')).EmergencyContactAgent



import streamlit as st

st.set_page_config(page_title="Business Traveler Risk Dashboard", layout="centered")
st.title("Business Traveler Risk Analysis Dashboard")

st.write("Enter your travel details to get personalized recommendations and compliance checks.")


agents = {
    "compliance": ComplianceAgent(),
    "health": HealthAgent(),
    "travel": TravelAgent(),
    "accommodation": AccommodationAgent(),
    "news_alert": NewsAlertAgent(),
    "language_guide": LanguageGuideAgent(),
    "emergency_contact": EmergencyContactAgent(),
}

orchestrator = Orchestrator(agents)

import datetime

# Main Travel Details
country = st.text_input("Country to Visit", st.session_state.get("country", "USA"))
city = st.text_input("City", st.session_state.get("city", ""))

# Create two columns for Planned Stay and Budget
col1, col2 = st.columns(2)
with col1:
    planned_stay = st.number_input("Planned Stay (days)", min_value=1, max_value=365, value=st.session_state.get("planned_stay", 8), step=1)
with col2:
    budget_range = st.select_slider(
        "Budget per Day (USD)",
        options=["$0-50", "$50-100", "$100-150", "$150-200", "$200-300", "$300+"],
        value=st.session_state.get("budget_range", "$100-150")
    )

purpose = st.selectbox("Purpose", ["Client Meetings", "Conference", "Training", "Business Visit", "Site Inspection", "Other"], index=0)


# Traveler Profile Section
st.subheader("Traveler Profile")
nationality = st.text_input("Nationality", st.session_state.get("nationality", ""))



# Gender selection (move above WHO logic)
gender = st.selectbox("Gender", ["Female", "Male", "Other", "Prefer not to say"], index=0, key="gender_select")


# Use a curated list of health conditions and map to WHO indicator codes if available
curated_conditions = [
    "None",
    "Diabetes",
    "Asthma",
    "Hypertension",
    "Heart Disease",
    "Pregnancy",
    "Other"
]
# Map to WHO indicator codes (update codes as needed based on your indicator list)
curated_indicator_map = {
    "Diabetes": "MORT_DIAB",
    "Asthma": "ASTHMA_001",
    "Hypertension": None,
    "Heart Disease": "MORT_CVD",
    "Pregnancy": "MMR",
}

selected_condition = st.selectbox(
    "Health Condition",
    curated_conditions,
    index=0
)
other_condition = ""
if selected_condition == "Other":
    other_condition = st.text_input("Please specify your health condition(s) or symptoms")
    health_conditions = other_condition
elif selected_condition != "None":
    health_conditions = selected_condition
else:
    health_conditions = selected_condition

# WHO indicator code mapping for each health condition
who_indicator_map = {
    "Diabetes": "NCD_BMI_30",  # Example: Overweight/obesity as a diabetes risk
    "Hypertension": "NCD_BMI_30",  # No direct hypertension indicator, use related
    "Asthma": "ASTHMA_001",  # Example code, replace with actual if available
    "Heart Disease": "CVD_001",  # Example code, replace with actual if available
    "Allergies": None,  # No direct indicator
    "Immunocompromised": None,  # No direct indicator
    "Pregnancy": None,  # No direct indicator
}

# Import WHO API using custom import function
try:
    who_api = import_from_path('who_api', os.path.join(root, 'app', 'utils', 'who_api.py'))
except:
    who_api = None

# Gender code mapping for WHO API
gender_code_map = {
    "Female": "FMLE",
    "Male": "MLE",
    "Other": None,
    "Prefer not to say": None
}


# Fetch and display WHO data if available
who_data = None
who_error = None
if who_api and health_conditions in who_indicator_map and who_indicator_map[health_conditions]:
    indicator_code = who_indicator_map[health_conditions]
    gender_code = gender_code_map.get(gender)
    filters = None
    if gender_code:
        filters = f"$filter=Dim1 eq '{gender_code}'"
    try:
        who_data = who_api.get_who_indicator_data(indicator_code, filters)
    except Exception as e:
        who_error = str(e)

# Rule-based health advice for each health condition and gender
health_advice = {
    ("Diabetes", "Female"): "Women with diabetes should carry extra medication, monitor blood sugar frequently, and be aware of hormonal changes that may affect glucose levels. Carry snacks and stay hydrated.",
    ("Diabetes", "Male"): "Men with diabetes should monitor blood sugar, carry medication, and avoid excessive alcohol. Stay active and hydrated.",
    ("Hypertension", "Female"): "Women with hypertension should avoid high-sodium foods, carry blood pressure medication, and monitor blood pressure regularly. Be cautious with over-the-counter meds.",
    ("Hypertension", "Male"): "Men with hypertension should avoid salty foods, carry medication, and monitor blood pressure. Limit caffeine and alcohol.",
    ("Asthma", "Female"): "Women with asthma should carry inhalers, avoid triggers, and have an asthma action plan. Inform travel companions.",
    ("Asthma", "Male"): "Men with asthma should carry inhalers, avoid triggers, and have an asthma action plan. Inform travel companions.",
    ("Heart Disease", "Female"): "Women with heart disease should carry nitroglycerin or other prescribed meds, avoid strenuous activity, and know the location of nearby hospitals.",
    ("Heart Disease", "Male"): "Men with heart disease should carry prescribed meds, avoid overexertion, and know the location of nearby hospitals.",
    ("Allergies", "Female"): "Women with allergies should carry antihistamines and epinephrine if prescribed. Inform travel companions and avoid known allergens.",
    ("Allergies", "Male"): "Men with allergies should carry antihistamines and epinephrine if prescribed. Inform travel companions and avoid known allergens.",
    ("Immunocompromised", "Female"): "Immunocompromised women should avoid raw foods, crowded places, and ensure all vaccinations are up to date. Carry a doctor's note if needed.",
    ("Immunocompromised", "Male"): "Immunocompromised men should avoid raw foods, crowded places, and ensure all vaccinations are up to date. Carry a doctor's note if needed.",
    ("Pregnancy", "Female"): "Pregnant women should consult their doctor before travel, avoid risky foods, stay hydrated, and know the location of medical facilities.",
}

# Display WHO data only if it's successful (no errors and has records)
if who_data and 'error' not in who_data and who_data.get('records_found', 0) > 0:
    st.subheader("WHO Data for Selected Health Condition and Gender")
    st.write(who_data)

# Store in session state for multipage access
st.session_state["country"] = country
st.session_state["city"] = city
st.session_state["planned_stay"] = planned_stay
st.session_state["budget_range"] = budget_range
st.session_state["purpose"] = purpose
st.session_state["nationality"] = nationality
st.session_state["health_conditions"] = health_conditions
st.session_state["gender"] = gender

# Determine season from current month (Northern Hemisphere logic) - fallback only
month = datetime.datetime.now().month
if month in [12, 1, 2]:
    season = "winter"
elif month in [3, 4, 5]:
    season = "spring"
elif month in [6, 7, 8]:
    season = "summer"
else:
    season = "autumn"

# Import web search for real-time weather (used when fetching recommendations)
try:
    search_web = import_from_path('search_web', os.path.join(root, 'app', 'utils', 'web_search.py')).search_web
except:
    search_web = None


# Navigation state (robust initialization)
selected_agent = st.session_state.get("selected_agent", None)



selected_agent = st.session_state.get("selected_agent", None)

if selected_agent and selected_agent in agents:
    st.subheader(f"{selected_agent.replace('_', ' ').title()} Details")
    # Show detail level indicator
    detail_mode = "Critical Info Only" if planned_stay < 10 else "Detailed Info"
    st.caption(f"{detail_mode} for {planned_stay} day stay")
    if not country:
        st.warning("Please enter a country to view details.")
    else:
        if selected_agent == "travel":
            result = agents[selected_agent].process(
                country=country,
                city=city,
                season=season.lower(),
                planned_stay=planned_stay,
                nationality=nationality,
                gender=gender,                      
                health_condition=health_conditions, 
                purpose=purpose
            )
            st.write(result)
        elif selected_agent == "health":
            result = agents[selected_agent].process(
                country=country, 
                city=city, 
                gender=gender, 
                health_conditions=health_conditions,
                nationality=nationality,
                planned_stay=planned_stay
            )
            st.write(result)
        else:
            result = agents[selected_agent].process(
                country=country, 
                city=city, 
                planned_stay=planned_stay,
                nationality=nationality,
                gender=gender,
                health_conditions=health_conditions,
                budget_range=budget_range
            )
            st.write(result)
    if st.button("Back to Dashboard"):
        st.session_state.selected_agent = None
        st.rerun()
else:
    if st.button("Get Recommendations") and country:
        # Fetch real-time weather and season for the country
        weather_info = None
        season_detected = season  # Fallback to hardcoded season
        
        if search_web:
            try:
                # Get current weather and season
                weather_query = f"What is the current season and weather in {city+', ' if city else ''}{country} right now in December 2025? Reply with just the season name (summer/winter/spring/autumn) and a brief weather description."
                weather_info = search_web(weather_query, "critical")
                
                # Extract season from weather info (default to fallback if not detected)
                weather_lower = weather_info.lower()
                if "summer" in weather_lower:
                    season_detected = "summer"
                elif "winter" in weather_lower:
                    season_detected = "winter"
                elif "spring" in weather_lower:
                    season_detected = "spring"
                elif "autumn" in weather_lower or "fall" in weather_lower:
                    season_detected = "autumn"
            except Exception as e:
                # If weather fetch fails, use fallback season
                pass
        
        st.subheader(f"Recommendations for {country}")
        # Show detail level indicator
        detail_mode = "Critical Info Only" if planned_stay < 10 else "Detailed Info"
        if weather_info:
            st.caption(f"🌤️ Current Weather & Season: {weather_info[:150]}{'...' if len(weather_info) > 150 else ''}")
        else:
            st.caption(f"(Season auto-detected as {season_detected.title()})")
        st.caption(f"📅 {detail_mode} for {planned_stay} day stay")
        st.markdown("---")
        cols = st.columns(2)
        agent_blocks = list(agents.items())
        for idx, (agent_type, agent) in enumerate(agent_blocks):
            with cols[idx % 2]:
                block_title = agent_type.replace('_', ' ').title()
                with st.expander(block_title):
                    if agent_type == "travel":
                        result = agent.process(
                            country=country,
                            city=city,
                            season=season_detected,
                            planned_stay=planned_stay,
                            nationality=nationality,
                            gender=gender,                 
                            health_condition=health_conditions, 
                            purpose=purpose  
                        )
                        st.write(result)
                    elif agent_type == "health":
                        result = agent.process(
                            country=country, 
                            city=city, 
                            gender=gender, 
                            health_conditions=health_conditions,
                            nationality=nationality,
                            planned_stay=planned_stay
                        )
                        st.write(result)
                    else:
                        result = agent.process(
                            country=country, 
                            city=city, 
                            planned_stay=planned_stay,
                            nationality=nationality,
                            gender=gender,
                            health_conditions=health_conditions,
                            budget_range=budget_range
                        )
                        st.write(result)
    else:
        st.info("Enter a country and click 'Get Recommendations' to see results.")

