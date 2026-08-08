from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.engine import create
from sqlalchemy.orm import Session

from apps.db.database import get_db
from apps.models.user import User
from apps.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from apps.services.auth import hash_password, verify_password
from apps.services.user_service import authenticate_user, create_user
from apps.services.jwt import create_access_token
from apps.core.security import get_current_user
from apps.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
        prefix="/auth",
        tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
    ) -> User:
    """
    Register once(for admin registration)
    """
    logger.info("Register user request received for email=%s", user.email)
    result = create_user(user, db)
    logger.info("User registered successfully, id=%s", result.id)
    return result


@router.post("/login", response_model=TokenResponse)
def login(
    user_cred: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Verify user credentials and generate JWT token.
    """
    logger.info("Login request received for email=%s", user_cred.email)

    user = authenticate_user(
        db,
        user_cred.email,
        user_cred.password
    )

    if not user:
        logger.warning("Login failed for email=%s", user_cred.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        # data={"sub": str(user.id)}
        data = {"sub": user.email}
    )

    logger.info("Login successful for user id=%s email=%s", user.id, user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def fetch_current_user(
    user = Depends(get_current_user)
):
    logger.info("Fetch current user request for email=%s", user.email)
    return user
