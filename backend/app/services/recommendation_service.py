import json
import re
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parents[2] / "dataset" / "tourism_data.json"

INTEREST_TO_FIELD = {
    "nature": "nature_score",
    "adventure": "adventure_score",
    "beach": "beach_score",
    "culture": "culture_score",
    "historical": "historical_score",
    "wildlife": "wildlife_score",
    "family": "family_score",
    "religious": "culture_score",
    "luxury": "rating",
}


def load_destinations():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _coerce_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _get_interest_match(destination, interests):
    if not interests:
        return 0.0
    score = 0.0
    for interest in interests:
        key = interest.lower().strip()
        field = INTEREST_TO_FIELD.get(key)
        if not field:
            continue
        score += float(destination.get(field, 0) or 0)
    return min(score / max(len(interests), 1), 1.0) * 100


def _get_budget_match(destination_cost, budget):
    if budget <= 0:
        return 50.0
    difference = abs(destination_cost - budget)
    ratio = difference / max(budget, 1)
    return max(0.0, 100.0 - (ratio * 100.0))


def _get_duration_match(recommended_days, trip_days):
    if trip_days <= 0:
        return 50.0
    difference = abs(recommended_days - trip_days)
    return max(0.0, 100.0 - (difference * 12.5))


def _get_rating_score(rating):
    return float(rating or 0) * 20


def _get_travel_type_score(destination, travel_type):
    if not travel_type:
        return 80.0
    travel_type = travel_type.lower()
    if travel_type in {"family", "friends"} and destination.get("family_score", 0):
        return float(destination.get("family_score", 0)) * 100
    if travel_type == "adventure" and destination.get("adventure_score", 0):
        return float(destination.get("adventure_score", 0)) * 100
    if travel_type == "beach" and destination.get("beach_score", 0):
        return float(destination.get("beach_score", 0)) * 100
    return 75.0


def _climate_match(destination_climate, user_climate):
    if not user_climate:
        return 1.0
    user_climate = user_climate.lower()
    destination_climate = str(destination_climate).lower()
    if user_climate in destination_climate:
        return 1.0
    if user_climate in {"summer", "winter", "monsoon", "spring"} and user_climate in destination_climate:
        return 1.0
    return 0.7


def recommend_destinations(payload):
    preferences = payload or {}
    budget = float(preferences.get("budget", 25000) or 25000)
    trip_days = int(preferences.get("days", preferences.get("duration", 4)) or 4)
    travelers = int(preferences.get("travelers", 2) or 2)
    travel_type = str(preferences.get("travel_type", "")).strip() or "general"
    interests = _coerce_list(preferences.get("interests", []))
    location = str(preferences.get("location", "")).strip().lower()
    climate = str(preferences.get("climate", "")).strip().lower()
    destinations = load_destinations()

    ranked = []
    for destination in destinations:
        destination_name = destination.get("destination_name", "Unknown")
        destination_country = str(destination.get("country", "")).lower()
        destination_state = str(destination.get("state", "")).lower()
        destination_cost = float(destination.get("average_cost", 0) or 0)
        rating_score = _get_rating_score(destination.get("rating", 0))
        budget_match = _get_budget_match(destination_cost, budget)
        duration_match = _get_duration_match(int(destination.get("recommended_days", 3) or 3), trip_days)
        interest_match = _get_interest_match(destination, interests)
        travel_type_score = _get_travel_type_score(destination, travel_type)
        climate_score = _climate_match(destination.get("best_season", ""), climate) * 100
        popularity_score = float(destination.get("popularity", 50) or 50)
        location_score = 100.0 if (not location or location in destination_country or location in destination_state) else 75.0

        total_score = (
            budget_match * 0.25
            + interest_match * 0.20
            + travel_type_score * 0.15
            + climate_score * 0.15
            + rating_score * 0.15
            + duration_match * 0.10
            + popularity_score * 0.05
            + location_score * 0.10
        ) / 1.0

        total_score = max(0.0, min(100.0, total_score))
        reasons = []
        if budget_match >= 70:
            reasons.append("Fits your budget")
        if interest_match >= 60:
            reasons.append("Matches your interests")
        if duration_match >= 70:
            reasons.append("Suitable for your trip duration")
        if rating_score >= 70:
            reasons.append("Strong traveler rating")
        if climate_score >= 70:
            reasons.append("Suitable climate for your preference")
        if not reasons:
            reasons.append("Good overall travel fit")

        ranked.append(
            {
                "destination_id": destination.get("destination_id"),
                "destination_name": destination_name,
                "state": destination.get("state"),
                "country": destination.get("country"),
                "estimated_cost": destination_cost * max(1, travelers),
                "recommended_days": destination.get("recommended_days", trip_days),
                "match_score": int(round(total_score)),
                "rating": destination.get("rating", 0),
                "best_season": destination.get("best_season"),
                "reasons": reasons,
                "category": destination.get("category"),
                "activities": destination.get("activities", []),
            }
        )

    ranked.sort(key=lambda item: item["match_score"], reverse=True)
    return ranked[:5]


def build_travel_plan(payload):
    destination_name = payload.get("destination_name") or payload.get("destination")
    days = int(payload.get("days") or 3)
    travelers = int(payload.get("travelers") or 2)
    travel_type = str(payload.get("travel_type") or "general")
    interests = _coerce_list(payload.get("interests", []))
    destination = next((item for item in load_destinations() if item["destination_name"].lower() == str(destination_name).lower()), None)
    if not destination:
        destination = load_destinations()[0]

    activities = destination.get("activities", [])
    base_day_plan = []
    for day in range(1, days + 1):
        morning_activity = activities[(day * 2) % max(len(activities), 1)] if activities else "Local sightseeing"
        afternoon_activity = activities[(day * 2 + 1) % max(len(activities), 1)] if activities else "Cultural walk"
        evening_activity = "Sunset viewpoint" if "nature" in " ".join(interests).lower() else "Local market experience"
        base_day_plan.append(
            {
                "day": day,
                "morning": morning_activity,
                "afternoon": afternoon_activity,
                "evening": evening_activity,
            }
        )

    return {
        "destination_name": destination.get("destination_name"),
        "days": days,
        "travelers": travelers,
        "travel_type": travel_type,
        "daily_plan": base_day_plan,
        "notes": [
            f"Recommended for {travel_type} travelers.",
            f"Budget-friendly itinerary for {travelers} traveler(s).",
            "Places selected to match the user interest profile and nearby attractions.",
        ],
    }


def estimate_budget(payload):
    destination_name = payload.get("destination_name") or payload.get("destination")
    days = int(payload.get("days") or 3)
    travelers = int(payload.get("travelers") or 2)
    destination = next((item for item in load_destinations() if item["destination_name"].lower() == str(destination_name).lower()), None)
    if not destination:
        destination = load_destinations()[0]

    base_cost = float(destination.get("average_cost", 2000) or 2000)
    transport = 1500 * travelers + (base_cost * 0.15)
    accommodation = base_cost * travelers * 0.4 * days / 2
    food = 500 * travelers * days
    activities = base_cost * travelers * 0.3
    local_transport = 250 * travelers * days
    miscellaneous = 350 * travelers * days
    total = transport + accommodation + food + activities + local_transport + miscellaneous

    return {
        "destination_name": destination.get("destination_name"),
        "minimum_cost": int(total * 0.85),
        "average_cost": int(total),
        "maximum_cost": int(total * 1.2),
        "breakdown": {
            "transportation": int(transport),
            "accommodation": int(accommodation),
            "food": int(food),
            "activities": int(activities),
            "local_transport": int(local_transport),
            "miscellaneous": int(miscellaneous),
        },
        "currency": "INR",
        "note": "Estimated trip cost based on demo data; live pricing requires external API integration.",
    }


def get_dashboard_data():
    destinations = load_destinations()
    total_destinations = len(destinations)
    total_attractions = sum(len(destination.get("attractions", [])) for destination in destinations)
    average_rating = sum(float(destination.get("rating", 0) or 0) for destination in destinations) / max(total_destinations, 1)
    average_cost = sum(float(destination.get("average_cost", 0) or 0) for destination in destinations) / max(total_destinations, 1)

    top_destinations = sorted(destinations, key=lambda item: float(item.get("popularity", 0) or 0), reverse=True)[:5]
    affordable_destinations = sorted(destinations, key=lambda item: float(item.get("average_cost", 0) or 0))[:5]
    expensive_destinations = sorted(destinations, key=lambda item: float(item.get("average_cost", 0) or 0), reverse=True)[:5]

    category_breakdown = {}
    for destination in destinations:
        key = destination.get("category", "General")
        category_breakdown[key] = category_breakdown.get(key, 0) + 1

    preferences = {"Nature": 0, "Adventure": 0, "Beach": 0, "Culture": 0, "Family": 0}
    for destination in destinations:
        preferences["Nature"] += int(float(destination.get("nature_score", 0) or 0) * 100)
        preferences["Adventure"] += int(float(destination.get("adventure_score", 0) or 0) * 100)
        preferences["Beach"] += int(float(destination.get("beach_score", 0) or 0) * 100)
        preferences["Culture"] += int(float(destination.get("culture_score", 0) or 0) * 100)
        preferences["Family"] += int(float(destination.get("family_score", 0) or 0) * 100)

    return {
        "total_destinations": total_destinations,
        "total_attractions": total_attractions,
        "average_rating": round(average_rating, 2),
        "average_cost": round(average_cost, 2),
        "popular_destinations": top_destinations,
        "affordable_destinations": affordable_destinations,
        "expensive_destinations": expensive_destinations,
        "category_breakdown": category_breakdown,
        "preference_distribution": preferences,
    }


def compare_destinations(destinations):
    selected = []
    for name in destinations:
        match = next((item for item in load_destinations() if item["destination_name"].lower() == str(name).lower()), None)
        if match:
            selected.append(match)

    rows = []
    for destination in selected:
        rows.append(
            {
                "destination_name": destination.get("destination_name"),
                "average_cost": destination.get("average_cost"),
                "rating": destination.get("rating"),
                "adventure_score": destination.get("adventure_score"),
                "nature_score": destination.get("nature_score"),
                "culture_score": destination.get("culture_score"),
                "beach_score": destination.get("beach_score"),
                "family_score": destination.get("family_score"),
            }
        )
    return rows


def rule_based_chat(message):
    text = (message or "").lower()
    budget = 30000
    days = 4
    travelers = 2
    interests = []
    location = "India"

    budget_match = re.search(r"rs\.?\s?(\d+(?:,\d+)*)|₹\s?(\d+(?:,\d+)*)|inr\s?(\d+(?:,\d+)*)", text, re.IGNORECASE)
    if budget_match:
        value = next(g for g in budget_match.groups() if g)
        value = value.replace(",", "")
        budget = float(value)

    day_match = re.search(r"(\d+)\s*(day|days)", text)
    if day_match:
        days = int(day_match.group(1))

    traveler_match = re.search(r"(\d+)\s*(person|people|traveler|travelers)", text)
    if traveler_match:
        travelers = int(traveler_match.group(1))

    if "nature" in text:
        interests.append("nature")
    if "adventure" in text:
        interests.append("adventure")
    if "beach" in text:
        interests.append("beach")
    if "culture" in text or "heritage" in text:
        interests.append("culture")
    if "history" in text:
        interests.append("historical")
    if "family" in text:
        interests.append("family")
    if "wildlife" in text:
        interests.append("wildlife")

    if "kerala" in text:
        location = "Kerala"

    result = recommend_destinations({
        "budget": budget,
        "days": days,
        "travelers": travelers,
        "interests": interests,
        "location": location,
        "travel_type": "general",
    })

    return {
        "summary": f"I found {len(result)} destination options for your trip budget and duration.",
        "recommendations": result[:3],
    }
