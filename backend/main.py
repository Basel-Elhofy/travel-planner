"""
Travel Planner - FastAPI Backend
================================
Main entry point for the Travel Planner multi-agent system.
Provides REST API endpoints and serves the frontend.
"""
import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from blackboard.blackboard import Blackboard
from agents.orchestrator import OrchestratorAgent
from models.schemas import TravelRequest

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global state
blackboard = Blackboard()
orchestrator = OrchestratorAgent(blackboard)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Travel Planner API starting up...")
    yield
    logger.info("Travel Planner API shutting down...")


app = FastAPI(
    title="Travel Planner Multi-Agent System",
    description="AI-powered travel planning with orchestrator, planner, flight, hotels, activities, budget, and output agents.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def root():
    """Serve the frontend."""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(frontend_path)


@app.post("/api/plan", response_model=dict)
async def create_travel_plan(request: TravelRequest):
    """
    Create a complete travel plan.
    
    This endpoint triggers the orchestrator which coordinates
    all sub-agents (planner, flight, hotels, activities, budget, output)
    to generate a complete travel plan with Excel export.
    """
    logger.info(f"Received travel plan request: {request.location}, {request.duration_days} days, ${request.budget}")

    try:
        result = await orchestrator.run(request)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        logger.error(f"Error creating travel plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """Get the current status of the planning system."""
    status = await blackboard.get_status()
    return {
        "status": status.value if status else "idle",
        "blackboard_keys": list((await blackboard.read_all()).keys()),
    }


@app.get("/api/download/{filename}")
async def download_excel(filename: str):
    """Download a generated Excel file."""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    filepath = os.path.join(output_dir, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )


@app.get("/api/plans")
async def list_plans():
    """List all generated travel plans."""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    if not os.path.exists(output_dir):
        return {"plans": []}

    files = [f for f in os.listdir(output_dir) if f.endswith(".xlsx")]
    plans = []
    for f in sorted(files, reverse=True):
        plans.append({
            "filename": f,
            "download_url": f"/api/download/{f}",
        })
    return {"plans": plans}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
