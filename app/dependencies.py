# External imports
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# Local imports
from app.database import get_db
from app.auth.oauth2_scheme import oauth2_scheme
from app.auth.jwt_handler import verify_access_token

from typing import Dict

# Dependency to get the current user based on the access token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Dict:
    """
    Verifies access token, loads user from DB and returns a dict:
    {"user": <User object>, "role": "<role>"}
    """
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    user_id = payload.get("user_id")
    role = payload.get("role")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload", headers={"WWW-Authenticate": "Bearer"})
    # import inside function to avoid circular imports
    from app.models.user_model import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"user": user, "role": role}

def get_current_active_user(data: Dict = Depends(get_current_user)):
    user = data["user"]
    if not getattr(user, "is_active", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return data

def admin_only(data: Dict = Depends(get_current_user)):
    role = data.get("role")
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return data

