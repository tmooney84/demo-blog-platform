from sqlmodel import Field, Session, SQLModel, create_engine, select
from models import Product, ProductRequest
from typing import Generator

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Allows FastAPI to use the same SQLite DB in different threads
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
