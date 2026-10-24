def score_incident(incident: dict) -> dict:
    # Transparent heuristic, not a validated emergency triage model.
    severity = incident["urgency"] / 5 * 35
    affected = min(incident["estimated_affected"], 100) / 100 * 25
    evidence = incident["confidence"] * 20
    vulnerability = 10 if any(w in incident["text"].lower() for w in ("child", "elderly", "hospital", "school", "disabled")) else 0
    uncertainty_penalty = 8 if incident.get("conflict_flag") else 0
    duplicate_penalty = 12 if incident.get("duplicate_of") else 0
    score = round(max(0, min(100, severity + affected + evidence + vulnerability - uncertainty_penalty - duplicate_penalty)))
    priority = "CRITICAL" if score >= 75 else "HIGH" if score >= 55 else "MEDIUM" if score >= 35 else "LOW"
    reasons = [
        f"Urgency contributes {severity:.0f}/35 points",
        f"Estimated affected population contributes {affected:.0f}/25 points",
        f"Evidence confidence contributes {evidence:.0f}/20 points",
    ]
    if vulnerability:
        reasons.append("Potentially vulnerable people or critical facility mentioned (+10)")
    if incident.get("conflict_flag"):
        reasons.append("Conflicting incident claims reduce score (-8)")
    if incident.get("duplicate_of"):
        reasons.append("Likely duplicate report is down-weighted (-12)")
    if incident["confidence"] < 0.6:
        reasons.append("Low confidence: operator verification recommended")
    incident["risk_score"] = score
    incident["priority"] = priority
    incident["explanation"] = reasons
    return incident
