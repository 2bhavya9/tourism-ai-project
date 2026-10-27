from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.app.services.recommendation_service import (
        build_travel_plan,
        compare_destinations,
        estimate_budget,
        get_dashboard_data,
        load_destinations,
        recommend_destinations,
        rule_based_chat,
    )
except ModuleNotFoundError:  # pragma: no cover
    from app.services.recommendation_service import (
        build_travel_plan,
        compare_destinations,
        estimate_budget,
        get_dashboard_data,
        load_destinations,
        recommend_destinations,
        rule_based_chat,
    )

app = FastAPI(
    title="Tourism AI Decision Support System",
    description="AI-based tourism analytics and travel planning backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Tourism AI API is running"}


@app.get("/api/destinations")
def get_destinations():
    return {"destinations": load_destinations()}


@app.get("/api/destinations/{destination_id}")
def get_destination(destination_id: str):
    for destination in load_destinations():
        if destination["destination_id"] == destination_id:
            return {"destination": destination}
    raise HTTPException(status_code=404, detail="Destination not found")


@app.post("/api/recommendations")
def api_recommendations(payload: dict):
    recommendations = recommend_destinations(payload)
    return {"recommendations": recommendations}


@app.post("/api/travel-plan")
def api_travel_plan(payload: dict):
    plan = build_travel_plan(payload)
    return {"travel_plan": plan}


@app.post("/api/budget/estimate")
def api_budget_estimate(payload: dict):
    cost = estimate_budget(payload)
    return {"budget_estimate": cost}


@app.get("/api/analytics/dashboard")
def api_dashboard():
    return {"dashboard": get_dashboard_data()}


@app.post("/api/destinations/compare")
def api_compare(payload: dict):
    destinations = payload.get("destinations", [])
    comparison_data = compare_destinations(destinations)
    return {"comparison": comparison_data}


@app.post("/api/chat")
def api_chat(payload: dict):
    message = payload.get("message") or payload.get("query") or ""
    return {"response": rule_based_chat(message)}


@app.post("/api/auth/register")
def register_user(payload: dict):
    return {
        "message": "User registered successfully",
        "user": {
            "email": payload.get("email"),
            "name": payload.get("name", "Traveler"),
        },
    }


@app.post("/api/auth/login")
def login_user(payload: dict):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    return {"message": "Login successful", "token": "demo-token", "user": {"email": email}}


@app.get("/")
def index():
    return {"project": "Tourism AI Decision Support System"}
