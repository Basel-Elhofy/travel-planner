/**
 * Travel Planner - Frontend Application
 * Handles form submission, status polling, and results display.
 */

const API_BASE = "http://localhost:8000/api";

// DOM Elements
const form = document.getElementById("travelForm");
const submitBtn = document.getElementById("submitBtn");
const btnText = submitBtn.querySelector(".btn-text");
const btnLoading = submitBtn.querySelector(".btn-loading");
const statusSection = document.getElementById("statusSection");
const statusMessage = document.getElementById("statusMessage");
const resultsSection = document.getElementById("resultsSection");
const errorSection = document.getElementById("errorSection");
const errorMessage = document.getElementById("errorMessage");

// Status steps
const statusSteps = document.querySelectorAll(".status-step");

// Tab handling
const tabBtns = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        const tabId = btn.dataset.tab;
        tabBtns.forEach((b) => b.classList.remove("active"));
        tabContents.forEach((c) => c.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`${tabId}Tab`).classList.add("active");
    });
});

// Form submission
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = {
        location: document.getElementById("location").value,
        start_date: document.getElementById("start_date").value,
        duration_days: parseInt(document.getElementById("duration_days").value),
        budget: parseFloat(document.getElementById("budget").value),
        travelers: parseInt(document.getElementById("travelers").value),
        preferences: document.getElementById("preferences").value || null,
    };

    // Show loading state
    setLoading(true);
    showSection("status");
    resetStatusSteps();

    try {
        const response = await fetch(`${API_BASE}/plan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
        });

        const result = await response.json();

        if (result.success) {
            displayResults(result.plan, result.excel_path);
            showSection("results");
        } else {
            showError(result.detail || "Failed to create travel plan");
        }
    } catch (error) {
        showError("Failed to connect to the server. Make sure the backend is running on port 8000.");
    } finally {
        setLoading(false);
    }
});

function setLoading(loading) {
    submitBtn.disabled = loading;
    btnText.classList.toggle("hidden", loading);
    btnLoading.classList.toggle("hidden", !loading);
}

function showSection(section) {
    statusSection.classList.add("hidden");
    resultsSection.classList.add("hidden");
    errorSection.classList.add("hidden");

    if (section === "status") statusSection.classList.remove("hidden");
    if (section === "results") resultsSection.classList.remove("hidden");
    if (section === "error") errorSection.classList.remove("hidden");
}

function showError(message) {
    errorMessage.textContent = message;
    showSection("error");
}

function resetStatusSteps() {
    statusSteps.forEach((step) => {
        step.classList.remove("active", "completed");
    });
}

function updateStatusStep(stepName) {
    const step = document.querySelector(`.status-step[data-step="${stepName}"]`);
    if (step) {
        step.classList.add("active");
    }
}

function completeStatusStep(stepName) {
    const step = document.querySelector(`.status-step[data-step="${stepName}"]`);
    if (step) {
        step.classList.remove("active");
        step.classList.add("completed");
    }
}

function displayResults(plan, excelPath) {
    // Update summary
    document.getElementById("flightCount").textContent = plan.flights.length;
    document.getElementById("hotelCount").textContent = plan.hotels.length;
    document.getElementById("activityCount").textContent = plan.activities.length;
    document.getElementById("totalCost").textContent = `$${plan.budget.total.toLocaleString()}`;

    // Budget bar
    document.getElementById("budgetTotal").textContent = `$${plan.request.budget.toLocaleString()}`;
    document.getElementById("budgetRemaining").textContent = `$${plan.budget.remaining.toLocaleString()}`;
    const usedPercent = Math.min((plan.budget.total / plan.request.budget) * 100, 100);
    document.getElementById("budgetProgress").style.width = `${usedPercent}%`;

    // Download button
    const downloadBtn = document.getElementById("downloadBtn");
    if (excelPath) {
        // Extract just the filename (handles both / and \ path separators)
        const filename = excelPath.split(/[\\/]/).pop();
        downloadBtn.href = `${API_BASE}/download/${filename}`;
        downloadBtn.classList.remove("hidden");
    }

    // Flights table
    const flightsBody = document.getElementById("flightsTableBody");
    flightsBody.innerHTML = plan.flights
        .map(
            (f) => `
        <tr>
            <td>${f.airline}</td>
            <td>${f.flight_number}</td>
            <td>${f.departure}</td>
            <td>${f.arrival}</td>
            <td>${f.duration}</td>
            <td>${f.stops}</td>
            <td>$${f.price.toLocaleString()}</td>
        </tr>
    `
        )
        .join("");

    // Hotels table
    const hotelsBody = document.getElementById("hotelsTableBody");
    hotelsBody.innerHTML = plan.hotels
        .map(
            (h) => `
        <tr>
            <td>${h.name}</td>
            <td>${"★".repeat(Math.round(h.rating))} ${h.rating}</td>
            <td>$${h.price_per_night.toFixed(2)}</td>
            <td>${h.amenities.join(", ")}</td>
        </tr>
    `
        )
        .join("");

    // Activities table
    const activitiesBody = document.getElementById("activitiesTableBody");
    activitiesBody.innerHTML = plan.activities
        .map(
            (a) => `
        <tr>
            <td>${a.name}</td>
            <td>${a.category}</td>
            <td>${a.description}</td>
            <td>${a.duration_hours}h</td>
            <td>${"★".repeat(Math.round(a.rating))} ${a.rating}</td>
            <td>$${a.price.toFixed(2)}</td>
        </tr>
    `
        )
        .join("");

    // Itinerary
    const itineraryContainer = document.getElementById("itineraryContainer");
    itineraryContainer.innerHTML = plan.itinerary
        .map(
            (day) => `
        <div class="day-card">
            <div class="day-header">Day ${day.day} - ${day.date}</div>
            <div class="day-items">
                ${day.items
                    .map(
                        (item) => `
                    <div class="itinerary-item">
                        <span class="item-time">${item.time}</span>
                        <span class="item-activity">${item.activity}</span>
                        <span class="item-cost">$${item.cost.toFixed(0)}</span>
                    </div>
                `
                    )
                    .join("")}
            </div>
        </div>
    `
        )
        .join("");

    // Animate status steps
    animateStatusSteps();
}

function animateStatusSteps() {
    const steps = ["planning", "flights", "hotels", "activities", "budget", "completed"];
    let i = 0;
    const interval = setInterval(() => {
        if (i > 0) {
            completeStatusStep(steps[i - 1]);
        }
        if (i < steps.length) {
            updateStatusStep(steps[i]);
            i++;
        } else {
            clearInterval(interval);
        }
    }, 400);
}

function resetForm() {
    form.reset();
    showSection("status");
    statusSection.classList.add("hidden");
}

// Set minimum date to today
const dateInput = document.getElementById("start_date");
const today = new Date().toISOString().split("T")[0];
dateInput.min = today;
dateInput.value = today;
