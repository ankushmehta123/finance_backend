from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas


# ---------- Users ----------

def create_user(db: Session, user_in: schemas.UserCreate, password_hash: str):
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        password_hash=password_hash,
        role=user_in.role,
        is_active=user_in.is_active,
        created_at=datetime.utcnow().isoformat(timespec="seconds"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def list_users(db: Session):
    return db.query(models.User).order_by(models.User.id.asc()).all()


def update_user_role(db: Session, user: models.User, new_role: str):
    user.role = new_role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_status(db: Session, user: models.User, is_active: bool):
    user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- Records ----------

def create_record(db: Session, record_in: schemas.RecordCreate):
    record = models.FinancialRecord(
        user_id=record_in.user_id,
        amount=record_in.amount,
        record_type=record_in.record_type,
        category=record_in.category,
        record_date=record_in.record_date.isoformat(),  # date -> "YYYY-MM-DD"
        notes=record_in.notes,
        created_at=datetime.utcnow().isoformat(timespec="seconds"),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_record_by_id(db: Session, record_id: int):
    return db.query(models.FinancialRecord).filter(models.FinancialRecord.id == record_id).first()


def list_records(
    db: Session,
    record_type: str | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    query = db.query(models.FinancialRecord)

    if record_type:
        query = query.filter(models.FinancialRecord.record_type == record_type)

    if category:
        query = query.filter(models.FinancialRecord.category.ilike(f"%{category}%"))

    if start_date:
        query = query.filter(
            models.FinancialRecord.record_date >= start_date.isoformat()
        )

    if end_date:
        query = query.filter(
            models.FinancialRecord.record_date <= end_date.isoformat()
        )

    return query.order_by(models.FinancialRecord.record_date.desc()).all()


def update_record(db: Session, record: models.FinancialRecord, record_in: schemas.RecordUpdate):
    if record_in.amount is not None:
        record.amount = record_in.amount
    if record_in.record_type is not None:
        record.record_type = record_in.record_type
    if record_in.category is not None:
        record.category = record_in.category
    if record_in.record_date is not None:
        record.record_date = record_in.record_date.isoformat()
    if record_in.notes is not None:
        record.notes = record_in.notes

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record: models.FinancialRecord):
    db.delete(record)
    db.commit()


# ---------- Dashboard ----------

def get_summary(db: Session):
    income = (
        db.query(func.coalesce(func.sum(models.FinancialRecord.amount), 0))
        .filter(models.FinancialRecord.record_type == "income")
        .scalar()
    )

    expense = (
        db.query(func.coalesce(func.sum(models.FinancialRecord.amount), 0))
        .filter(models.FinancialRecord.record_type == "expense")
        .scalar()
    )

    income = Decimal(income)
    expense = Decimal(expense)

    return {
        "total_income": income,
        "total_expenses": expense,
        "net_balance": income - expense,
    }


def get_category_totals(db: Session):
    rows = (
        db.query(
            models.FinancialRecord.category,
            models.FinancialRecord.record_type,
            func.sum(models.FinancialRecord.amount).label("total_amount"),
        )
        .group_by(models.FinancialRecord.category, models.FinancialRecord.record_type)
        .order_by(models.FinancialRecord.category.asc())
        .all()
    )

    return [
        {
            "category": row.category,
            "record_type": row.record_type,
            "total_amount": float(row.total_amount),
        }
        for row in rows
    ]


def get_monthly_trends(db: Session):
    rows = (
        db.query(
            func.substr(models.FinancialRecord.record_date, 1, 7).label("month"),
            models.FinancialRecord.record_type,
            func.sum(models.FinancialRecord.amount).label("total_amount"),
        )
        .group_by(
            func.substr(models.FinancialRecord.record_date, 1, 7),
            models.FinancialRecord.record_type,
        )
        .order_by("month")
        .all()
    )

    return [
        {
            "month": row.month,
            "record_type": row.record_type,
            "total_amount": float(row.total_amount),
        }
        for row in rows
    ]


def get_recent_activity(db: Session, limit: int = 10):
    return (
        db.query(models.FinancialRecord)
        .order_by(models.FinancialRecord.record_date.desc())
        .limit(limit)
        .all()
    )