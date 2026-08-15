import pytest
from pydantic import ValidationError

from app.models import SupportRequest


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