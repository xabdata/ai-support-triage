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


def calculate_metrics(
    scores: list[dict[str, bool]],
) -> dict[str, int | float]:
    total_cases = len(scores)

    category_accuracy = (
        sum(score["category_correct"] for score in scores)
        / total_cases
        * 100
    )
    priority_accuracy = (
        sum(score["priority_correct"] for score in scores)
        / total_cases
        * 100
    )
    exact_match_accuracy = (
        sum(score["exact_match"] for score in scores)
        / total_cases
        * 100
    )

    return {
        "total_cases": total_cases,
        "category_accuracy": round(category_accuracy, 2),
        "priority_accuracy": round(priority_accuracy, 2),
        "exact_match_accuracy": round(exact_match_accuracy, 2),
    }
