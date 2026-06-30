# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase # Changed import here
from app.core.config import settings

# "check_same_thread" is a SQLite-only quirk; Postgres doesn't understand it
# and will error if passed. Only apply it when actually running on SQLite,
# so the same code works for local dev (sqlite) and production (Postgres).
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modern SQLAlchemy 2.0 style: Create an explicit class instead of a function call
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()