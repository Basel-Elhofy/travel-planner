"""
Planner Agent
=============
Receives location, time, duration, and budget from the user.
Creates the initial travel plan skeleton and day-by-day structure.
Writes the plan structure to the blackboard.
"""
import asyncio
import logging
from datetime import date, timedelta
from blackboard.blackboard import Blackboard
from models.schemas import TravelRequest, PlanStatus, DayPlan, ItineraryItem

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    The Planner Agent receives user input (location, dates, duration, budget)
    and creates a structured day-by-day itinerary skeleton.
    """

    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self.name = "PlannerAgent"

    async def run(self) -> list[DayPlan]:
        """
        Execute the planner: read request from blackboard,
        generate day-by-day structure, write back to blackboard.
        """
        logger.info(f"[{self.name}] Starting planning phase...")

        request = await self.blackboard.get_request()
        if not request:
            raise ValueError(f"[{self.name}] No request found on blackboard")

        logger.info(
            f"[{self.name}] Planning trip to {request.location} "
            f"for {request.duration_days} days starting {request.start_date}"
        )

        # Generate day-by-day skeleton
        itinerary = self._generate_day_structure(request)

        # Write to blackboard
        await self.blackboard.set_itinerary(itinerary)
        await self.blackboard.set_status(PlanStatus.PLANNING)

        logger.info(f"[{self.name}] Planning complete. {len(itinerary)} days planned.")
        return itinerary

    def _generate_day_structure(self, request: TravelRequest) -> list[DayPlan]:
        """Generate a day-by-day skeleton for the trip."""
        itinerary = []
        start = request.start_date

        for day_num in range(1, request.duration_days + 1):
            current_date = start + timedelta(days=day_num - 1)
            items = []

            # Morning activity
            items.append(
                ItineraryItem(
                    time="09:00",
                    activity="Morning Activity",
                    location=request.location,
                    cost=0.0,
                    notes="To be filled by Activities Agent",
                )
            )

            # Lunch
            items.append(
                ItineraryItem(
                    time="12:30",
                    activity="Lunch",
                    location=request.location,
                    cost=0.0,
                    notes="To be filled by Budget Agent",
                )
            )

            # Afternoon activity
            items.append(
                ItineraryItem(
                    time="14:00",
                    activity="Afternoon Activity",
                    location=request.location,
                    cost=0.0,
                    notes="To be filled by Activities Agent",
                )
            )

            # Dinner
            items.append(
                ItineraryItem(
                    time="19:00",
                    activity="Dinner",
                    location=request.location,
                    cost=0.0,
                    notes="To be filled by Budget Agent",
                )
            )

            # Last day: departure
            if day_num == request.duration_days:
                items.append(
                    ItineraryItem(
                        time="11:00",
                        activity="Departure",
                        location=request.location,
                        cost=0.0,
                        notes="Check-out and head to airport",
                    )
                )

            itinerary.append(
                DayPlan(
                    day=day_num,
                    date=current_date.isoformat(),
                    items=items,
                )
            )

        return itinerary
