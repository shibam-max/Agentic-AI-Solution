from fastapi import FastAPI, HTTPException

from app.core.pipeline import review_logs
from app.schemas.models import ReviewRequest, ReviewResponse

app = FastAPI(
    title="Agentic Incident Response",
    description="Detect incidents from logs and generate investigation reports.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review/logs", response_model=ReviewResponse)
def review_log_payload(request: ReviewRequest) -> ReviewResponse:
    try:
        return review_logs(request.raw_logs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
