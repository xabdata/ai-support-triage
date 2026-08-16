from fastapi import FastAPI


app = FastAPI(title="AI Support Triage")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}