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
    session.commit()
    session.refresh(record)

    return record