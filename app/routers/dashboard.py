from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.dependencies import require_roles
from app.schemas import (
    CategoryTotalOut,
    DashboardSummaryOut,
    RecordOut,
    MonthlyTrendOut,
    RecentActivityOut,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryOut,
    dependencies=[Depends(require_roles(["viewer", "analyst", "admin"]))],
)
def get_summary(db: Session = Depends(get_db)) -> dict:
    return crud.get_summary(db)


@router.get(
    "/category-totals",
    response_model=list[CategoryTotalOut],
    dependencies=[Depends(require_roles(["viewer", "analyst", "admin"]))],
)
def get_category_totals(db: Session = Depends(get_db)) -> list[dict]:
    return crud.get_category_totals(db)


@router.get(
    "/recent-activity",
    response_model=list[RecentActivityOut],
    dependencies=[Depends(require_roles(["viewer", "analyst", "admin"]))],
)
def get_recent_activity(
    db: Session = Depends(get_db),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[RecordOut]:
    return crud.get_recent_activity(db, limit=limit)


@router.get(
    "/monthly-trends",
    response_model=list[MonthlyTrendOut],
    dependencies=[Depends(require_roles(["viewer", "analyst", "admin"]))],
)
def get_monthly_trends(db: Session = Depends(get_db)) -> list[dict]:
    return crud.get_monthly_trends(db)