from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base


# Klasa bazowa dla SQLAlchemy
Base = declarative_base()


# Model SQLAlchemy
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)  # automatycznie ustawia czas dodania

