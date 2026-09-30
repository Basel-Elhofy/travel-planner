"""
Excel Exporter
==============
Exports the complete travel plan to a formatted Excel file.
Creates multiple sheets: Overview, Flights, Hotels, Activities, Budget, Itinerary.
"""
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from models.schemas import TravelPlan


class ExcelExporter:
    """Exports travel plan data to a formatted Excel workbook."""

    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "output")

    # Style constants
    HEADER_FONT = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
    HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
    TITLE_FONT = Font(name="Calibri", bold=True, size=16, color="2F5496")
    SUBTITLE_FONT = Font(name="Calibri", bold=True, size=12, color="2F5496")
    NORMAL_FONT = Font(name="Calibri", size=11)
    BORDER = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    def export(self, plan: TravelPlan) -> str:
        """
        Export the travel plan to an Excel file.
        
        Returns:
            Path to the generated Excel file.
        """
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{plan.request.location.replace(' ', '_')}_{timestamp}.xlsx"
        filepath = os.path.join(self.OUTPUT_DIR, filename)

        wb = Workbook()

        # Create sheets
        self._create_overview_sheet(wb, plan)
        self._create_flights_sheet(wb, plan)
        self._create_hotels_sheet(wb, plan)
        self._create_activities_sheet(wb, plan)
        self._create_budget_sheet(wb, plan)
        self._create_itinerary_sheet(wb, plan)

        # Remove default sheet
        if "Sheet" in wb.sheetnames:
            del wb["Sheet"]

        wb.save(filepath)
        return filepath

    def _create_overview_sheet(self, wb: Workbook, plan: TravelPlan) -> None:
        """Create the Overview sheet with trip summary."""
        ws = wb.create_sheet("Overview")

        # Title
        ws["A1"] = "TRAVEL PLAN"
        ws["A1"].font = self.TITLE_FONT
        ws.merge_cells("A1:D1")

        # Trip details
        row = 3
        details = [
            ("Destination:", plan.request.location),
            ("Start Date:", str(plan.request.start_date)),
            ("Duration:", f"{plan.request.duration_days} days"),
            ("Travelers:", str(plan.request.travelers)),
            ("Budget:", f"${plan.request.budget:,.2f}"),
            ("Status:", plan.status.value),
            ("Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]

        for label, value in details:
            ws.cell(row=row, column=1, value=label).font = self.SUBTITLE_FONT
            ws.cell(row=row, column=2, value=value).font = self.NORMAL_FONT
            row += 1

        # Summary
        row += 1
        ws.cell(row=row, column=1, value="SUMMARY").font = self.SUBTITLE_FONT
        row += 1
        summary_items = [
            ("Flights Found:", len(plan.flights)),
            ("Hotels Found:", len(plan.hotels)),
            ("Activities Found:", len(plan.activities)),
            ("Total Cost:", f"${plan.budget.total:,.2f}" if plan.budget else "N/A"),
            ("Remaining Budget:", f"${plan.budget.remaining:,.2f}" if plan.budget else "N/A"),
        ]
        for label, value in summary_items:
            ws.cell(row=row, column=1, value=label).font = self.NORMAL_FONT
            ws.cell(row=row, column=2, value=value).font = self.NORMAL_FONT
            row += 1

        # Adjust column widths
        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 30

    def _create_flights_sheet(self, wb: Workbook, plan: TravelPlan) -> None:
        """Create the Flights sheet."""
        ws = wb.create_sheet("Flights")

        headers = ["Airline", "Flight Number", "Departure", "Arrival", "Price ($)", "Duration", "Stops"]
        self._write_header_row(ws, headers)

        for i, flight in enumerate(plan.flights, start=2):
            ws.cell(row=i, column=1, value=flight.airline)
            ws.cell(row=i, column=2, value=flight.flight_number)
            ws.cell(row=i, column=3, value=flight.departure)
            ws.cell(row=i, column=4, value=flight.arrival)
            ws.cell(row=i, column=5, value=flight.price)
            ws.cell(row=i, column=6, value=flight.duration)
            ws.cell(row=i, column=7, value=flight.stops)

        self._adjust_columns(ws, headers)

    def _create_hotels_sheet(self, wb: Workbook, plan: TravelPlan) -> None:
        """Create the Hotels sheet."""
        ws = wb.create_sheet("Hotels")

        headers = ["Name", "Address", "Rating", "Price/Night ($)", "Amenities"]
        self._write_header_row(ws, headers)

        for i, hotel in enumerate(plan.hotels, start=2):
            ws.cell(row=i, column=1, value=hotel.name)
            ws.cell(row=i, column=2, value=hotel.address)
            ws.cell(row=i, column=3, value=hotel.rating)
            ws.cell(row=i, column=4, value=hotel.price_per_night)
            ws.cell(row=i, column=5, value=", ".join(hotel.amenities))

        self._adjust_columns(ws, headers)

    def _create_activities_sheet(self, wb: Workbook, plan: TravelPlan) -> None:
        """Create the Activities sheet."""
        ws = wb.create_sheet("Activities")

        headers = ["Name", "Category", "Description", "Price ($)", "Duration (hrs)", "Rating"]
        self._write_header_row(ws, headers)

        for i, activity in enumerate(plan.activities, start=2):
            ws.cell(row=i, column=1, value=activity.name)
            ws.cell(row=i, column=2, value=activity.category)
            ws.cell(row=i, column=3, value=activity.description)
            ws.cell(row=i, column=4, value=activity.price)
            ws.cell(row=i, column=5, value=activity.duration_hours)
            ws.cell(row=i, column=6, value=activity.rating)

        self._adjust_columns(ws, headers)

    def _create_budget_sheet(self, wb: Workbook, plan: TravelPlan) -> None:
        """Create the Budget sheet."""
        ws = wb.create_sheet("Budget")

        if plan.budget:
            headers = ["Category", "Amount ($)"]
            self._write_header_row(ws, headers)

            budget_items = [
                ("Flights", plan.budget.flights_total),
                ("Hotels", plan.budget.hotels_total),
                ("Activities", plan.budget.activities_total),
                ("Food (est.)", plan.budget.food_estimate),
                ("Transport (est.)", plan.budget.transport_estimate),
                ("Miscellaneous (est.)", plan.budget.misc_estimate),
                ("", ""),
                ("TOTAL", plan.budget.total),
                ("BUDGET", plan.request.budget),
                ("REMAINING", plan.budget.remaining),
            ]

            for i, (category, amount) in enumerate(budget_items, start=2):
                ws.cell(row=i, column=1, value=category).font = self.NORMAL_FONT
                ws.cell(row=i, column=2, value=amount).font = self.NORMAL_FONT
                if category in ("TOTAL", "BUDGET", "REMAINING"):
                    ws.cell(row=i, column=1).font = self.SUBTITLE_FONT
                    ws.cell(row=i, column=2).font = self.SUBTITLE_FONT

        self._adjust_columns(ws, ["Category", "Amount ($)"])

    def _create_itinerary_sheet(self, wb: Workbook, plan: TravelPlan) -> None:
        """Create the Itinerary sheet with day-by-day plan."""
        ws = wb.create_sheet("Itinerary")

        headers = ["Day", "Date", "Time", "Activity", "Location", "Cost ($)", "Notes"]
        self._write_header_row(ws, headers)

        row = 2
        for day in plan.itinerary:
            for item in day.items:
                ws.cell(row=row, column=1, value=day.day)
                ws.cell(row=row, column=2, value=day.date)
                ws.cell(row=row, column=3, value=item.time)
                ws.cell(row=row, column=4, value=item.activity)
                ws.cell(row=row, column=5, value=item.location)
                ws.cell(row=row, column=6, value=item.cost)
                ws.cell(row=row, column=7, value=item.notes or "")
                row += 1

        self._adjust_columns(ws, headers)

    def _write_header_row(self, ws, headers: list[str]) -> None:
        """Write a styled header row."""
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=1, value=header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal="center")
            cell.border = self.BORDER

    def _adjust_columns(self, ws, headers: list[str]) -> None:
        """Auto-adjust column widths based on content."""
        for col, header in enumerate(headers, start=1):
            max_length = len(header)
            for row in ws.iter_rows(min_col=col, max_col=col, min_row=2, max_row=ws.max_row):
                for cell in row:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[get_column_letter(col)].width = min(max_length + 2, 50)
