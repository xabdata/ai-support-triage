import json
from collections.abc import Callable
from pathlib import Path

from app.llm import MODEL, triage_with_llm
from app.models import SupportRequest, TriageResult

EVALUATION_DIR = Path(__file__).parent
DATASET_PATH = EVALUATION_DIR / "cases.json"
REPORT_PATH = EVALUATION_DIR / "results.json"


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


def evaluate_cases(
    cases: list[dict[str, object]],
    triage_function: Callable[
        [SupportRequest],
        TriageResult,
    ] = triage_with_llm,
) -> dict[str, object]:
    scores: list[dict[str, bool]] = []
    results: list[dict[str, object]] = []

    for case in cases:
        request = SupportRequest.model_validate(
            case["request"]
        )
        result = triage_function(request)
        score = score_case(case, result)

        scores.append(score)
        results.append(
            {
                "id": case["id"],
                "expected_category": case[
                    "expected_category"
                ],
                "actual_category": result.category,
                "expected_priority": case[
                    "expected_priority"
                ],
                "actual_priority": result.priority,
                **score,
                "summary": result.summary,
                "next_action": result.next_action,
                "draft_response": result.draft_response,
            }
        )

    return {
        "metrics": calculate_metrics(scores),
        "results": results,
    }


def run_evaluation(
    dataset_path: Path,
    report_path: Path,
    triage_function: Callable[
        [SupportRequest],
        TriageResult,
    ] = triage_with_llm,
) -> dict[str, object]:
    cases = json.loads(
        dataset_path.read_text(encoding="utf-8")
    )
    evaluation = evaluate_cases(
        cases,
        triage_function,
    )
    report = {
        "model": MODEL,
        **evaluation,
    }

    report_path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return report


def main() -> None:
    def triage_with_progress(
        request: SupportRequest,
    ) -> TriageResult:
        print(
            f"Evaluating: {request.subject}",
            flush=True,
        )
        return triage_with_llm(request)

    report = run_evaluation(
        DATASET_PATH,
        REPORT_PATH,
        triage_with_progress,
    )
    metrics = report["metrics"]

    print("Evaluation complete")
    print(f"Cases: {metrics['total_cases']}")
    print(
        "Category accuracy: "
        f"{metrics['category_accuracy']}%"
    )
    print(
        "Priority accuracy: "
        f"{metrics['priority_accuracy']}%"
    )
    print(
        "Exact match accuracy: "
        f"{metrics['exact_match_accuracy']}%"
    )
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
