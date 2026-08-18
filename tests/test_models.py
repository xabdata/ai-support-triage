from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models import SupportRequest, TriageHistoryItem, TriageResult


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


def test_triage_history_item_accepts_orm_attributes():
    created_at = datetime(2026, 8, 18, 16, 18, tzinfo=UTC)
    record = SimpleNamespace(
        id=1,
        subject="No puedo iniciar sesión",
        description="Mi contraseña es rechazada desde esta mañana.",
        category="account",
        priority="high",
        summary="El cliente no puede iniciar sesión.",
        next_action="Ayudar al cliente a restablecer su contraseña.",
        draft_response="Vamos a ayudarte a recuperar el acceso a tu cuenta.",
        created_at=created_at,
    )

    history_item = TriageHistoryItem.model_validate(record)

    assert history_item.id == 1
    assert history_item.subject == "No puedo iniciar sesión"
    assert history_item.category == "account"
    assert history_item.priority == "high"
    assert history_item.created_at == created_at