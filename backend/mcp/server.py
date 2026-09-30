"""
MCP (Model Context Protocol) Server
===================================
Exposes the Travel Planner as an MCP server so that AI assistants
and other MCP clients can create travel plans programmatically.

Tools exposed:
- create_travel_plan: Create a complete travel plan
- get_plan_status: Check the status of a plan
- export_plan_to_excel: Export a plan to Excel
"""
import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from blackboard.blackboard import Blackboard
from agents.orchestrator import OrchestratorAgent
from models.schemas import TravelRequest

logger = logging.getLogger(__name__)


def create_mcp_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("travel-planner")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available MCP tools."""
        return [
            Tool(
                name="create_travel_plan",
                description="Create a complete travel plan including flights, hotels, activities, and budget. Returns an Excel file with the full itinerary.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Destination city or country",
                        },
                        "start_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Trip start date (YYYY-MM-DD)",
                        },
                        "duration_days": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 30,
                            "description": "Number of days for the trip",
                        },
                        "budget": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Total budget in USD",
                        },
                        "travelers": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 1,
                            "description": "Number of travelers",
                        },
                        "preferences": {
                            "type": "string",
                            "description": "Optional preferences (e.g., 'beach', 'adventure', 'cultural')",
                        },
                    },
                    "required": ["location", "start_date", "duration_days", "budget"],
                },
            ),
            Tool(
                name="get_plan_status",
                description="Get the current status of the travel planning system.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls from MCP clients."""
        if name == "create_travel_plan":
            return await _handle_create_plan(arguments)
        elif name == "get_plan_status":
            return await _handle_get_status()
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def _handle_create_plan(arguments: dict) -> list[TextContent]:
        """Handle create_travel_plan tool call."""
        try:
            request = TravelRequest(
                location=arguments["location"],
                start_date=arguments["start_date"],
                duration_days=arguments["duration_days"],
                budget=arguments["budget"],
                travelers=arguments.get("travelers", 1),
                preferences=arguments.get("preferences"),
            )

            blackboard = Blackboard()
            orchestrator = OrchestratorAgent(blackboard)
            result = await orchestrator.run(request)

            if result["success"]:
                plan = result["plan"]
                response = (
                    f"Travel plan created successfully!\n\n"
                    f"Destination: {plan['request']['location']}\n"
                    f"Duration: {plan['request']['duration_days']} days\n"
                    f"Flights found: {len(plan['flights'])}\n"
                    f"Hotels found: {len(plan['hotels'])}\n"
                    f"Activities found: {len(plan['activities'])}\n"
                    f"Total cost: ${plan['budget']['total']}\n"
                    f"Remaining budget: ${plan['budget']['remaining']}\n"
                    f"Excel file: {result['excel_path']}"
                )
            else:
                response = f"Error: {result['error']}"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error creating travel plan: {str(e)}")]

    async def _handle_get_status() -> list[TextContent]:
        """Handle get_plan_status tool call."""
        return [
            TextContent(
                type="text",
                text="Travel Planner MCP Server is running and ready to create travel plans.",
            )
        ]

    return server


async def run_mcp_server():
    """Run the MCP server with stdio transport."""
    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
