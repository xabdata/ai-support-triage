from unittest.mock import Mock, patch

from app.llm import MODEL, SYSTEM_PROMPT, triage_with_llm
from app.models import SupportRequest, TriageResult


def test_triage_with_llm_returns_structured_result():
    request = SupportRequest(
        subject="Error al iniciar sesión",
        description="No puedo acceder a mi cuenta con mi contraseña.",
    )
    expected_result = TriageResult(
        category="account",
        priority="high",
        summary="El cliente no puede iniciar sesión.",
        next_action="Ayudar al cliente a restablecer su contraseña.",
        draft_response="Vamos a ayudarte a recuperar el acceso a tu cuenta.",
    )

    mock_client = Mock()
    mock_client.responses.parse.return_value.output_parsed = expected_result

    with patch("app.llm.OpenAI", return_value=mock_client) as mock_openai:
        result = triage_with_llm(request)

    assert result == expected_result
    mock_openai.assert_called_once_with()
    mock_client.responses.parse.assert_called_once_with(
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request.model_dump_json()},
        ],
        text_format=TriageResult,
    )
