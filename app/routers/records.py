from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.dependencies import require_roles
from app.models import FinancialRecord
from app.schemas import RecordCreate, RecordOut, RecordUpdate

router = APIRouter(prefix="/records", tags=["records"])


@router.post(
    "",
    response_model=RecordOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["admin"]))],
)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
) -> FinancialRecord:
    user = crud.get_user_by_id(db, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_record(db, payload)


@router.get(
    "",
    response_model=list[RecordOut],
    dependencies=[Depends(require_roles(["analyst", "admin"]))],
)
def list_records(
    db: Session = Depends(get_db),
    record_type: str | None = Query(default=None, pattern="^(income|expense)$"),
    category: str | None = Query(default=None, min_length=1, max_length=100),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> list[FinancialRecord]:
    return crud.list_records(
        db,
        record_type=record_type,
        category=category,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/{record_id}",
    response_model=RecordOut,
    dependencies=[Depends(require_roles(["analyst", "admin"]))],
)
def get_record(record_id: int, db: Session = Depends(get_db)) -> FinancialRecord:
    record = crud.get_record_by_id(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.patch(
    "/{record_id}",
    response_model=RecordOut,
    dependencies=[Depends(require_roles(["admin"]))],
)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
) -> FinancialRecord:
    record = crud.get_record_by_id(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return crud.update_record(db, record, payload)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(["admin"]))],
)
def delete_record(record_id: int, db: Session = Depends(get_db)) -> None:
    record = crud.get_record_by_id(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    crud.delete_record(db, record)
    return None