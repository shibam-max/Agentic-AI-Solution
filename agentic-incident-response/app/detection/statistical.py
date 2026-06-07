from collections import defaultdict

from app.schemas.models import IncidentSignal, LogEvent


ERROR_SEVERITIES = {"error", "critical"}
SECURITY_KEYWORDS = {
    "unauthorized",
    "permission denied",
    "token",
    "secret",
    "sql injection",
    "auth",
}


def detect_incident_signals(events: list[LogEvent]) -> list[IncidentSignal]:
    grouped: dict[str, list[LogEvent]] = defaultdict(list)
    for event in events:
        if _is_suspicious(event):
            grouped[event.service].append(event)

    signals: list[IncidentSignal] = []
    for service, related_events in grouped.items():
        if len(related_events) < 2 and not any(event.severity == "critical" for event in related_events):
            continue

        severity = _score_severity(related_events)
        risk_score = _score_risk(related_events)
        signals.append(
            IncidentSignal(
                service=service,
                severity=severity,
                risk_score=risk_score,
                reason=_build_reason(related_events),
                evidence_count=len(related_events),
                first_seen=related_events[0].timestamp,
                last_seen=related_events[-1].timestamp,
                related_events=related_events,
            )
        )

    return sorted(signals, key=lambda signal: (signal.severity, signal.evidence_count), reverse=True)


def _contains_security_keyword(event: LogEvent) -> bool:
    message = event.message.lower()
    return any(keyword in message for keyword in SECURITY_KEYWORDS)


def _is_suspicious(event: LogEvent) -> bool:
    if event.severity in ERROR_SEVERITIES:
        return True
    if event.severity in {"warning", "error", "critical"} and _contains_security_keyword(event):
        return True
    return bool(event.status_code and event.status_code >= 400 and _contains_security_keyword(event))


def _score_severity(events: list[LogEvent]) -> str:
    critical_count = sum(1 for event in events if event.severity == "critical")
    error_count = sum(1 for event in events if event.severity == "error")
    security_count = sum(1 for event in events if _contains_security_keyword(event))
    high_latency_count = sum(1 for event in events if event.latency_ms and event.latency_ms > 2000)

    if critical_count or security_count >= 2:
        return "critical"
    if error_count >= 3 or high_latency_count >= 2:
        return "high"
    return "medium"


def _score_risk(events: list[LogEvent]) -> float:
    error_count = sum(1 for event in events if event.severity == "error")
    critical_count = sum(1 for event in events if event.severity == "critical")
    security_count = sum(1 for event in events if _contains_security_keyword(event))
    high_latency_count = sum(1 for event in events if event.latency_ms and event.latency_ms > 2000)
    server_error_count = sum(1 for event in events if event.status_code and event.status_code >= 500)

    raw_score = (
        0.15
        + error_count * 0.12
        + critical_count * 0.25
        + security_count * 0.18
        + high_latency_count * 0.08
        + server_error_count * 0.07
    )
    return min(round(raw_score, 2), 1.0)


def _build_reason(events: list[LogEvent]) -> str:
    severities = sorted({event.severity for event in events})
    statuses = sorted({event.status_code for event in events if event.status_code})
    status_text = f" with status codes {statuses}" if statuses else ""
    return f"{len(events)} suspicious events observed across severities {severities}{status_text}."
