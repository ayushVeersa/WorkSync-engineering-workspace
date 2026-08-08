from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.models.user import User
from apps.schemas.user import UserRegister
from apps.services.auth import verify_password, hash_password
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_user_by_email(
        email: str,
        db: Session
    ):
    """
    Fetch user by email if it exists
    """

    user = (
            db.query(User)
            .filter(User.email == email)
            .first()
            )

    if user:
        logger.info("Fetched user by email: %s", email)
    else:
        logger.info("No user found for email: %s", email)

    return user


def create_user(
        user: UserRegister,
        db: Session
) -> User:
    """
    creates user.
    """

    existing = get_user_by_email(user.email, db)
    if existing:
        logger.warning("User registration failed, email already exists: %s", user.email)
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
                )

    db_user = User(
            name=user.name,
            email=user.email,
            password_hash=hash_password(user.password),
            age=user.age,
            role=user.role,
            )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to commit new user %s", user.email)
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="error commiting changes"
                )

    logger.info("Created user with id=%s email=%s role=%s", db_user.id, db_user.email, db_user.role)
    return db_user


def get_all_users(
        db: Session,
    ):
    """
    gets all users from db
    """

    users = (
            db.query(User)
            .all()
            )

    logger.info("Fetched all users, count=%s", len(users))
    return users


def authenticate_user(
        db: Session,
        email: str,
        password: str
        ):
    """
    authenticate user based on their credentials - email and password
    """

    user = get_user_by_email(email, db)
    if not user:
        logger.warning("Authentication failed for unknown email: %s", email)
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Email or Password"
                )

    if not verify_password(password, user.password_hash):
        logger.warning("Authentication failed due to wrong password for email: %s", email)
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Email or Password"
                )

    if not user.is_active:
        logger.warning("Authentication failed, user is inactive: %s", email)
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Email or Password"
                )

    logger.info("User authenticated successfully: %s", email)
    return user
