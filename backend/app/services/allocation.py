from app.core.config import RESOURCE_INVENTORY

def allocate_resources(incidents: list[dict]) -> tuple[list[dict], list[dict]]:
    stock = {x["type"]: x["count"] for x in RESOURCE_INVENTORY}
    for item in incidents:
        item["assigned_resources"] = []
    # Deterministic greedy baseline: high risk first; no claim of global optimality.
    for incident in sorted(incidents, key=lambda x: (x["risk_score"], x["urgency"]), reverse=True):
        if incident.get("duplicate_of"):
            continue
        for resource_type in incident.get("resources_needed", []):
            if stock.get(resource_type, 0) > 0:
                stock[resource_type] -= 1
                incident["assigned_resources"].append(resource_type)
    remaining = [{"type": k, "available": v} for k, v in stock.items()]
    return incidents, remaining
