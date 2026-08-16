import pytest
from pydantic import ValidationError

from app.models import SupportRequest, TriageResult


def test_support_request_accepts_valid_data():
    request = SupportRequest(
        subject="Error al iniciar sesión",
        description="No puedo acceder con mi contraseña",
    )

    assert request.subject == "Error al iniciar sesión"
    assert request.description == "No puedo acceder con mi contraseña"


def test_support_request_rejects_short_subject():
    with pytest.raises(ValidationError):
        SupportRequest(
            subject="No",
            description="No puedo acceder con mi contraseña",
        )


def test_triage_result_accepts_valid_data():
    result = TriageResult(
        category="technical",
        priority="high",
        summary="El usuario no puede iniciar sesión",
        next_action="Revisar el estado de su cuenta",
        draft_response="Estamos revisando el problema de acceso a su cuenta",
    )

    assert result.category == "technical"
    assert result.priority == "high"
    assert result.summary == "El usuario no puede iniciar sesión"


def test_triage_result_rejects_unknown_category():
    with pytest.raises(ValidationError):
        TriageResult(
            category="sales",
            priority="high",
            summary="El usuario no puede iniciar sesión",
            next_action="Revisar el estado de su cuenta",
            draft_response="Estamos revisando el problema de acceso a su cuenta",
        )