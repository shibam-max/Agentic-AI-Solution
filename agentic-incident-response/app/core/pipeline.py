from app.agents.investigator import investigate_signal
from app.detection.statistical import detect_incident_signals
from app.ingestion.log_parser import parse_jsonl_logs
from app.schemas.models import ReviewResponse


def review_logs(raw_logs: str) -> ReviewResponse:
    events = parse_jsonl_logs(raw_logs)
    signals = detect_incident_signals(events)
    reports = [investigate_signal(signal) for signal in signals]
    return ReviewResponse(event_count=len(events), incident_count=len(reports), reports=reports)
