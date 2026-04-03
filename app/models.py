from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(String(32), nullable=False)  # ISO timestamp string

    records = relationship("FinancialRecord", back_populates="user")


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    record_type = Column(String(20), nullable=False)  # "income" / "expense"
    category = Column(String(100), nullable=False)
    record_date = Column(String(32), nullable=False)  # ISO date string
    notes = Column(String(255), nullable=True)
    created_at = Column(String(32), nullable=False)  # ISO timestamp string

    user = relationship("User", back_populates="records")