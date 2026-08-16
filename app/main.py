from fastapi import FastAPI

from app.models import SupportRequest


app = FastAPI(title="AI Support Triage")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage")
def triage_support_request(request: SupportRequest) -> dict[str, str]:
    return {
        "message": "Support request received",
        "subject": request.subject,
    }