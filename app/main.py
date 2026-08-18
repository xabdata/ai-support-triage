from fastapi import FastAPI

from app.llm import triage_with_llm
from app.models import SupportRequest, TriageResult


app = FastAPI(title="AI Support Triage")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResult)
def triage_support_request(request: SupportRequest) -> TriageResult:
    return triage_with_llm(request)
