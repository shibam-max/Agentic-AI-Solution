from dataclasses import dataclass
import re

from app.schemas.models import IncidentSignal, RunbookMatch


@dataclass(frozen=True)
class Runbook:
    title: str
    keywords: tuple[str, ...]
    actions: tuple[str, ...]


RUNBOOKS = (
    Runbook(
        title="Database Saturation",
        keywords=("database", "connection pool", "timeout", "slow query"),
        actions=(
            "Check database CPU, connection pool usage, lock waits, and slow query logs.",
            "Reduce retry amplification and verify circuit breakers before scaling traffic.",
            "Roll back recent schema, index, or connection-pool changes if correlated.",
        ),
    ),
    Runbook(
        title="Authentication Failure",
        keywords=("unauthorized", "permission denied", "token", "auth", "401", "403"),
        actions=(
            "Validate auth provider health and token signing key rotation status.",
            "Compare permission policy changes against the first failing timestamp.",
            "Sample failed requests to confirm whether failures are user-specific or global.",
        ),
    ),
    Runbook(
        title="Downstream Service Outage",
        keywords=("503", "dependency", "downstream", "retry", "unavailable"),
        actions=(
            "Check downstream service health, deploy timeline, and saturation metrics.",
            "Confirm retry policy, timeout budget, and circuit-breaker activation.",
            "Prepare degraded-mode messaging if user-facing impact is confirmed.",
        ),
    ),
    Runbook(
        title="Latency Regression",
        keywords=("latency", "slow", "timeout", "p95", "p99"),
        actions=(
            "Compare p95/p99 latency before and after the suspected regression window.",
            "Inspect trace spans for the slowest dependency and endpoint path.",
            "Disable recent expensive feature flags if correlated with the spike.",
        ),
    ),
)


def match_runbooks(signal: IncidentSignal) -> list[RunbookMatch]:
    haystack = _signal_text(signal)
    matches: list[RunbookMatch] = []
    for runbook in RUNBOOKS:
        matched_keywords = [keyword for keyword in runbook.keywords if _keyword_matches(keyword, haystack)]
        if not matched_keywords:
            continue

        confidence = min(0.45 + len(matched_keywords) * 0.15 + signal.risk_score * 0.2, 0.98)
        matches.append(
            RunbookMatch(
                title=runbook.title,
                confidence=round(confidence, 2),
                why_matched=f"Matched keywords: {', '.join(matched_keywords)}.",
                actions=list(runbook.actions),
            )
        )

    return sorted(matches, key=lambda match: match.confidence, reverse=True)


def _signal_text(signal: IncidentSignal) -> str:
    messages = " ".join(event.message.lower() for event in signal.related_events)
    statuses = " ".join(str(event.status_code) for event in signal.related_events if event.status_code)
    return f"{signal.reason.lower()} {messages} {statuses}"


def _keyword_matches(keyword: str, haystack: str) -> bool:
    if keyword.isdigit():
        return keyword in haystack.split()
    pattern = rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])"
    return re.search(pattern, haystack) is not None
