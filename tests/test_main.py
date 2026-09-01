from datetime import UTC, datetime
from unittest.mock import Mock, patch

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import APIConnectionError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_session
from app.main import app
from app.models import TriageHistoryItem, TriageResult


client = TestClient(app)


@pytest.fixture
def database_session():
    session = Mock(spec=Session)
    app.dependency_overrides[get_session] = lambda: session

    yield session

    app.dependency_overrides.clear()


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_triage_accepts_valid_request(database_session):
    triage_result = TriageResult(
        category="account",
        priority="high",
        summary="El cliente no puede iniciar sesión.",
        next_action="Ayudar al cliente a restablecer su contraseña.",
        draft_response="Vamos a ayudarte a recuperar el acceso a tu cuenta.",
    )

    with (
        patch(
            "app.main.triage_with_llm",
            return_value=triage_result,
        ) as mock_triage,
        patch("app.main.save_triage_record") as mock_save_record,
    ):
        response = client.post(
            "/triage",
            json={
                "subject": "Error al iniciar sesión",
                "description": "No puedo acceder con mi contraseña",
            },
        )

    assert response.status_code == 200
    assert response.json() == triage_result.model_dump()

    called_request = mock_triage.call_args.args[0]
    assert called_request.subject == "Error al iniciar sesión"
    assert called_request.description == "No puedo acceder con mi contraseña"

    mock_save_record.assert_called_once_with(
        database_session,
        called_request,
        triage_result,
    )


def test_triage_rejects_short_subject(database_session):
    with (
        patch("app.main.triage_with_llm") as mock_triage,
        patch("app.main.save_triage_record") as mock_save_record,
    ):
        response = client.post(
            "/triage",
            json={
                "subject": "No",
                "description": "No puedo acceder con mi contraseña",
            },
        )

    assert response.status_code == 422
    mock_triage.assert_not_called()
    mock_save_record.assert_not_called()


def test_history_returns_saved_records(database_session):
    history_item = TriageHistoryItem(
        id=1,
        subject="No puedo iniciar sesión",
        description="Mi contraseña es rechazada desde esta mañana.",
        category="account",
        priority="high",
        summary="El cliente no puede iniciar sesión.",
        next_action="Ayudar al cliente a restablecer su contraseña.",
        draft_response="Vamos a ayudarte a recuperar el acceso a tu cuenta.",
        created_at=datetime(2026, 8, 18, 16, 18, tzinfo=UTC),
    )

    with patch(
        "app.main.list_triage_records",
        return_value=[history_item],
    ) as mock_list_records:
        response = client.get("/history")

    assert response.status_code == 200
    assert response.json() == [
        history_item.model_dump(mode="json")
    ]
    mock_list_records.assert_called_once_with(database_session)


def test_app_creates_tables_on_startup():
    with patch("app.main.create_tables") as mock_create_tables:
        with TestClient(app):
            pass

    mock_create_tables.assert_called_once_with()


def test_triage_returns_503_when_openai_is_unavailable(database_session):
    openai_error = APIConnectionError(
        request=httpx.Request(
            "POST",
            "https://api.openai.com/v1/responses",
        )
    )

    with (
        patch(
            "app.main.triage_with_llm",
            side_effect=openai_error,
        ),
        patch("app.main.save_triage_record") as mock_save_record,
    ):
        response = client.post(
            "/triage",
            json={
                "subject": "Error al iniciar sesión",
                "description": "No puedo acceder con mi contraseña",
            },
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Triage service is temporarily unavailable"
    }
    mock_save_record.assert_not_called()


def test_triage_returns_503_when_database_is_unavailable(
    database_session,
):
    triage_result = TriageResult(
        category="account",
        priority="high",
        summary="El cliente no puede iniciar sesión.",
        next_action="Ayudar al cliente a restablecer su contraseña.",
        draft_response="Vamos a ayudarte a recuperar el acceso a tu cuenta.",
    )
    database_error = SQLAlchemyError("Database unavailable")

    with (
        patch(
            "app.main.triage_with_llm",
            return_value=triage_result,
        ),
        patch(
            "app.main.save_triage_record",
            side_effect=database_error,
        ),
    ):
        response = client.post(
            "/triage",
            json={
                "subject": "Error al iniciar sesión",
                "description": "No puedo acceder con mi contraseña",
            },
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Triage service is temporarily unavailable"
    }


def test_history_returns_503_when_database_is_unavailable(
    database_session,
):
    database_error = SQLAlchemyError("Database unavailable")

    with patch(
        "app.main.list_triage_records",
        side_effect=database_error,
    ):
        response = client.get("/history")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Triage service is temporarily unavailable"
    }
