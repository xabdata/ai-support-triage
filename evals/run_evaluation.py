from app.models import TriageResult


def score_case(
    case: dict[str, object],
    result: TriageResult,
) -> dict[str, bool]:
    category_correct = (
        result.category == case["expected_category"]
    )
    priority_correct = (
        result.priority == case["expected_priority"]
    )

    return {
        "category_correct": category_correct,
        "priority_correct": priority_correct,
        "exact_match": category_correct and priority_correct,
    }
