"""
Output Agent
============
Combines all agent results from the blackboard into a final travel plan.
Exports the plan to an Excel file.
Writes the final plan and Excel path to the blackboard.
"""
import asyncio
import logging
from blackboard.blackboard import Blackboard
from models.schemas import PlanStatus
from excel.exporter import ExcelExporter

logger = logging.getLogger(__name__)


class OutputAgent:
    """
    The Output Agent reads all results from the blackboard,
    combines them into a final plan, and exports to Excel.
    """

    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self.name = "OutputAgent"

    async def run(self) -> str:
        """
        Execute output phase: combine results, export to Excel.
        Returns the path to the generated Excel file.
        """
        logger.info(f"[{self.name}] Starting output generation...")

        # Build the complete plan from blackboard
        plan = await self.blackboard.build_plan()

        # Export to Excel
        exporter = ExcelExporter()
        excel_path = exporter.export(plan)

        # Write to blackboard
        await self.blackboard.set_excel_path(excel_path)
        await self.blackboard.set_status(PlanStatus.COMPLETED)

        logger.info(f"[{self.name}] Plan exported to: {excel_path}")
        return excel_path
