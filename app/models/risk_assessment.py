# Data model for risk assessment

class RiskAssessment:
    def __init__(self, traveler, destination, risks):
        self.traveler = traveler
        self.destination = destination
        self.risks = risks