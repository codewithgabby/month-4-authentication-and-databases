import logging
from app.core.rate_limiter import limiter

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


from app.database import get_db
from app.models.user_model import User
from app.models.refresh_token_model import RefreshToken
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.token_schema import TokenPair, TokenOut
from app.utils.hash import hash_password, verify_password
from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)
from app.dependencies import get_current_user

logger = logging.getLogger("app")

router = APIRouter(prefix="/auth", tags=["Auth"])

# REGISTER
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):

    logger.info(
        "Registration attempt received",
        extra={"email": user_in.email},
    )

    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        logger.warning(
            "Registration failed - email already exists",
            extra={"email": user_in.email},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        role="user",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(
        "User registered successfully",
        extra={"user_id": user.id},
    )

    return user

# LOGIN (SET COOKIES HERE)
@router.post("/login", response_model=TokenPair, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    logger.info(
        "Login attempt received",
        extra={"email": form_data.username},
    )

    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(
                "Failed login attempt",
                extra={"email": form_data.username},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = create_access_token(
            {"user_id": user.id, "role": user.role}
        )
        refresh_token = create_refresh_token(
            {"user_id": user.id}
        )

        # Store refresh token in DB
        now = datetime.utcnow()
        expires_at = now + timedelta(days=7)

        db_rt = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=expires_at,
            revoked=False,
        )
        db.add(db_rt)
        db.commit()

        # Set secure cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # set True in production (HTTPS)
            samesite="lax",
            max_age=30 * 60,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # set True in production
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
        )

        logger.info(
            "User login successful",
            extra={"user_id": user.id},
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    except HTTPException:
        raise

    except Exception:
        logger.error(
            "Unexpected error during login",
            exc_info=True,
        )
        raise


# REFRESH TOKEN (COOKIE OR BODY)
@router.post("/refresh", response_model=TokenOut, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def refresh(
    request: Request,
    response: Response,
    payload: dict | None = None,
    db: Session = Depends(get_db),
):
    logger.info("Refresh token request received")

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token and payload:
        refresh_token = payload.get("refresh_token")

    if not refresh_token:
        logger.warning("Refresh token missing")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required",
        )

    token_payload = verify_refresh_token(refresh_token)
    if not token_payload:
        logger.warning("Invalid refresh token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()

    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        logger.warning("Revoked or expired refresh token used")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or expired",
        )

    user = db.query(User).filter(
        User.id == token_payload.get("user_id")
    ).first()

    if not user:
        logger.error("Refresh token valid but user not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_access = create_access_token(
        {"user_id": user.id, "role": user.role}
    )

    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 60,
    )

    logger.info(
        "Access token refreshed successfully",
        extra={"user_id": user.id},
    )

    return {
        "access_token": new_access,
        "token_type": "bearer",
    }



# LOGOUT (CLEAR COOKIES)
@router.post("/logout", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
def logout(
    request: Request,
    response: Response,
    payload: dict | None = None,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    logger.info(
        "Logout request received",
        extra={"user_id": current.get("user_id")},
    )

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token and payload:
        refresh_token = payload.get("refresh_token")

    if refresh_token:
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        if db_token:
            db_token.revoked = True
            db.commit()
            logger.info(
                "Refresh token revoked during logout",
                extra={"user_id": db_token.user_id},
            )

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    logger.info(
        "User logged out successfully",
        extra={"user_id": current.get("user_id")},
    )

    return {"detail": "Logged out"}