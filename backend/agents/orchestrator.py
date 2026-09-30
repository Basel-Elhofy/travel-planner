"""
Orchestrator Agent
==================
The central coordinator that manages the execution of all sub-agents.
Uses the blackboard for inter-agent communication.
Executes agents in the correct order and handles errors.
"""
import asyncio
import logging
from blackboard.blackboard import Blackboard
from models.schemas import TravelRequest, PlanStatus
from agents.planner import PlannerAgent
from agents.flight import FlightAgent
from agents.hotels import HotelsAgent
from agents.activities import ActivitiesAgent
from agents.budget import BudgetAgent
from agents.output import OutputAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    The Orchestrator coordinates all sub-agents.
    It manages the workflow, handles errors, and ensures
    agents execute in the correct order.
    """

    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self.name = "OrchestratorAgent"

        # Initialize all sub-agents with shared blackboard
        self.planner = PlannerAgent(blackboard)
        self.flight_agent = FlightAgent(blackboard)
        self.hotels_agent = HotelsAgent(blackboard)
        self.activities_agent = ActivitiesAgent(blackboard)
        self.budget_agent = BudgetAgent(blackboard)
        self.output_agent = OutputAgent(blackboard)

    async def run(self, request: TravelRequest) -> dict:
        """
        Execute the full travel planning workflow.
        
        Args:
            request: User's travel request (location, dates, duration, budget)
            
        Returns:
            Dictionary with plan results and Excel file path
        """
        logger.info(f"[{self.name}] Starting travel planning orchestration...")
        logger.info(
            f"[{self.name}] Destination: {request.location}, "
            f"Duration: {request.duration_days} days, "
            f"Budget: ${request.budget}"
        )

        try:
            # Step 0: Write request to blackboard
            await self.blackboard.clear()
            await self.blackboard.set_request(request)
            await self.blackboard.set_status(PlanStatus.PLANNING)

            # Step 1: Planner Agent - creates day-by-day structure
            logger.info(f"[{self.name}] Phase 1: Planning")
            await self.planner.run()

            # Step 2: Run Flight, Hotels, and Activities agents in parallel
            logger.info(f"[{self.name}] Phase 2: Searching flights, hotels, activities (parallel)")
            await asyncio.gather(
                self.flight_agent.run(),
                self.hotels_agent.run(),
                self.activities_agent.run(),
            )

            # Step 3: Budget Agent - calculates costs
            logger.info(f"[{self.name}] Phase 3: Budget calculation")
            await self.budget_agent.run()

            # Step 4: Output Agent - combines results and exports to Excel
            logger.info(f"[{self.name}] Phase 4: Generating output")
            excel_path = await self.output_agent.run()

            # Build final result
            plan = await self.blackboard.build_plan()

            logger.info(f"[{self.name}] Travel planning completed successfully!")
            logger.info(f"[{self.name}] Excel file: {excel_path}")

            return {
                "success": True,
                "plan": plan.model_dump(),
                "excel_path": excel_path,
                "message": "Travel plan generated successfully!",
            }

        except Exception as e:
            error_msg = f"Travel planning failed: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            await self.blackboard.set_error(error_msg)
            await self.blackboard.set_status(PlanStatus.FAILED)

            return {
                "success": False,
                "error": error_msg,
                "excel_path": None,
            }
