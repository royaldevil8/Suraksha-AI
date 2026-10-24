import re
from datetime import datetime, timezone

LOCATIONS = {
    "rampur": (28.80, 77.52), "shivpur": (28.64, 77.43),
    "old town": (28.70, 77.49), "sector 4": (28.61, 77.38),
    "riverbank": (28.74, 77.55), "unknown": (28.65, 77.45),
}
KEYWORDS = {
    "flood": ("flood", ["boat", "rescue_team"]),
    "fire": ("fire", ["ambulance", "rescue_team"]),
    "injury": ("medical_emergency", ["ambulance", "medical_kit"]),
    "trapped": ("trapped_people", ["rescue_team", "boat"]),
    "shelter": ("displacement", ["shelter_space", "medical_kit"]),
    "earthquake": ("earthquake", ["rescue_team", "ambulance", "medical_kit"]),
    "cyclone": ("cyclone", ["rescue_team", "shelter_space"]),
}

def extract_report(report: dict) -> dict:
    text = str(report.get("text", "")).lower()
    incident_type, needed = "general_emergency", ["rescue_team"]
    for keyword, result in KEYWORDS.items():
        if keyword in text:
            incident_type, needed = result
            break
    urgency = 5 if any(x in text for x in ("critical", "trapped", "collapse", "many injured")) else 4 if any(x in text for x in ("urgent", "rising fast", "severe", "injured")) else 3 if any(x in text for x in ("water", "smoke", "damage")) else 2
    numbers = [int(n) for n in re.findall(r"\b(\d{1,4})\s*(?:people|person|families|injured|casualties)", text)]
    affected = max(numbers, default=(25 if urgency >= 4 else 8 if urgency == 3 else 2))
    location = str(report.get("location_name") or "unknown").lower()
    coords = LOCATIONS.get(location, LOCATIONS["unknown"])
    return {
        "incident_id": report.get("incident_id", report.get("report_id", "INC-UNKNOWN")),
        "report_id": report.get("report_id", "R-UNKNOWN"),
        "text": report.get("text", ""),
        "source": report.get("source", "unknown"),
        "timestamp": report.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "location_name": location.title(),
        "latitude": float(report.get("latitude", coords[0])),
        "longitude": float(report.get("longitude", coords[1])),
        "incident_type": incident_type,
        "urgency": urgency,
        "estimated_affected": affected,
        "resources_needed": needed,
        "confidence": float(report.get("confidence", 0.55)),
    }
