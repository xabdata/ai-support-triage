import pytest

from app.database import get_database_url


def test_get_database_url_uses_environment_variables(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")
    monkeypatch.setenv("POSTGRES_HOST", "database.example")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("POSTGRES_DB", "test_database")

    url = get_database_url()

    assert url.drivername == "postgresql+psycopg"
    assert url.username == "test_user"
    assert url.password == "test_password"
    assert url.host == "database.example"
    assert url.port == 5433
    assert url.database == "test_database"


def test_get_database_url_requires_password(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_DB", "test_database")
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)

    with pytest.raises(
        RuntimeError,
        match="POSTGRES_PASSWORD environment variable is required",
    ):
        get_database_url()
