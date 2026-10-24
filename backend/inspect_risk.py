from app.services.orchestrator import build_snapshot

items = build_snapshot()["incidents"]

print("TOP 10 INCIDENTS")
for i in items[:10]:
    print({
        "id": i["incident_id"],
        "type": i["incident_type"],
        "urgency": i["urgency"],
        "affected": i["estimated_affected"],
        "confidence": i["confidence"],
        "duplicate": bool(i["duplicate_of"]),
        "score": i["risk_score"],
        "priority": i["priority"],
        "text": i["text"][:100],
    })

print("\nNON-DUPLICATE PRIORITIES")
primary = [i for i in items if not i["duplicate_of"]]
for priority in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
    print(priority, sum(i["priority"] == priority for i in primary))

print("\nNON-DUPLICATE MAX SCORE")
print(max((i["risk_score"] for i in primary), default=0))
