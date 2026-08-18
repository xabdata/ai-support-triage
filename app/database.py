import os
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


def get_required_environment_variable(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"{name} environment variable is required")

    return value


def get_database_url() -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=get_required_environment_variable("POSTGRES_USER"),
        password=get_required_environment_variable("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=get_required_environment_variable("POSTGRES_DB"),
    )


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )

def create_tables() -> None:
    import app.db_models  # Registra los modelos en Base.metadata.

    Base.metadata.create_all(get_engine())

def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session
