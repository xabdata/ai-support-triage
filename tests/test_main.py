from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_triage_accepts_valid_request():
    response = client.post(
        "/triage",
        json={
            "subject": "Error al iniciar sesión",
            "description": "No puedo acceder con mi contraseña",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Support request received",
        "subject": "Error al iniciar sesión",
    }


def test_triage_rejects_short_subject():
    response = client.post(
        "/triage",
        json={
            "subject": "No",
            "description": "No puedo acceder con mi contraseña",
        },
    )

    assert response.status_code == 422