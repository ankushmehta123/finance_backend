import os
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth import get_password_hash
from app.database import Base
from app.models import User, FinancialRecord


DATABASE_URL = "sqlite:///./data/finance.db"


def dt(year: int, month: int, day: int) -> str:
    return datetime(year, month, day).isoformat(timespec="seconds")


def main() -> None:
    os.makedirs("./data", exist_ok=True)

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)

    users_seed = [
        {
            "name": "admin",
            "email": "admin@example.com",
            "password": "Admin@123",
            "role": "admin",
            "is_active": True,
        },
        {
            "name": "analyst",
            "email": "analyst@example.com",
            "password": "Analyst@123",
            "role": "analyst",
            "is_active": True,
        },
        {
            "name": "viewer",
            "email": "viewer@example.com",
            "password": "Viewer@123",
            "role": "viewer",
            "is_active": True,
        },
    ]

    records_seed = [
        {"email": "admin@example.com", "amount": "5500.00", "record_type": "income", "category": "salary", "record_date": dt(2026, 1, 5), "notes": "Salary payment - Jan"},
        {"email": "admin@example.com", "amount": "820.00", "record_type": "income", "category": "bonus", "record_date": dt(2026, 1, 20), "notes": "Performance bonus"},
        {"email": "admin@example.com", "amount": "165.75", "record_type": "expense", "category": "groceries", "record_date": dt(2026, 1, 8), "notes": "Groceries"},
        {"email": "admin@example.com", "amount": "79.30", "record_type": "expense", "category": "transport", "record_date": dt(2026, 1, 11), "notes": "Transit"},
        {"email": "admin@example.com", "amount": "1050.00", "record_type": "expense", "category": "rent", "record_date": dt(2026, 1, 1), "notes": "Rent Jan"},
        {"email": "admin@example.com", "amount": "62.10", "record_type": "expense", "category": "utilities", "record_date": dt(2026, 1, 14), "notes": "Electricity"},
        {"email": "admin@example.com", "amount": "220.00", "record_type": "expense", "category": "healthcare", "record_date": dt(2026, 1, 18), "notes": "Pharmacy"},
        {"email": "admin@example.com", "amount": "98.40", "record_type": "expense", "category": "entertainment", "record_date": dt(2026, 1, 26), "notes": "Movies"},
        {"email": "admin@example.com", "amount": "5500.00", "record_type": "income", "category": "salary", "record_date": dt(2026, 2, 5), "notes": "Salary payment - Feb"},
        {"email": "admin@example.com", "amount": "165.20", "record_type": "expense", "category": "groceries", "record_date": dt(2026, 2, 10), "notes": "Groceries"},
        {"email": "admin@example.com", "amount": "92.60", "record_type": "expense", "category": "utilities", "record_date": dt(2026, 2, 15), "notes": "Internet + water"},
        {"email": "admin@example.com", "amount": "240.00", "record_type": "income", "category": "investment", "record_date": dt(2026, 2, 22), "notes": "Dividend"},
        {"email": "admin@example.com", "amount": "480.00", "record_type": "expense", "category": "shopping", "record_date": dt(2026, 2, 28), "notes": "Home essentials"},
        {"email": "admin@example.com", "amount": "1050.00", "record_type": "expense", "category": "rent", "record_date": dt(2026, 2, 1), "notes": "Rent Feb"},
        {"email": "admin@example.com", "amount": "130.50", "record_type": "expense", "category": "food", "record_date": dt(2026, 2, 18), "notes": "Dining out"},
        {"email": "admin@example.com", "amount": "1750.00", "record_type": "income", "category": "freelance", "record_date": dt(2026, 3, 12), "notes": "Freelance project"},
        {"email": "admin@example.com", "amount": "300.00", "record_type": "expense", "category": "travel", "record_date": dt(2026, 3, 7), "notes": "Business trip"},
        {"email": "admin@example.com", "amount": "5500.00", "record_type": "income", "category": "salary", "record_date": dt(2026, 4, 5), "notes": "Salary payment - Apr"},

        {"email": "analyst@example.com", "amount": "4200.00", "record_type": "income", "category": "salary", "record_date": dt(2026, 1, 6), "notes": "Salary Jan"},
        {"email": "analyst@example.com", "amount": "650.00", "record_type": "income", "category": "freelance", "record_date": dt(2026, 1, 28), "notes": "Consulting"},
        {"email": "analyst@example.com", "amount": "120.45", "record_type": "expense", "category": "transport", "record_date": dt(2026, 1, 9), "notes": "Fuel"},
        {"email": "analyst@example.com", "amount": "980.00", "record_type": "expense", "category": "rent", "record_date": dt(2026, 1, 1), "notes": "Rent Jan"},
        {"email": "analyst@example.com", "amount": "154.90", "record_type": "expense", "category": "groceries", "record_date": dt(2026, 1, 13), "notes": "Groceries"},
        {"email": "analyst@example.com", "amount": "58.80", "record_type": "expense", "category": "utilities", "record_date": dt(2026, 1, 21), "notes": "Utilities"},
        {"email": "analyst@example.com", "amount": "74.25", "record_type": "expense", "category": "healthcare", "record_date": dt(2026, 1, 25), "notes": "Dental"},
        {"email": "analyst@example.com", "amount": "120.00", "record_type": "income", "category": "investment", "record_date": dt(2026, 2, 18), "notes": "Interest"},
        {"email": "analyst@example.com", "amount": "4200.00", "record_type": "income", "category": "salary", "record_date": dt(2026, 2, 6), "notes": "Salary Feb"},
        {"email": "analyst@example.com", "amount": "190.10", "record_type": "expense", "category": "shopping", "record_date": dt(2026, 2, 12), "notes": "Office supplies"},
        {"email": "analyst@example.com", "amount": "110.60", "record_type": "expense", "category": "food", "record_date": dt(2026, 2, 17), "notes": "Lunch"},
        {"email": "analyst@example.com", "amount": "980.00", "record_type": "expense", "category": "rent", "record_date": dt(2026, 2, 1), "notes": "Rent Feb"},
        {"email": "analyst@example.com", "amount": "65.90", "record_type": "expense", "category": "entertainment", "record_date": dt(2026, 2, 27), "notes": "Streaming"},
        {"email": "analyst@example.com", "amount": "420.00", "record_type": "income", "category": "freelance", "record_date": dt(2026, 3, 8), "notes": "Market research"},
        {"email": "analyst@example.com", "amount": "130.00", "record_type": "expense", "category": "education", "record_date": dt(2026, 3, 15), "notes": "Course fee"},
        {"email": "analyst@example.com", "amount": "250.00", "record_type": "expense", "category": "travel", "record_date": dt(2026, 3, 28), "notes": "Conference travel"},

        {"email": "viewer@example.com", "amount": "3000.00", "record_type": "income", "category": "salary", "record_date": dt(2026, 1, 7), "notes": "Salary Jan"},
        {"email": "viewer@example.com", "amount": "760.00", "record_type": "expense", "category": "rent", "record_date": dt(2026, 1, 1), "notes": "Rent Jan"},
        {"email": "viewer@example.com", "amount": "135.20", "record_type": "expense", "category": "groceries", "record_date": dt(2026, 1, 12), "notes": "Groceries"},
        {"email": "viewer@example.com", "amount": "40.60", "record_type": "expense", "category": "transport", "record_date": dt(2026, 1, 16), "notes": "Commute"},
        {"email": "viewer@example.com", "amount": "70.50", "record_type": "expense", "category": "utilities", "record_date": dt(2026, 1, 22), "notes": "Electricity"},
        {"email": "viewer@example.com", "amount": "88.99", "record_type": "expense", "category": "entertainment", "record_date": dt(2026, 1, 30), "notes": "Game subscription"},
        {"email": "viewer@example.com", "amount": "95.00", "record_type": "income", "category": "bonus", "record_date": dt(2026, 2, 2), "notes": "Bonus"},
        {"email": "viewer@example.com", "amount": "3000.00", "record_type": "income", "category": "salary", "record_date": dt(2026, 2, 7), "notes": "Salary Feb"},
        {"email": "viewer@example.com", "amount": "760.00", "record_type": "expense", "category": "rent", "record_date": dt(2026, 2, 1), "notes": "Rent Feb"},
        {"email": "viewer@example.com", "amount": "150.00", "record_type": "expense", "category": "shopping", "record_date": dt(2026, 2, 14), "notes": "Clothing"},
        {"email": "viewer@example.com", "amount": "102.75", "record_type": "expense", "category": "food", "record_date": dt(2026, 2, 18), "notes": "Takeout"},
        {"email": "viewer@example.com", "amount": "40.00", "record_type": "income", "category": "refund", "record_date": dt(2026, 2, 25), "notes": "Refund"},
        {"email": "viewer@example.com", "amount": "60.00", "record_type": "expense", "category": "healthcare", "record_date": dt(2026, 3, 6), "notes": "Insurance copay"},
        {"email": "viewer@example.com", "amount": "185.40", "record_type": "expense", "category": "groceries", "record_date": dt(2026, 3, 9), "notes": "Monthly groceries"},
        {"email": "viewer@example.com", "amount": "3000.00", "record_type": "income", "category": "salary", "record_date": dt(2026, 3, 7), "notes": "Salary Mar"},
        {"email": "viewer@example.com", "amount": "240.00", "record_type": "expense", "category": "travel", "record_date": dt(2026, 3, 27), "notes": "Weekend getaway"},
    ]

    with SessionLocal() as session:
        email_to_user_id = {}

        for u in users_seed:
            existing = session.query(User).filter(User.email == u["email"]).first()
            if existing is None:
                user = User(
                    name=u["name"],
                    email=u["email"],
                    password_hash=get_password_hash(u["password"]),
                    role=u["role"],
                    is_active=u["is_active"],
                    created_at=datetime.utcnow().isoformat(timespec="seconds"),
                )
                session.add(user)
                session.flush()
                email_to_user_id[u["email"]] = user.id
            else:
                email_to_user_id[u["email"]] = existing.id

        for r in records_seed:
            session.add(
                FinancialRecord(
                    user_id=email_to_user_id[r["email"]],
                    amount=Decimal(r["amount"]),
                    record_type=r["record_type"],
                    category=r["category"],
                    record_date=r["record_date"],
                    notes=r["notes"],
                    created_at=datetime.utcnow().isoformat(timespec="seconds"),
                )
            )

        session.commit()

    print("Database setup complete.")


if __name__ == "__main__":
    main()