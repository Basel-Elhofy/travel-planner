"""Pydantic models for the Travel Planner multi-agent system."""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import date


class PlanStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    FLIGHTS = "flights"
    HOTELS = "hotels"
    ACTIVITIES = "activities"
    BUDGET = "budget"
    COMPLETED = "completed"
    FAILED = "failed"


class TravelRequest(BaseModel):
    """User input for travel planning."""
    location: str = Field(..., description="Destination city/country")
    start_date: date = Field(..., description="Trip start date")
    duration_days: int = Field(..., ge=1, le=30, description="Number of days")
    budget: float = Field(..., gt=0, description="Total budget in USD")
    travelers: int = Field(default=1, ge=1, le=10, description="Number of travelers")
    preferences: Optional[str] = Field(default=None, description="Optional preferences")


class FlightResult(BaseModel):
    """Flight search result."""
    airline: str
    flight_number: str
    departure: str
    arrival: str
    price: float
    duration: str
    stops: int


class HotelResult(BaseModel):
    """Hotel search result."""
    name: str
    address: str
    rating: float
    price_per_night: float
    amenities: list[str]


class ActivityResult(BaseModel):
    """Activity search result."""
    name: str
    category: str
    description: str
    price: float
    duration_hours: float
    rating: float


class BudgetResult(BaseModel):
    """Budget breakdown result."""
    flights_total: float
    hotels_total: float
    activities_total: float
    food_estimate: float
    transport_estimate: float
    misc_estimate: float
    total: float
    remaining: float
    currency: str = "USD"


class ItineraryItem(BaseModel):
    """Single item in a day's itinerary."""
    time: str
    activity: str
    location: str
    cost: float
    notes: Optional[str] = None


class DayPlan(BaseModel):
    """Plan for a single day."""
    day: int
    date: str
    items: list[ItineraryItem]


class TravelPlan(BaseModel):
    """Complete travel plan combining all agent results."""
    request: TravelRequest
    status: PlanStatus
    flights: list[FlightResult] = []
    hotels: list[HotelResult] = []
    activities: list[ActivityResult] = []
    budget: Optional[BudgetResult] = None
    itinerary: list[DayPlan] = []
    excel_path: Optional[str] = None
    error: Optional[str] = None
