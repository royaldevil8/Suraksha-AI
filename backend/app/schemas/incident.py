from pydantic import BaseModel, Field
from typing import Literal

class Incident(BaseModel):
    incident_id: str
    report_id: str
    text: str
    source: str
    timestamp: str
    location_name: str
    latitude: float
    longitude: float
    incident_type: str
    urgency: int = Field(ge=1, le=5)
    estimated_affected: int = Field(ge=0)
    resources_needed: list[str] = []
    confidence: float = Field(ge=0, le=1)
    risk_score: int = Field(ge=0, le=100)
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    duplicate_of: str | None = None
    conflict_flag: bool = False
    evidence_status: Literal["unverified", "corroborated", "conflicting"] = "unverified"
    explanation: list[str] = []
    assigned_resources: list[str] = []

class ReplayRequest(BaseModel):
    text: str = Field(min_length=5, max_length=2000)
    source: str = "scenario_replay"
    location_name: str = "Unknown location"
