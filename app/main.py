from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from openai import APIError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import create_tables, get_session
from app.llm import triage_with_llm
from app.models import SupportRequest, TriageHistoryItem, TriageResult
from app.repository import list_triage_records, save_triage_record


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    create_tables()
    yield


app = FastAPI(
    title="AI Support Triage",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResult)
def triage_support_request(
    request: SupportRequest,
    session: Annotated[Session, Depends(get_session)],
) -> TriageResult:
    try:
        result = triage_with_llm(request)
    except APIError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Triage service is temporarily unavailable",
        ) from exc

    try:
        save_triage_record(session, request, result)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Triage service is temporarily unavailable",
        ) from exc

    return result


@app.get("/history", response_model=list[TriageHistoryItem])
def get_triage_history(
    session: Annotated[Session, Depends(get_session)],
) -> list[TriageHistoryItem]:
    try:
        records = list_triage_records(session)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Triage service is temporarily unavailable",
        ) from exc

    return [
        TriageHistoryItem.model_validate(record)
        for record in records
    ]
