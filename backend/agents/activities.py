"""
Activities Agent
================
Searches for activities and attractions at the destination.
In production, this would connect to an activities API (TripAdvisor, Viator, etc.).
For demo purposes, generates realistic mock activity data.
Writes activity results to the blackboard.
"""
import asyncio
import logging
import random
from blackboard.blackboard import Blackboard
from models.schemas import ActivityResult, PlanStatus

logger = logging.getLogger(__name__)

ACTIVITIES_DATA = [
    ("City Walking Tour", "Sightseeing", "Guided tour of the city's historic landmarks and hidden gems.", 25.0, 3.0, 4.7),
    ("Museum of Art", "Culture", "World-class art collection spanning centuries.", 20.0, 2.5, 4.5),
    ("Cooking Class", "Food", "Learn to cook local cuisine with a professional chef.", 65.0, 3.0, 4.8),
    ("Boat Cruise", "Adventure", "Scenic cruise along the coastline with dinner.", 80.0, 4.0, 4.6),
    ("Hiking Trail", "Nature", "Breathtaking mountain trails for all skill levels.", 15.0, 5.0, 4.4),
    ("Wine Tasting", "Food", "Sample local wines at a vineyard estate.", 55.0, 2.0, 4.9),
    ("Historical Landmark", "Sightseeing", "Iconic monument with guided historical tours.", 12.0, 1.5, 4.3),
    ("Spa & Wellness", "Relaxation", "Full-day spa package with massage and treatments.", 120.0, 4.0, 4.8),
    ("Market Tour", "Culture", "Explore local markets and street food.", 30.0, 2.5, 4.5),
    ("Water Sports", "Adventure", "Jet skiing, parasailing, and more.", 90.0, 3.0, 4.2),
    ("Photography Tour", "Culture", "Capture the best spots with a local photographer.", 45.0, 3.0, 4.6),
    ("Nightlife Experience", "Entertainment", "VIP access to the best clubs and bars.", 70.0, 4.0, 4.1),
]


class ActivitiesAgent:
    """
    The Activities Agent searches for activities at the destination.
    Writes activity options to the blackboard.
    """

    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self.name = "ActivitiesAgent"

    async def run(self) -> list[ActivityResult]:
        """Execute activity search and write results to blackboard."""
        logger.info(f"[{self.name}] Starting activity search...")

        request = await self.blackboard.get_request()
        if not request:
            raise ValueError(f"[{self.name}] No request found on blackboard")

        # Simulate API call delay
        await asyncio.sleep(0.5)

        # Generate mock activity data
        activities = self._generate_activities(request)

        # Write to blackboard
        await self.blackboard.set_activities(activities)
        await self.blackboard.set_status(PlanStatus.ACTIVITIES)

        logger.info(f"[{self.name}] Found {len(activities)} activities.")
        return activities

    def _generate_activities(self, request) -> list[ActivityResult]:
        """Generate realistic mock activity data."""
        activities = []
        num_activities = min(len(ACTIVITIES_DATA), random.randint(6, 10))

        selected = random.sample(ACTIVITIES_DATA, num_activities)

        for name, category, desc, price, duration, rating in selected:
            # Add some price variation
            varied_price = round(price * random.uniform(0.9, 1.2), 2)

            activities.append(
                ActivityResult(
                    name=name,
                    category=category,
                    description=desc,
                    price=varied_price,
                    duration_hours=duration,
                    rating=rating,
                )
            )

        # Sort by rating (descending)
        activities.sort(key=lambda a: a.rating, reverse=True)
        return activities
