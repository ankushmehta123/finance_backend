from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.auth import get_password_hash
from app.database import get_db
from app.dependencies import require_roles
from app.models import User
from app.schemas import UserCreate, UserOut, UserRoleUpdate, UserStatusUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["admin"]))],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = crud.get_user_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = get_password_hash(payload.password)

    return crud.create_user(
        db=db,
        user_in=payload,
        password_hash=password_hash,
    )


@router.get(
    "",
    response_model=list[UserOut],
    dependencies=[Depends(require_roles(["admin"]))],
)
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return crud.list_users(db)


@router.get(
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_roles(["admin"]))],
)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}/role",
    response_model=UserOut,
    dependencies=[Depends(require_roles(["admin"]))],
)
def update_role(user_id: int, payload: UserRoleUpdate, db: Session = Depends(get_db)) -> User:
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user_role(db, user, payload.role)


@router.patch(
    "/{user_id}/status",
    response_model=UserOut,
    dependencies=[Depends(require_roles(["admin"]))],
)
def update_status(
    user_id: int, payload: UserStatusUpdate, db: Session = Depends(get_db)
) -> User:
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user_status(db, user, payload.is_active)