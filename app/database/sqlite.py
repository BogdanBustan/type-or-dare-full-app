from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

SQLITE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLITE_URL)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
