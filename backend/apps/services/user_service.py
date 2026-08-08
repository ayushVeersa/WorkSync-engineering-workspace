from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.models.user import User
from apps.schemas.user import UserRegister
from apps.services.auth import verify_password, hash_password


def get_user_by_email(
        email: str,
        db: Session
    ):
    """
    Fetch user by email if it exists
    """

    return (
            db.query(User)
            .filter(User.email==email)
            .first()
            )



def create_user(
        user: UserRegister,
        db: Session
) -> User:
    """
    creates user.
    """

    existing = get_user_by_email(user.email, db)
    if existing:
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
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="error commiting changes"
                )

    return db_user


def get_all_users(
        db: Session,
    ):
    """
    gets all users from db
    """

    return (
            db.query(User)
            .all()
            )



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
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Email or Password"
                )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Email or Password"
                )

    if not user.is_active:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Email or Password"
                )

    return user
