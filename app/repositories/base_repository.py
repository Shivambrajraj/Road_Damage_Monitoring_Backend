# app/repositories/base_repository.py
from typing import Generic, TypeVar, Type
from sqlalchemy.orm import Session
from app.core.database import Base

# VS Code will now see Base as a true class and remove the orange line!
ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> ModelType | None:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session):
        return db.query(self.model).all()