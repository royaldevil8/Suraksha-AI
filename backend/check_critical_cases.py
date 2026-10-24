from collections import Counter
from app.services.orchestrator import build_snapshot

items = build_snapshot()["incidents"]

print("Urgency 5:", sum(i["urgency"] == 5 for i in items))
print("Urgency 5, non-duplicate:", sum(
    i["urgency"] == 5 and not i["duplicate_of"] for i in items
))
print("Urgency 5, confidence >= 0.8:", sum(
    i["urgency"] == 5 and i["confidence"] >= 0.8 and not i["duplicate_of"]
    for i in items
))
print("Uncertainty language in top 20:")
for i in items[:20]:
    print(i["incident_id"], i["risk_score"], i["priority"], i["text"][:90])
