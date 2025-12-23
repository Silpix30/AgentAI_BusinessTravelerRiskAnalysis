# Data model for travel itinerary

class Itinerary:
    def __init__(self, traveler, destination, duration, activities):
        self.traveler = traveler
        self.destination = destination
        self.duration = duration
        self.activities = activities