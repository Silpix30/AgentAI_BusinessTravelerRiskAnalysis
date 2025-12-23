from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
from app.config import (
    TENANT_ID,
    CLIENT_ID,
    CLIENT_SECRET,
    PROJECT_ENDPOINT,
    MODEL_NAME
)
import time


class AzureAIAgent:
    def __init__(self, agent_name="LegalComplianceAgent"):
        """Initialize Azure AI Foundry Agent"""
        self.credential = ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        
        self.project = AIProjectClient(
            credential=self.credential,
            endpoint=PROJECT_ENDPOINT
        )
        
        # Create agent
        self.agent = self.project.agents.create_agent(
            model=MODEL_NAME,
            name=agent_name,
            instructions="You are a helpful AI assistant for legal compliance and travel planning."
        )
        
        print(f"✓ Agent created with ID: {self.agent.id}")

    def run(self, prompt: str) -> str:
        """Send a message to the agent and get response"""
        # Create a new thread
        thread = self.project.agents.threads.create()
        
        # Send user message
        self.project.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )
        
        # Run the agent
        run = self.project.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=self.agent.id
        )
        
        # Poll for completion
        while True:
            response = self.project.agents.runs.get(thread_id=thread.id, run_id=run.id)
            status = response.status
            
            if status in ("completed", "failed"):
                break
            time.sleep(1)
        
        if status == "completed":
            messages = list(self.project.agents.messages.list(thread_id=thread.id))
            for msg in messages:
                if msg.role == "assistant":
                    return msg.content[0].text.value
        
        return "Error: Run failed"
