"""
Unit tests for low-level service helpers: password hashing/verification,
JWT creation/decoding, and user service functions.
"""

import pytest
from fastapi import HTTPException
from jose import jwt as jose_jwt

from apps.core.config import settings
from apps.schemas.user import UserRegister
from apps.schemas.role import Role
from apps.services.auth import hash_password, verify_password
from apps.services.jwt import create_access_token, decode_access_token
from apps.services import user_service


# --------------------------- Password hashing ---------------------------


def test_hash_and_verify_password():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_hash_is_salted():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2  # bcrypt salts produce different hashes


# --------------------------- JWT ---------------------------


def test_create_and_decode_token():
    token = create_access_token(data={"sub": "user@test.com"})
    decoded = decode_access_token(token)
    assert decoded["sub"] == "user@test.com"
    assert "exp" in decoded


def test_decode_token_matches_secret():
    payload = {"sub": "someone@test.com"}
    token = create_access_token(data=payload)
    decoded = jose_jwt.decode(token, settings.jwt_secret, algorithms=settings.algorithm)
    assert decoded["sub"] == "someone@test.com"


# --------------------------- User service ---------------------------


def test_create_user(db):
    user = user_service.create_user(
        UserRegister(
            name="Test",
            email="test@test.com",
            password="secret123",
            age=25,
            role=Role.EMPLOYEE,
        ),
        db,
    )
    assert user.id
    assert user.email == "test@test.com"
    assert user.password_hash != "secret123"


def test_create_user_duplicate(db):
    reg = UserRegister(
        name="Test",
        email="test@test.com",
        password="secret123",
        age=25,
        role=Role.EMPLOYEE,
    )
    user_service.create_user(reg, db)
    with pytest.raises(HTTPException) as exc:
        user_service.create_user(reg, db)
    assert exc.value.status_code == 400


def test_get_user_by_email(db, make_user):
    user = make_user(email="findme@test.com")
    found = user_service.get_user_by_email("findme@test.com", db)
    assert found.id == user.id
    assert user_service.get_user_by_email("missing@test.com", db) is None


def test_get_all_users(db, make_user):
    make_user(email="a@test.com")
    make_user(email="b@test.com")
    assert len(user_service.get_all_users(db)) == 2


def test_authenticate_user_success(db, make_user):
    make_user(email="auth@test.com", password="secret123")
    user = user_service.authenticate_user(db, "auth@test.com", "secret123")
    assert user.email == "auth@test.com"


def test_authenticate_user_unknown_email(db):
    with pytest.raises(HTTPException) as exc:
        user_service.authenticate_user(db, "nobody@test.com", "whatever")
    assert exc.value.status_code == 400


def test_authenticate_user_wrong_password(db, make_user):
    make_user(email="auth@test.com", password="secret123")
    with pytest.raises(HTTPException) as exc:
        user_service.authenticate_user(db, "auth@test.com", "wrongpass")
    assert exc.value.status_code == 403


def test_authenticate_user_inactive(db, make_user):
    make_user(email="inactive@test.com", password="secret123", is_active=False)
    with pytest.raises(HTTPException) as exc:
        user_service.authenticate_user(db, "inactive@test.com", "secret123")
    assert exc.value.status_code == 401
