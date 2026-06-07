from pathlib import Path

from app.core.pipeline import review_logs


def test_review_logs_detects_payment_incident() -> None:
    raw_logs = Path("data/sample_logs/payment_incident.jsonl").read_text(encoding="utf-8")

    response = review_logs(raw_logs)

    assert response.event_count == 5
    assert response.incident_count == 1
    report = response.reports[0]
    assert report.severity == "critical"
    assert report.risk_score > 0.8
    assert report.confidence > 0.8
    assert report.affected_services == ["payment-service"]
    assert "Database" in report.likely_root_cause
    assert report.timeline
    assert report.runbook_matches[0].title == "Database Saturation"


def test_review_logs_detects_auth_incident() -> None:
    raw_logs = Path("data/sample_logs/auth_incident.jsonl").read_text(encoding="utf-8")

    response = review_logs(raw_logs)

    assert response.incident_count == 1
    report = response.reports[0]
    assert report.affected_services == ["identity-service"]
    assert report.runbook_matches[0].title == "Authentication Failure"
    assert "Authentication" in report.likely_root_cause
