from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db_models import TriageRecord
from app.models import SupportRequest, TriageResult


def save_triage_record(
    session: Session,
    request: SupportRequest,
    result: TriageResult,
) -> TriageRecord:
    record = TriageRecord(
        subject=request.subject,
        description=request.description,
        category=result.category,
        priority=result.priority,
        summary=result.summary,
        next_action=result.next_action,
        draft_response=result.draft_response,
    )

    session.add(record)

    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise

    session.refresh(record)

    return record


def list_triage_records(session: Session) -> list[TriageRecord]:
    statement = select(TriageRecord).order_by(TriageRecord.id.desc())

    return list(session.scalars(statement).all())
