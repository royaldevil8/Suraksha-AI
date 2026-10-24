import json
from threading import Lock

from app.core.config import REPORTS_FILE
from app.services.extraction import extract_report
from app.services.deduplication import annotate_duplicates
from app.services.risk_scoring import score_incident
from app.services.allocation import allocate_resources

_snapshot_cache: dict | None = None
_snapshot_lock = Lock()


def load_reports() -> list[dict]:
    if not REPORTS_FILE.exists():
        return []
    return json.loads(REPORTS_FILE.read_text(encoding="utf-8"))


def invalidate_snapshot_cache() -> None:
    global _snapshot_cache
    with _snapshot_lock:
        _snapshot_cache = None


def _compute_snapshot(extra_reports: list[dict] | None = None) -> dict:
    raw = load_reports()
    if extra_reports:
        raw.extend(extra_reports)

    incidents = [extract_report(r) for r in raw]
    incidents = annotate_duplicates(incidents)
    incidents = [score_incident(i) for i in incidents]
    incidents, remaining = allocate_resources(incidents)
    incidents.sort(key=lambda x: x["risk_score"], reverse=True)

    return {
        "incidents": incidents,
        "remaining_resources": remaining,
        "report_count": len(raw),
    }


def build_snapshot(extra_reports: list[dict] | None = None) -> dict:
    global _snapshot_cache

    # Replay requests must include their new report and must not
    # overwrite the regular dashboard snapshot cache.
    if extra_reports:
        return _compute_snapshot(extra_reports)

    with _snapshot_lock:
        if _snapshot_cache is None:
            _snapshot_cache = _compute_snapshot()

        # Return a copy so callers cannot mutate the shared cache.
        return {
            "incidents": [dict(i) for i in _snapshot_cache["incidents"]],
            "remaining_resources": [dict(item) for item in _snapshot_cache["remaining_resources"]],
            "report_count": _snapshot_cache["report_count"],
        }

