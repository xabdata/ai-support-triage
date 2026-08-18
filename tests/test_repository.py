from unittest.mock import Mock

from sqlalchemy.orm import Session

from app.models import SupportRequest, TriageResult
from app.repository import save_triage_record


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