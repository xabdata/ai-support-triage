from unittest.mock import Mock

from sqlalchemy.orm import Session

from app.models import SupportRequest, TriageResult
from app.repository import list_triage_records, save_triage_record


def test_save_triage_record_commits_complete_record():
    session = Mock(spec=Session)
    request = SupportRequest(
        subject="Error al iniciar sesión",
        description="No puedo acceder con mi contraseña.",
    )
    result = TriageResult(
        category="account",
        priority="high",
        summary="El cliente no puede iniciar sesión.",
        next_action="Ayudar al cliente a restablecer su contraseña.",
        draft_response="Vamos a ayudarte a recuperar el acceso a tu cuenta.",
    )

    saved_record = save_triage_record(session, request, result)

    assert saved_record.subject == request.subject
    assert saved_record.description == request.description
    assert saved_record.category == result.category
    assert saved_record.priority == result.priority
    assert saved_record.summary == result.summary
    assert saved_record.next_action == result.next_action
    assert saved_record.draft_response == result.draft_response

    session.add.assert_called_once_with(saved_record)
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(saved_record)


def test_list_triage_records_orders_newest_first():
    session = Mock(spec=Session)
    newest_record = object()
    oldest_record = object()
    session.scalars.return_value.all.return_value = [
        newest_record,
        oldest_record,
    ]

    records = list_triage_records(session)

    assert records == [newest_record, oldest_record]
    session.scalars.assert_called_once()

    statement = session.scalars.call_args.args[0]
    assert "ORDER BY triage_records.id DESC" in str(statement)