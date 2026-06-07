from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["debug", "info", "warning", "error", "critical"]


class LogEvent(BaseModel):
    timestamp: datetime
    service: str
    severity: Severity
    message: str
    trace_id: str | None = None
    latency_ms: int | None = None
    status_code: int | None = None


class IncidentSignal(BaseModel):
    service: str
    severity: Literal["medium", "high", "critical"]
    risk_score: float = Field(ge=0, le=1)
    reason: str
    evidence_count: int = Field(ge=1)
    first_seen: datetime
    last_seen: datetime
    related_events: list[LogEvent]


class TimelineEntry(BaseModel):
    timestamp: datetime
    service: str
    severity: Severity
    message: str
    latency_ms: int | None = None
    status_code: int | None = None


class RunbookMatch(BaseModel):
    title: str
    confidence: float = Field(ge=0, le=1)
    why_matched: str
    actions: list[str]


class IncidentReport(BaseModel):
    title: str
    severity: Literal["medium", "high", "critical"]
    confidence: float = Field(ge=0, le=1)
    risk_score: float = Field(ge=0, le=1)
    affected_services: list[str]
    blast_radius: str
    summary: str
    likely_root_cause: str
    timeline: list[TimelineEntry]
    runbook_matches: list[RunbookMatch]
    evidence: list[str]
    recommended_actions: list[str]
    generated_by: str = "deterministic-investigation-agent-v1"


class ReviewRequest(BaseModel):
    raw_logs: str


class ReviewResponse(BaseModel):
    event_count: int
    incident_count: int
    reports: list[IncidentReport]
