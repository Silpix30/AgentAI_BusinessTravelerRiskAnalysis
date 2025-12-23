
from app.orchestrator import Orchestrator
from app.agents.compliance_agent import ComplianceAgent
from app.agents.health_agent import HealthAgent
from app.agents.travel_agent import TravelAgent
from app.agents.accommodation_agent import AccommodationAgent
from app.agents.news_alert_agent import NewsAlertAgent
from app.agents.language_guide_agent import LanguageGuideAgent
from app.agents.emergency_contact_agent import EmergencyContactAgent

if __name__ == "__main__":
    # Register all agents in a dictionary
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

    # Example: invoke each agent for demonstration
    for agent_type in agents:
        if agent_type == "travel":
            # Demo: TravelAgent with specific parameters
            result = orchestrator.handle_request(
                agent_type,
                country="UK",
                city="London",
                season="winter"
            )
            print(f"{agent_type.capitalize()} Agent (London, UK, winter): {result}")
        else:
            result = orchestrator.handle_request(agent_type)
            print(f"{agent_type.capitalize()} Agent: {result}")
