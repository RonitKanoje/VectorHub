from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from threadcore.api.dependencies import get_current_user
from threadcore.api.schemas import UserCreateRequest, UserResponse
from threadcore.infrastructure.db.models import UserDB
from threadcore.infrastructure.db.repositories import (
    get_all_users,
    get_user_by_username,
)
from threadcore.infrastructure.db.session import get_db


router = APIRouter(tags=["auth"])


def _resolve_user(x_user_id: str = Header(..., alias="X-User-Id"), db: Session = Depends(get_db)):
    return get_current_user(x_user_id=x_user_id, db=db)


# ---------------------------------------------------------------------------
# NOTE: /register and /login (token) have moved to the Express server.
# Express handles bcrypt password hashing and JWT signing.
# FastAPI only exposes these internal-only endpoints below.
# ---------------------------------------------------------------------------


@router.post("/register", response_model=UserResponse)
def register(user: UserCreateRequest, db: Session = Depends(get_db)):
    """
    Internal endpoint called by Express after it has already hashed the
    password. The 'password' field received here is the bcrypt hash produced
    by Node — FastAPI stores it as-is.
    """
    existing = get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = UserDB(
        name=user.name,
        username=user.username,
        password_hash=user.password,  # Express sends the hash, not plaintext
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: UserDB = Depends(_resolve_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


@router.get("/users", response_model=List[UserResponse])
def get_users(
    current_user: UserDB = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    return get_all_users(db)
