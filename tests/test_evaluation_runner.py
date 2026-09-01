from app.models import TriageResult
from evals.run_evaluation import score_case


def test_score_case_compares_category_and_priority():
    case = {
        "expected_category": "billing",
        "expected_priority": "high",
    }
    result = TriageResult(
        category="billing",
        priority="medium",
        summary="El cliente informa de un problema de facturación.",
        next_action="Revisar los movimientos de facturación.",
        draft_response="Vamos a revisar los cargos asociados a su cuenta.",
    )

    score = score_case(case, result)

    assert score == {
        "category_correct": True,
        "priority_correct": False,
        "exact_match": False,
    }
