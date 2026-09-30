"""
Budget Agent
============
Calculates the total budget breakdown based on flights, hotels, and activities.
Ensures the plan stays within the user's budget.
Writes budget results to the blackboard.
"""
import asyncio
import logging
from blackboard.blackboard import Blackboard
from models.schemas import BudgetResult, PlanStatus

logger = logging.getLogger(__name__)


class BudgetAgent:
    """
    The Budget Agent calculates costs and ensures the plan fits the budget.
    Writes budget breakdown to the blackboard.
    """

    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self.name = "BudgetAgent"

    async def run(self) -> BudgetResult:
        """Execute budget calculation and write results to blackboard."""
        logger.info(f"[{self.name}] Starting budget calculation...")

        request = await self.blackboard.get_request()
        if not request:
            raise ValueError(f"[{self.name}] No request found on blackboard")

        # Read other agents' results from blackboard
        flights = await self.blackboard.get_flights()
        hotels = await self.blackboard.get_hotels()
        activities = await self.blackboard.get_activities()

        # Calculate costs
        budget = self._calculate_budget(request, flights, hotels, activities)

        # Write to blackboard
        await self.blackboard.set_budget(budget)
        await self.blackboard.set_status(PlanStatus.BUDGET)

        logger.info(
            f"[{self.name}] Budget calculated: ${budget.total:.2f} "
            f"(remaining: ${budget.remaining:.2f})"
        )
        return budget

    def _calculate_budget(
        self, request, flights, hotels, activities
    ) -> BudgetResult:
        """Calculate the full budget breakdown."""
        # Cheapest flight (round trip approximation)
        flights_total = flights[0].price * 2 if flights else 0.0
        flights_total *= request.travelers

        # Best value hotel (highest rating, reasonable price)
        hotels_total = 0.0
        if hotels:
            best_hotel = max(hotels, key=lambda h: h.rating)
            hotels_total = best_hotel.price_per_night * request.duration_days

        # Activities (pick top activities within remaining budget)
        activities_total = 0.0
        remaining_for_activities = request.budget - flights_total - hotels_total
        for act in sorted(activities, key=lambda a: a.rating, reverse=True):
            if activities_total + act.price <= remaining_for_activities * 0.4:
                activities_total += act.price

        # Estimates
        food_estimate = request.duration_days * request.travelers * 50.0
        transport_estimate = request.duration_days * 20.0
        misc_estimate = request.budget * 0.05

        total = flights_total + hotels_total + activities_total + food_estimate + transport_estimate + misc_estimate
        remaining = request.budget - total

        return BudgetResult(
            flights_total=round(flights_total, 2),
            hotels_total=round(hotels_total, 2),
            activities_total=round(activities_total, 2),
            food_estimate=round(food_estimate, 2),
            transport_estimate=round(transport_estimate, 2),
            misc_estimate=round(misc_estimate, 2),
            total=round(total, 2),
            remaining=round(remaining, 2),
        )
