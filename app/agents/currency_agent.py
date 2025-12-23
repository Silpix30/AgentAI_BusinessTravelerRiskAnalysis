# currency_agent.py

import re
from app.agent import AzureAIAgent

def normalize(text):
    return re.sub(r'[^a-z ]', '', text.strip().lower())

class CurrencyAgent:
    def __init__(self):
        self.agent = AzureAIAgent(agent_name="CurrencyAgent")

    def process(self, payload):
        nationality = payload.get('nationality', '')
        prompt = f"What is the official currency code (like USD, EUR, INR, etc.) for a person whose nationality is '{nationality}'? Only return the ISO currency code."
        response = self.agent.run(prompt)
        matches = re.findall(r'([A-Z]{3})', response)
        # Filter out 'ISO' and pick the first valid code
        currency = next((m for m in matches if m != 'ISO'), "USD")
        return { 'currency': currency }

currency_agent = CurrencyAgent().process
