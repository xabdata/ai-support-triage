from app.db_models import TriageRecord


def test_triage_record_table_definition():
    table = TriageRecord.__table__

    assert table.name == "triage_records"
    assert set(table.columns.keys()) == {
        "id",
        "subject",
        "description",
        "category",
        "priority",
        "summary",
        "next_action",
        "draft_response",
        "created_at",
    }

    assert table.c.id.primary_key
    assert table.c.subject.type.length == 120
    assert table.c.summary.type.length == 500
    assert table.c.next_action.type.length == 500
    assert table.c.draft_response.type.length == 2000
    assert table.c.created_at.server_default is not None