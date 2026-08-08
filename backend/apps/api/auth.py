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
    return create_user(user, db)


@router.post("/login", response_model=TokenResponse)
def login(
    user_cred: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Verify user credentials and generate JWT token.
    """

    user = authenticate_user(
        db,
        user_cred.email,
        user_cred.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        # data={"sub": str(user.id)}
        data = {"sub": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def fetch_current_user(
    user = Depends(get_current_user)
):
    return user
