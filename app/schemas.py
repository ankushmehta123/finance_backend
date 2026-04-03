from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Users ----------

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str
    is_active: bool = True


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    role: str


class UserStatusUpdate(BaseModel):
    is_active: bool


# ---------- Records ----------

class RecordCreate(BaseModel):
    user_id: int
    amount: Decimal
    record_type: str
    category: str
    record_date: date
    notes: Optional[str] = None


class RecordUpdate(BaseModel):
    amount: Optional[Decimal] = None
    record_type: Optional[str] = None
    category: Optional[str] = None
    record_date: Optional[date] = None
    notes: Optional[str] = None


class RecordOut(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    record_type: str
    category: str
    record_date: str
    notes: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


# ---------- Dashboard ----------

class DashboardSummaryOut(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal


class CategoryTotalOut(BaseModel):
    category: str
    record_type: str
    total_amount: float


class MonthlyTrendOut(BaseModel):
    month: str
    record_type: str
    total_amount: float


class RecentActivityOut(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    record_type: str
    category: str
    record_date: str
    notes: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}