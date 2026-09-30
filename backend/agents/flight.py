"""
Flight Agent
============
Searches for flights to the destination.
In production, this would connect to a flight API (Amadeus, Skyscanner, etc.).
For demo purposes, generates realistic mock flight data.
Writes flight results to the blackboard.
"""
import asyncio
import logging
import random
from blackboard.blackboard import Blackboard
from models.schemas import FlightResult, PlanStatus

logger = logging.getLogger(__name__)

AIRLINES = [
    ("Emirates", "EK"),
    ("Qatar Airways", "QR"),
    ("Singapore Airlines", "SQ"),
    ("Lufthansa", "LH"),
    ("British Airways", "BA"),
    ("Air France", "AF"),
    ("Turkish Airlines", "TK"),
    ("Japan Airlines", "JL"),
]


class FlightAgent:
    """
    The Flight Agent searches for flights to the destination.
    Writes flight options to the blackboard.
    """

    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self.name = "FlightAgent"

    async def run(self) -> list[FlightResult]:
        """Execute flight search and write results to blackboard."""
        logger.info(f"[{self.name}] Starting flight search...")

        request = await self.blackboard.get_request()
        if not request:
            raise ValueError(f"[{self.name}] No request found on blackboard")

        # Simulate API call delay
        await asyncio.sleep(0.5)

        # Generate mock flight data
        flights = self._generate_flights(request)

        # Write to blackboard
        await self.blackboard.set_flights(flights)
        await self.blackboard.set_status(PlanStatus.FLIGHTS)

        logger.info(f"[{self.name}] Found {len(flights)} flight options.")
        return flights

    def _generate_flights(self, request) -> list[FlightResult]:
        """Generate realistic mock flight data."""
        flights = []
        base_price = random.randint(300, 1200)

        for airline_name, airline_code in AIRLINES[:5]:
            price_variation = random.uniform(0.8, 1.5)
            price = round(base_price * price_variation, 2)
            duration_hours = random.randint(6, 16)
            duration_mins = random.randint(0, 59)
            stops = random.choices([0, 1, 2], weights=[0.3, 0.5, 0.2])[0]

            flights.append(
                FlightResult(
                    airline=airline_name,
                    flight_number=f"{airline_code} {random.randint(100, 999)}",
                    departure=f"08:{random.randint(10, 59):02d}",
                    arrival=f"{random.randint(10, 23):02d}:{random.randint(10, 59):02d}",
                    price=price,
                    duration=f"{duration_hours}h {duration_mins}m",
                    stops=stops,
                )
            )

        # Sort by price
        flights.sort(key=lambda f: f.price)
        return flights
