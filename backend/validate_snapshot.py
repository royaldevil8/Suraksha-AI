from collections import Counter
from app.services.orchestrator import build_snapshot

snapshot = build_snapshot()
items = snapshot["incidents"]

print("Priority distribution:", dict(Counter(i["priority"] for i in items)))
print("Evidence statuses:", dict(Counter(i["evidence_status"] for i in items)))
print("Assigned resource counts:", dict(Counter(
    resource
    for i in items
    for resource in i["assigned_resources"]
)))
print("Remaining resources:", snapshot["remaining_resources"])
print("Total incidents:", len(items))
print("Critical incidents:", sum(i["priority"] == "CRITICAL" for i in items))
print("Duplicate incidents:", sum(bool(i["duplicate_of"]) for i in items))
print("Conflict incidents:", sum(bool(i["conflict_flag"]) for i in items))
