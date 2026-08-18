from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models import TriageResult


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_triage_accepts_valid_request():
    triage_result = TriageResult(
        category="account",
        priority="high",
        summary="El cliente no puede iniciar sesión.",
        next_action="Ayudar al cliente a restablecer su contraseña.",
        draft_response="Vamos a ayudarte a recuperar el acceso a tu cuenta.",
    )

    with patch(
        "app.main.triage_with_llm",
        return_value=triage_result,
    ) as mock_triage:
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


def test_triage_rejects_short_subject():
    with patch("app.main.triage_with_llm") as mock_triage:
        response = client.post(
            "/triage",
            json={
                "subject": "No",
                "description": "No puedo acceder con mi contraseña",
            },
        )

    assert response.status_code == 422
    mock_triage.assert_not_called()
