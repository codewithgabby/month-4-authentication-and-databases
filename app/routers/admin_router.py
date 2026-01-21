from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import admin_only  # admin_only should raise 403 if not admin
from app.models.user_model import User
from app.schemas.user_schema import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", summary="Admin: site statistics")
def get_stats(_admin: dict = Depends(admin_only), db: Session = Depends(get_db)):
    """
    Return basic admin statistics. _admin dependency enforces that the caller is an admin.
    """
    total = db.query(User).count()
    return {"total_users": total}


@router.get("/users", response_model=List[UserResponse], summary="Admin: list users")
def list_users(
    _admin: dict = Depends(admin_only),
    db: Session = Depends(get_db),
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


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Admin: delete user")
def delete_user(user_id: int, _admin: dict = Depends(admin_only), db: Session = Depends(get_db)):
    """
    Delete a user by id. Admin only.
    Consider soft-delete / audit log in production.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return
