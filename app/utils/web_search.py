# Utility for web search (e.g., news, weather)
# Uses Azure AI Foundry Agent for queries

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app.agent import AzureAIAgent

# Create a singleton instance for reuse
_agent_instance = None

def get_agent():
    """Get or create the Azure AI agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AzureAIAgent(agent_name="TravelSearchAgent")
    return _agent_instance

def search_web(query, detail_level="detailed"):
    """
    Uses Azure AI Foundry Agent to get answers for travel-related queries.
    
    Args:
        query: The search query
        detail_level: Either "critical" (for short stays < 10 days) or "detailed" (for longer stays)
    """
    try:
        agent = get_agent()
        # Format the query based on detail level
        if detail_level == "critical":
            full_query = f"You are a travel and compliance assistant. Provide ONLY the most critical, essential information that a traveler must know. Be concise and focus on must-know facts, requirements, and safety information: {query}"
        else:
            full_query = f"You are a travel and compliance assistant. Provide detailed, comprehensive, up-to-date information with all relevant details and recommendations: {query}"
        result = agent.run(full_query)
        return result
    except Exception as e:
        return f"Azure AI Agent error: {str(e)}"