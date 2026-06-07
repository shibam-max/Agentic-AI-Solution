import json
from datetime import datetime
from typing import Iterable

from app.schemas.models import LogEvent


def parse_jsonl_logs(raw_logs: str) -> list[LogEvent]:
    events: list[LogEvent] = []
    for line_number, line in enumerate(raw_logs.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue

        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on log line {line_number}") from exc

        if isinstance(payload.get("timestamp"), str):
            payload["timestamp"] = _parse_timestamp(payload["timestamp"])

        events.append(LogEvent.model_validate(payload))

    return sorted(events, key=lambda event: event.timestamp)


def logs_to_jsonl(events: Iterable[dict]) -> str:
    return "\n".join(json.dumps(event, sort_keys=True) for event in events)


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)
