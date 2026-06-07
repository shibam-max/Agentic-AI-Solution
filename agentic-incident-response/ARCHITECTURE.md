# Architecture

## Current MVP

```text
JSONL logs
   |
   v
Log parser
   |
   v
Statistical signal detector
   |
   v
Runbook matcher + investigation agent
   |
   v
Incident report API / CLI
```

## Why This Is Recruiter-Friendly

This is not a plain chatbot. The project demonstrates a production-style incident workflow:

- structured log ingestion
- anomaly and risk scoring
- root-cause hypothesis generation
- runbook matching
- timeline reconstruction
- incident report generation
- API and CLI interfaces
- testable deterministic behavior before LLM integration

## Next Technical Milestones

1. Replace the statistical detector with a PyTorch anomaly model.
2. Add LangGraph nodes for log investigation, metrics investigation, runbook retrieval, and postmortem writing.
3. Add vector search over runbooks and service docs.
4. Add a dashboard for incident timeline, severity, confidence, and recommended actions.
5. Add eval datasets for precision, recall, false positives, and report usefulness.
