# app/dependencies/database.py
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def get_db_session() -> Generator[Session, None, None]:
    """
    Enterprise dependency provider that yields a localized database 
    session wrapper and guarantees transaction termination.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()