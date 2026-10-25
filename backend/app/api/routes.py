
from fastapi import APIRouter

from app.core.config import RESOURCE_INVENTORY
from app.schemas.incident import ReplayRequest
from app.services.orchestrator import build_snapshot
from app.services.scenario import replay_report

router = APIRouter()


def build_summary(snapshot: dict) -> dict:
    """Calculate dashboard metrics from one consistent snapshot."""
    items = snapshot["incidents"]

    return {
        "report_count": snapshot["report_count"],
        "incident_count": len(items),
        "critical_count": sum(
            i["priority"] == "CRITICAL" for i in items
        ),
        "high_count": sum(
            i["priority"] == "HIGH" for i in items
        ),
        "duplicate_count": sum(
            bool(i.get("duplicate_of")) for i in items
        ),
        "conflict_count": sum(
            bool(i.get("conflict_flag")) for i in items
        ),
        "unverified_count": sum(
            i.get("evidence_status", "unverified") == "unverified"
            for i in items
        ),
        "low_confidence_count": sum(
            i.get("confidence", 0.0) < 0.6 for i in items
        ),
    }


@router.get("/health")
def health():
    return {"status": "ok", "service": "suraksha-ai"}


@router.get("/summary")
def summary():
    return build_summary(build_snapshot())


@router.get("/incidents")
def incidents():
    return build_snapshot()["incidents"]


@router.get("/resources")
def resources():
    snapshot = build_snapshot()

    return {
        "inventory": RESOURCE_INVENTORY,
        "remaining": snapshot["remaining_resources"],
    }


@router.post("/scenario/replay")
def scenario_replay(payload: ReplayRequest):
    snapshot = replay_report(
        payload.text,
        payload.source,
        payload.location_name,
    )

    return {
        **snapshot,
        "summary": build_summary(snapshot),
    }
