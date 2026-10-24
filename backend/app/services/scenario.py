from datetime import datetime, timezone
from uuid import uuid4
from app.services.orchestrator import build_snapshot

def replay_report(text: str, source: str, location_name: str) -> dict:
    report = {
        "report_id": f"REPLAY-{uuid4().hex[:8].upper()}",
        "incident_id": f"INC-REPLAY-{uuid4().hex[:6].upper()}",
        "text": text, "source": source, "location_name": location_name,
        "timestamp": datetime.now(timezone.utc).isoformat(), "confidence": 0.5,
    }
    snapshot = build_snapshot([report])
    return {"injected_report": report, **snapshot}
