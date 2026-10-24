import json
from app.core.config import REPORTS_FILE
from app.services.extraction import extract_report
from app.services.deduplication import annotate_duplicates
from app.services.risk_scoring import score_incident
from app.services.allocation import allocate_resources

def load_reports() -> list[dict]:
    if not REPORTS_FILE.exists():
        return []
    return json.loads(REPORTS_FILE.read_text(encoding="utf-8"))

def build_snapshot(extra_reports: list[dict] | None = None) -> dict:
    raw = load_reports()
    if extra_reports:
        raw.extend(extra_reports)
    incidents = [extract_report(r) for r in raw]
    incidents = annotate_duplicates(incidents)
    incidents = [score_incident(i) for i in incidents]
    incidents, remaining = allocate_resources(incidents)
    incidents.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"incidents": incidents, "remaining_resources": remaining, "report_count": len(raw)}
