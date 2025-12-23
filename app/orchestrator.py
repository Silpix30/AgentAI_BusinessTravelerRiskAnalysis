# Orchestrator for dynamic agent invocation

class Orchestrator:
    def __init__(self, agents):
        self.agents = agents

    def handle_request(self, request_type, **kwargs):
        """Dynamically invoke the relevant agent(s) based on request_type."""
        agent = self.agents.get(request_type)
        if agent:
            # Special case for currency_agent: pass the whole payload as a dict
            if request_type == "currency_agent":
                return agent.process(kwargs)
            return agent.process(**kwargs)
        else:
            return f"No agent found for request type: {request_type}"