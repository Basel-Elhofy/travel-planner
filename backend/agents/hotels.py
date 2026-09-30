"""
Hotels Agent
============
Searches for hotels at the destination.
In production, this would connect to a hotel API (Booking.com, Expedia, etc.).
For demo purposes, generates realistic mock hotel data.
Writes hotel results to the blackboard.
"""
import asyncio
import logging
import random
from blackboard.blackboard import Blackboard
from models.schemas import HotelResult, PlanStatus

logger = logging.getLogger(__name__)

HOTEL_NAMES = [
    "Grand Palace Hotel",
    "Marina Bay Resort",
    "City Center Inn",
    "Royal Orchid Hotel",
    "Sunset View Resort",
    "The Metropolitan",
    "Harbor Lights Hotel",
    "Mountain Lodge & Spa",
]

AMENITIES_POOL = [
    "Free WiFi",
    "Pool",
    "Spa",
    "Gym",
    "Restaurant",
    "Bar",
    "Room Service",
    "Parking",
    "Airport Shuttle",
    "Beach Access",
    "Business Center",
    "Concierge",
]


class HotelsAgent:
    """
    The Hotels Agent searches for hotels at the destination.
    Writes hotel options to the blackboard.
    """

    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self.name = "HotelsAgent"

    async def run(self) -> list[HotelResult]:
        """Execute hotel search and write results to blackboard."""
        logger.info(f"[{self.name}] Starting hotel search...")

        request = await self.blackboard.get_request()
        if not request:
            raise ValueError(f"[{self.name}] No request found on blackboard")

        # Simulate API call delay
        await asyncio.sleep(0.5)

        # Generate mock hotel data
        hotels = self._generate_hotels(request)

        # Write to blackboard
        await self.blackboard.set_hotels(hotels)
        await self.blackboard.set_status(PlanStatus.HOTELS)

        logger.info(f"[{self.name}] Found {len(hotels)} hotel options.")
        return hotels

    def _generate_hotels(self, request) -> list[HotelResult]:
        """Generate realistic mock hotel data."""
        hotels = []
        num_hotels = random.randint(4, 7)

        for i in range(num_hotels):
            name = HOTEL_NAMES[i % len(HOTEL_NAMES)]
            if i >= len(HOTEL_NAMES):
                name += f" {i + 1}"

            rating = round(random.uniform(3.5, 5.0), 1)
            base_price = random.uniform(50, 400)
            # Higher rated hotels cost more
            price = round(base_price * (rating / 4.0), 2)

            num_amenities = random.randint(3, 7)
            amenities = random.sample(AMENITIES_POOL, num_amenities)

            hotels.append(
                HotelResult(
                    name=name,
                    address=f"{random.randint(1, 999)} Main St, {request.location}",
                    rating=rating,
                    price_per_night=price,
                    amenities=amenities,
                )
            )

        # Sort by rating (descending)
        hotels.sort(key=lambda h: h.rating, reverse=True)
        return hotels
