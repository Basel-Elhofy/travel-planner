"""
Blackboard Pattern Implementation
=================================
Shared memory space where all agents read/write their results.
The orchestrator coordinates agents, each agent reads from the
blackboard, processes data, and writes results back.
"""
import asyncio
from typing import Any, Optional
from models.schemas import TravelRequest, TravelPlan, PlanStatus


class Blackboard:
    """
    Central shared memory for multi-agent communication.
    Agents publish results here; the orchestrator reads them.
    """

    def __init__(self):
        self._data: dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._subscribers: list[asyncio.Queue] = []

    async def write(self, key: str, value: Any) -> None:
        """Write data to the blackboard."""
        async with self._lock:
            self._data[key] = value
        await self._notify(key, value)

    async def read(self, key: str) -> Optional[Any]:
        """Read data from the blackboard."""
        async with self._lock:
            return self._data.get(key)

    async def read_all(self) -> dict[str, Any]:
        """Read all data from the blackboard."""
        async with self._lock:
            return dict(self._data)

    async def clear(self) -> None:
        """Clear the blackboard."""
        async with self._lock:
            self._data.clear()

    async def subscribe(self) -> asyncio.Queue:
        """Subscribe to blackboard updates."""
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    async def _notify(self, key: str, value: Any) -> None:
        """Notify all subscribers of an update."""
        dead = []
        for q in self._subscribers:
            try:
                q.put_nowait((key, value))
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self._subscribers.remove(q)

    # --- Convenience methods for the travel planner ---

    async def set_request(self, request: TravelRequest) -> None:
        await self.write("request", request)

    async def get_request(self) -> Optional[TravelRequest]:
        return await self.read("request")

    async def set_status(self, status: PlanStatus) -> None:
        await self.write("status", status)

    async def get_status(self) -> Optional[PlanStatus]:
        return await self.read("status")

    async def set_flights(self, flights: list) -> None:
        await self.write("flights", flights)

    async def get_flights(self) -> list:
        return await self.read("flights") or []

    async def set_hotels(self, hotels: list) -> None:
        await self.write("hotels", hotels)

    async def get_hotels(self) -> list:
        return await self.read("hotels") or []

    async def set_activities(self, activities: list) -> None:
        await self.write("activities", activities)

    async def get_activities(self) -> list:
        return await self.read("activities") or []

    async def set_budget(self, budget) -> None:
        await self.write("budget", budget)

    async def get_budget(self):
        return await self.read("budget")

    async def set_itinerary(self, itinerary: list) -> None:
        await self.write("itinerary", itinerary)

    async def get_itinerary(self) -> list:
        return await self.read("itinerary") or []

    async def set_excel_path(self, path: str) -> None:
        await self.write("excel_path", path)

    async def get_excel_path(self) -> Optional[str]:
        return await self.read("excel_path")

    async def set_error(self, error: str) -> None:
        await self.write("error", error)

    async def get_error(self) -> Optional[str]:
        return await self.read("error")

    async def build_plan(self) -> TravelPlan:
        """Build a complete TravelPlan from blackboard data."""
        request = await self.get_request()
        if not request:
            raise ValueError("No request found on blackboard")

        return TravelPlan(
            request=request,
            status=await self.get_status() or PlanStatus.PENDING,
            flights=await self.get_flights(),
            hotels=await self.get_hotels(),
            activities=await self.get_activities(),
            budget=await self.get_budget(),
            itinerary=await self.get_itinerary(),
            excel_path=await self.get_excel_path(),
            error=await self.get_error(),
        )
