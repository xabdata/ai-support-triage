import json
from pathlib import Path

from app.models import SupportRequest


DATASET_PATH = (
    Path(__file__).parents[1]
    / "evals"
    / "cases.json"
)
VALID_CATEGORIES = {
    "technical",
    "billing",
    "account",
    "other",
}
VALID_PRIORITIES = {
    "low",
    "medium",
    "high",
    "urgent",
}


def test_evaluation_dataset_contains_20_valid_cases():
    cases = json.loads(
        DATASET_PATH.read_text(encoding="utf-8")
    )

    case_ids = []

    for case in cases:
        case_ids.append(case["id"])
        SupportRequest.model_validate(case["request"])
        assert case["expected_category"] in VALID_CATEGORIES
        assert case["expected_priority"] in VALID_PRIORITIES

    assert len(cases) == 20
    assert len(case_ids) == len(set(case_ids))
