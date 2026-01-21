from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserResponse
from app.dependencies import get_current_user, admin_only


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def read_current_user(data: dict = Depends(get_current_user)):
    return data["user"]

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), data: dict = Depends(admin_only)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/", response_model=list[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    data: dict = Depends(admin_only),
    # 🔍 SEARCH
    keyword: Optional[str] = Query(
        None, description="Search users by email"
    ),
    # 🎭 FILTER
    role: Optional[str] = Query(
        None, description="Filter users by role"
    ),
    # 🔃 SORT
    sort: str = Query(
        "desc", enum=["asc", "desc"]
    ),
    # 📄 PAGINATION
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(User)

    # SEARCH
    if keyword:
        query = query.filter(User.email.ilike(f"%{keyword}%"))

    # FILTER
    if role:
        query = query.filter(User.role == role)

    # SORT
    if sort == "asc":
        query = query.order_by(User.id.asc())
    else:
        query = query.order_by(User.id.desc())

    users = query.offset(skip).limit(limit).all()

    return users

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), data: dict = Depends(admin_only)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return

