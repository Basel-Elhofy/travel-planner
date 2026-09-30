# Travel Planner - Multi-Agent System

A complete multi-agent travel planning system built with FastAPI, the Blackboard pattern, and MCP (Model Context Protocol).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│                  (Central Coordinator)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│  PLANNER  │  │  FLIGHT   │  │  HOTELS   │
│   AGENT   │  │   AGENT   │  │   AGENT   │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
              ┌──────┴──────┐
              │  BLACKBOARD  │
              │ (Shared Mem) │
              └──────┬──────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│ACTIVITIES │ │  BUDGET   │ │  OUTPUT   │
│   AGENT   │ │   AGENT   │ │   AGENT   │
└───────────┘ └───────────┘ └───────────┘
```

## Agents

| Agent | Responsibility |
|-------|---------------|
| **Orchestrator** | Coordinates all agents, manages workflow |
| **Planner** | Receives user input, creates day-by-day structure |
| **Flight** | Searches for flights to destination |
| **Hotels** | Searches for hotels at destination |
| **Activities** | Finds activities and attractions |
| **Budget** | Calculates costs, ensures budget compliance |
| **Output** | Combines results, exports to Excel |

## Project Structure

```
travel-planner/
├── backend/
│   ├── agents/           # All agent implementations
│   │   ├── orchestrator.py
│   │   ├── planner.py
│   │   ├── flight.py
│   │   ├── hotels.py
│   │   ├── activities.py
│   │   ├── budget.py
│   │   └── output.py
│   ├── blackboard/       # Shared memory (Blackboard pattern)
│   │   └── blackboard.py
│   ├── mcp/              # MCP server implementation
│   │   └── server.py
│   ├── excel/            # Excel export functionality
│   │   └── exporter.py
│   ├── models/           # Pydantic data models
│   │   └── schemas.py
│   ├── main.py           # FastAPI application
│   ├── mcp_runner.py     # MCP server entry point
│   └── requirements.txt
├── frontend/             # Web UI
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── output/               # Generated Excel files
├── start_backend.bat     # Backend startup script
├── start_mcp.bat         # MCP server startup script
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Start the Backend

```bash
# Using the batch script:
start_backend.bat

# Or manually:
cd backend
python main.py
```

The API will be available at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### 3. Open the Frontend

Open `frontend/index.html` in your browser, or visit `http://localhost:8000`

### 4. Start MCP Server (Optional)

```bash
start_mcp.bat
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve frontend |
| `POST` | `/api/plan` | Create travel plan |
| `GET` | `/api/status` | Get system status |
| `GET` | `/api/plans` | List generated plans |
| `GET` | `/api/download/{filename}` | Download Excel file |

## MCP Tools

| Tool | Description |
|------|-------------|
| `create_travel_plan` | Create a complete travel plan |
| `get_plan_status` | Check system status |

## Excel Output

Generated Excel files include:
- **Overview** - Trip summary
- **Flights** - Flight options table
- **Hotels** - Hotel options table
- **Activities** - Activity options table
- **Budget** - Budget breakdown
- **Itinerary** - Day-by-day plan

## Design Patterns

- **Blackboard Pattern** - Shared memory for agent communication
- **Orchestrator Pattern** - Central coordinator for agent execution
- **MCP** - Standardized tool exposure for AI assistants
