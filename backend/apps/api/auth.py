from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile, File
from sqlalchemy.engine import create
from sqlalchemy.orm import Session
import os
import uuid

from apps.db.database import get_db
from apps.models.user import User
from apps.schemas.user import UserRegister, UserLogin, UserResponse
from apps.services.auth import hash_password, verify_password
from apps.services.user_service import authenticate_user, create_user
from apps.services.jwt import create_access_token
from apps.core.security import ACCESS_TOKEN_COOKIE, get_current_user
from apps.core.config import settings, Environment
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


@router.post("/login", response_model=UserResponse)
def login(
    response: Response,
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

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=True,
        secure=settings.environment == Environment.prod,
        samesite="lax",
        max_age=settings.jwt_expiry * 60,
        path="/",
    )

    logger.info("Login successful for user id=%s email=%s", user.id, user.email)
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.environment == Environment.prod,
    )
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserResponse)
def fetch_current_user(
    user = Depends(get_current_user)
):
    logger.info("Fetch current user request for email=%s", user.email)
    return user


@router.post("/profile-image", response_model=UserResponse)
async def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Upload or update current user profile avatar image
    """
    os.makedirs("uploads/avatars", exist_ok=True)
    file_ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "png"
    filename = f"user_{user.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = os.path.join("uploads/avatars", filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    user.profile_image = f"/uploads/avatars/{filename}"
    db.commit()
    db.refresh(user)
    logger.info("Updated profile image for user id=%s path=%s", user.id, user.profile_image)
    return user

