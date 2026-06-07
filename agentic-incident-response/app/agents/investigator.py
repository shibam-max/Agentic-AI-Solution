from app.agents.runbooks import match_runbooks
from app.schemas.models import IncidentReport, IncidentSignal, TimelineEntry


def investigate_signal(signal: IncidentSignal) -> IncidentReport:
    runbooks = match_runbooks(signal)
    evidence = [
        f"{event.timestamp.isoformat()} {event.service} {event.severity.upper()}: {event.message}"
        for event in signal.related_events[:5]
    ]
    runbook_actions = [action for runbook in runbooks[:2] for action in runbook.actions[:2]]

    return IncidentReport(
        title=f"{signal.service} incident: {signal.severity} reliability signal",
        severity=signal.severity,
        confidence=_score_confidence(signal),
        risk_score=signal.risk_score,
        affected_services=[signal.service],
        blast_radius=_estimate_blast_radius(signal),
        summary=(
            f"{signal.service} produced {signal.evidence_count} suspicious log events between "
            f"{signal.first_seen.isoformat()} and {signal.last_seen.isoformat()}. {signal.reason}"
        ),
        likely_root_cause=_infer_root_cause(signal),
        timeline=_build_timeline(signal),
        runbook_matches=runbooks,
        evidence=evidence,
        recommended_actions=_dedupe(_recommend_actions(signal) + runbook_actions),
    )


def _build_timeline(signal: IncidentSignal) -> list[TimelineEntry]:
    return [
        TimelineEntry(
            timestamp=event.timestamp,
            service=event.service,
            severity=event.severity,
            message=event.message,
            latency_ms=event.latency_ms,
            status_code=event.status_code,
        )
        for event in signal.related_events
    ]


def _infer_root_cause(signal: IncidentSignal) -> str:
    messages = " ".join(event.message.lower() for event in signal.related_events)
    statuses = {event.status_code for event in signal.related_events}

    if "database" in messages or "connection pool" in messages or "timeout" in messages:
        return "Database connectivity or resource saturation is the leading hypothesis."
    if "unauthorized" in messages or "permission denied" in messages or 401 in statuses or 403 in statuses:
        return "Authentication or authorization failure is the leading hypothesis."
    if 500 in statuses or 503 in statuses:
        return "Service-side failure or downstream dependency outage is the leading hypothesis."
    if "latency" in messages or any(event.latency_ms and event.latency_ms > 2000 for event in signal.related_events):
        return "Latency regression or overloaded dependency is the leading hypothesis."
    return "Multiple correlated errors were detected; inspect recent deploys and downstream dependencies first."


def _score_confidence(signal: IncidentSignal) -> float:
    score = 0.45 + min(signal.evidence_count, 5) * 0.08 + signal.risk_score * 0.25
    if any(event.severity == "critical" for event in signal.related_events):
        score += 0.08
    return min(round(score, 2), 0.99)


def _estimate_blast_radius(signal: IncidentSignal) -> str:
    statuses = {event.status_code for event in signal.related_events}
    if signal.severity == "critical" and (500 in statuses or 503 in statuses):
        return "Likely customer-facing impact for requests routed through this service."
    if signal.severity == "high":
        return "Elevated risk of partial user impact; confirm with traffic and trace metrics."
    return "Localized service degradation unless correlated signals appear in dependent services."


def _recommend_actions(signal: IncidentSignal) -> list[str]:
    actions = [
        f"Check recent deploys and configuration changes for {signal.service}.",
        "Inspect traces for the most frequent failing request path.",
        "Confirm whether error volume is still increasing before paging additional owners.",
    ]

    root_cause = _infer_root_cause(signal).lower()
    if "database" in root_cause:
        actions.insert(1, "Review database connection pool saturation, slow queries, and timeout settings.")
    if "authentication" in root_cause:
        actions.insert(1, "Validate auth provider health, token expiry behavior, and permission policy changes.")
    if "downstream" in root_cause:
        actions.insert(1, "Check downstream service health and retry/circuit-breaker behavior.")

    return actions


def _dedupe(actions: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for action in actions:
        if action in seen:
            continue
        seen.add(action)
        deduped.append(action)
    return deduped
