import json
from unittest.mock import Mock, patch

from app.llm import MODEL
from app.models import TriageResult
from evals.run_evaluation import (
    DATASET_PATH,
    REPORT_PATH,
    calculate_metrics,
    evaluate_cases,
    main,
    run_evaluation,
    score_case,
)


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


def test_calculate_metrics_returns_accuracy_percentages():
    scores = [
        {
            "category_correct": True,
            "priority_correct": True,
            "exact_match": True,
        },
        {
            "category_correct": True,
            "priority_correct": False,
            "exact_match": False,
        },
    ]

    metrics = calculate_metrics(scores)

    assert metrics == {
        "total_cases": 2,
        "category_accuracy": 100.0,
        "priority_accuracy": 50.0,
        "exact_match_accuracy": 50.0,
    }


def test_evaluate_cases_runs_triage_and_builds_report():
    case = {
        "id": "billing-01",
        "request": {
            "subject": "Cargo duplicado",
            "description": "La misma factura aparece cobrada dos veces.",
        },
        "expected_category": "billing",
        "expected_priority": "high",
    }
    result = TriageResult(
        category="billing",
        priority="medium",
        summary="El cliente informa de un cargo duplicado.",
        next_action="Revisar los movimientos de facturación.",
        draft_response="Vamos a revisar los cargos asociados a su cuenta.",
    )
    triage_function = Mock(return_value=result)

    report = evaluate_cases(
        [case],
        triage_function,
    )

    assert report == {
        "metrics": {
            "total_cases": 1,
            "category_accuracy": 100.0,
            "priority_accuracy": 0.0,
            "exact_match_accuracy": 0.0,
        },
        "results": [
            {
                "id": "billing-01",
                "expected_category": "billing",
                "actual_category": "billing",
                "expected_priority": "high",
                "actual_priority": "medium",
                "category_correct": True,
                "priority_correct": False,
                "exact_match": False,
                "summary": result.summary,
                "next_action": result.next_action,
                "draft_response": result.draft_response,
            }
        ],
    }

    called_request = triage_function.call_args.args[0]
    assert called_request.subject == "Cargo duplicado"
    assert called_request.description == (
        "La misma factura aparece cobrada dos veces."
    )


def test_run_evaluation_loads_cases_and_writes_report(
    tmp_path,
):
    dataset_path = tmp_path / "cases.json"
    report_path = tmp_path / "results.json"
    case = {
        "id": "billing-01",
        "request": {
            "subject": "Cargo duplicado",
            "description": "La misma factura aparece cobrada dos veces.",
        },
        "expected_category": "billing",
        "expected_priority": "high",
    }
    result = TriageResult(
        category="billing",
        priority="high",
        summary="El cliente informa de un cargo duplicado.",
        next_action="Revisar los movimientos de facturación.",
        draft_response="Vamos a revisar los cargos asociados a su cuenta.",
    )
    triage_function = Mock(return_value=result)

    dataset_path.write_text(
        json.dumps([case]),
        encoding="utf-8",
    )

    report = run_evaluation(
        dataset_path,
        report_path,
        triage_function,
    )

    assert report["model"] == MODEL
    assert report["metrics"]["total_cases"] == 1
    assert json.loads(
        report_path.read_text(encoding="utf-8")
    ) == report
    triage_function.assert_called_once()


def test_main_uses_default_paths_and_prints_summary(
    capsys,
):
    report = {
        "model": MODEL,
        "metrics": {
            "total_cases": 20,
            "category_accuracy": 90.0,
            "priority_accuracy": 80.0,
            "exact_match_accuracy": 75.0,
        },
        "results": [],
    }

    with patch(
        "evals.run_evaluation.run_evaluation",
        return_value=report,
    ) as mock_run:
        main()

    dataset_path, report_path, triage_function = (
        mock_run.call_args.args
    )
    assert dataset_path == DATASET_PATH
    assert report_path == REPORT_PATH
    assert callable(triage_function)

    output = capsys.readouterr().out
    assert "20" in output
    assert "90.0%" in output
    assert "80.0%" in output
    assert "75.0%" in output
