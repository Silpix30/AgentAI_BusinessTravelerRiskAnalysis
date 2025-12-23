from flask import Flask, request, jsonify
from flask_cors import CORS
from app.orchestrator import Orchestrator
from app.agents.compliance_agent import ComplianceAgent
from app.agents.health_agent import HealthAgent
from app.agents.travel_agent import TravelAgent
from app.agents.accommodation_agent import AccommodationAgent
from app.agents.news_alert_agent import NewsAlertAgent
from app.agents.language_guide_agent import LanguageGuideAgent
from app.agents.emergency_contact_agent import EmergencyContactAgent
from app.agents.currency_agent import currency_agent

# Import web search utility for chatbot
try:
    from app.utils.web_search import search_web
except ImportError:
    search_web = None

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Register all agents
agents = {
    "compliance": ComplianceAgent(),
    "health": HealthAgent(),
    "travel": TravelAgent(),
    "accommodation": AccommodationAgent(),
    "news_alert": NewsAlertAgent(),
    "language_guide": LanguageGuideAgent(),
    "emergency_contact": EmergencyContactAgent(),
    "currency_agent": type('CurrencyAgent', (), { 'process': staticmethod(currency_agent) })(),
}
orchestrator = Orchestrator(agents)

@app.route("/api/agent/<agent_type>", methods=["POST"])
def agent_handler(agent_type):
    data = request.json or {}
    if agent_type not in agents:
        return jsonify({"error": f"Unknown agent: {agent_type}"}), 400
    try:
        result = orchestrator.handle_request(agent_type, **data)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/agent/health_hospitals", methods=["POST"])
def health_hospitals_handler():
    data = request.json or {}
    country = data.get("country")
    # Dummy hospital data, replace with Azure/Foundry/WHO API as needed
    hospitals_by_country = {
        "USA": ["Mayo Clinic", "Cleveland Clinic", "Johns Hopkins Hospital"],
        "India": ["Apollo Hospitals", "Fortis Healthcare", "AIIMS Delhi"],
        "UK": ["St Thomas' Hospital", "Royal London Hospital", "Addenbrooke's Hospital"],
        "Germany": ["Charité – Universitätsmedizin Berlin", "University Hospital Heidelberg", "LMU Klinikum Munich"],
    }
    hospitals = hospitals_by_country.get(country, [])
    return jsonify({"hospitals": hospitals})

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})

@app.route("/api/chat", methods=["POST"])
def chat_handler():
    """Handle chatbot queries using web search agent"""
    data = request.json or {}
    query = data.get("query", "")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Use web search to get response
        if search_web:
            response = search_web(query, "detailed")
        else:
            # Fallback response if search_web is not available
            response = "I apologize, but the search service is currently unavailable. Please check official government websites or contact your travel agent for up-to-date information."
        
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
