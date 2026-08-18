from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import get_session
from app.main import app
from app.models import TriageResult


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


def test_app_creates_tables_on_startup():
    with patch("app.main.create_tables") as mock_create_tables:
        with TestClient(app):
            pass

    mock_create_tables.assert_called_once_with()