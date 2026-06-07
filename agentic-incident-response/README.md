# Agentic Incident Response

Portfolio-grade AI incident response platform.

The system ingests application logs, detects suspicious error patterns, groups them into incidents, and produces a structured investigation summary. The first milestone is intentionally deterministic so the pipeline can be tested before LangGraph, PyTorch, RAG, and LLM providers are added.

## Features

- JSONL log ingestion
- suspicious event grouping by service
- severity and risk scoring
- timeline reconstruction
- deterministic root-cause hypothesis
- runbook matching
- recommended remediation steps
- FastAPI endpoint
- CLI demo command
- sample incident datasets

## Roadmap

1. MVP log ingestion and anomaly detection
2. Deterministic incident investigation agent
3. FastAPI review endpoint
4. PyTorch anomaly model
5. LangGraph multi-agent investigation workflow
6. RAG over runbooks and service docs
7. Dashboard, evals, and Docker deployment

## Architecture

```text
Log File / API Upload
        |
        v
Log Parser
        |
        v
Statistical Detector
        |
        v
Incident Grouper
        |
        v
Investigation Agent
        |
        v
Incident Report API
```

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
uvicorn app.api.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Docker

```powershell
docker compose up --build
```

API examples are available in `API_EXAMPLES.md`.

## CLI Demo

```powershell
python -m app.cli data\sample_logs\payment_incident.jsonl --pretty
```

Try the auth incident too:

```powershell
python -m app.cli data\sample_logs\auth_incident.jsonl --pretty
```

## Run Tests

```powershell
pytest
```
