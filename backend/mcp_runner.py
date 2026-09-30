"""
MCP Server Runner
=================
Run this file to start the Travel Planner as an MCP server.
AI assistants and MCP clients can then connect to create travel plans.

Usage:
    python mcp_runner.py
"""
import asyncio
import logging
from mcp.server import run_stdio_server
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from blackboard.blackboard import Blackboard
from agents.orchestrator import OrchestratorAgent
from models.schemas import TravelRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("travel-planner")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="create_travel_plan",
                description="Create a complete travel plan including flights, hotels, activities, and budget. Returns an Excel file with the full itinerary.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Destination city or country"},
                        "start_date": {"type": "string", "format": "date", "description": "Trip start date (YYYY-MM-DD)"},
                        "duration_days": {"type": "integer", "minimum": 1, "maximum": 30, "description": "Number of days"},
                        "budget": {"type": "number", "minimum": 0, "description": "Total budget in USD"},
                        "travelers": {"type": "integer", "minimum": 1, "maximum": 10, "default": 1},
                        "preferences": {"type": "string", "description": "Optional preferences"},
                    },
                    "required": ["location", "start_date", "duration_days", "budget"],
                },
            ),
            Tool(
                name="get_plan_status",
                description="Get the current status of the travel planning system.",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "create_travel_plan":
            return await _create_plan(arguments)
        elif name == "get_plan_status":
            return [TextContent(type="text", text="Travel Planner MCP Server is running.")]
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def _create_plan(args: dict) -> list[TextContent]:
        try:
            request = TravelRequest(
                location=args["location"],
                start_date=args["start_date"],
                duration_days=args["duration_days"],
                budget=args["budget"],
                travelers=args.get("travelers", 1),
                preferences=args.get("preferences"),
            )
            blackboard = Blackboard()
            orchestrator = OrchestratorAgent(blackboard)
            result = await orchestrator.run(request)

            if result["success"]:
                plan = result["plan"]
                text = (
                    f"Travel plan created!\n"
                    f"Destination: {plan['request']['location']}\n"
                    f"Flights: {len(plan['flights'])}\n"
                    f"Hotels: {len(plan['hotels'])}\n"
                    f"Activities: {len(plan['activities'])}\n"
                    f"Total: ${plan['budget']['total']}\n"
                    f"Excel: {result['excel_path']}"
                )
            else:
                text = f"Error: {result['error']}"
            return [TextContent(type="text", text=text)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def main():
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
