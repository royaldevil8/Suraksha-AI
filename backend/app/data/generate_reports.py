import json, random
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / "reports.json"
random.seed(42)
locations = [
    ("Rampur", 28.80, 77.52), ("Shivpur", 28.64, 77.43),
    ("Old Town", 28.70, 77.49), ("Sector 4", 28.61, 77.38),
    ("Riverbank", 28.74, 77.55),
]
templates = [
    "Flood water rising fast near {loc}; {n} people trapped, urgent boat and rescue support needed.",
    "Smoke and fire reported near {loc}; {n} people injured, ambulance requested.",
    "Residents at {loc} report water entering homes; families need shelter and medical kits.",
    "Possible earthquake damage at {loc}; {n} people may be trapped under debris.",
    "Field volunteer at {loc} reports an injured person; medical help requested.",
    "Unconfirmed social post claims major collapse at {loc}; details not verified.",
    "Cyclone damage reported around {loc}; elderly residents need safe shelter.",
    "Road blocked near {loc}; rescue team needed to check possible trapped residents.",
]
def main():
    reports = []
    start = datetime.now(timezone.utc) - timedelta(hours=8)
    for i in range(1200):
        loc, lat, lon = random.choice(locations)
        template = random.choice(templates)
        text = template.format(loc=loc, n=random.choice([2, 4, 8, 12, 25, 40]))
        # Add deliberate duplicates and conflicts to test evidence handling.
        if i > 0 and i % 13 == 0:
            text = reports[i - 1]["text"]
            loc = reports[i - 1]["location_name"]
            lat, lon = reports[i - 1]["latitude"], reports[i - 1]["longitude"]
        elif i > 0 and i % 29 == 0:
            text = f"Conflicting report at {loc}: no flood observed, road is currently passable."
        reports.append({
            "report_id": f"R-{i+1:04d}", "incident_id": f"INC-{i+1:04d}",
            "text": text, "source": random.choice(["emergency_call", "field_worker", "social_post", "weather_feed"]),
            "timestamp": (start + timedelta(seconds=i * 20)).isoformat(),
            "location_name": loc, "latitude": lat, "longitude": lon,
            "confidence": round(random.uniform(0.35, 0.95), 2)
        })
    OUT.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(f"Generated {len(reports)} synthetic reports at {OUT}")
if __name__ == "__main__":
    main()
