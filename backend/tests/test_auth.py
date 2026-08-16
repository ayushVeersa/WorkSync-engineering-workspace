"""
Tests for the authentication endpoints (register, login, me).
"""

import pytest


def register_payload(**kw):
    payload = {
        "name": "Test Admin",
        "age": 30,
        "email": "admin@test.com",
        "password": "secret123",
        "role": "ADMIN",
    }
    payload.update(kw)
    return payload


def login_payload(**kw):
    payload = {
        "email": "admin@test.com",
        "password": "secret123",
    }
    payload.update(kw)
    return payload


def test_register_success(client):
    resp = client.post("/auth/register", json=register_payload())
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "ADMIN"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    client.post("/auth/register", json=register_payload())
    resp = client.post("/auth/register", json=register_payload())
    assert resp.status_code == 400
    assert resp.json()["detail"] == "User already exists"


def test_register_invalid_email(client):
    resp = client.post(
        "/auth/register",
        json=register_payload(email="not-an-email"),
    )
    assert resp.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json=register_payload())
    resp = client.post("/auth/login", json=login_payload())
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "ADMIN"
    assert "access_token" not in data
    set_cookie = resp.headers.get("set-cookie", "")
    assert "worksync_access_token=" in set_cookie
    assert "HttpOnly" in set_cookie


def test_login_cookie_authenticates_me(client):
    client.post("/auth/register", json=register_payload())
    login_resp = client.post("/auth/login", json=login_payload())
    assert login_resp.status_code == 200

    resp = client.get("/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "admin@test.com"


def test_login_wrong_password(client):
    client.post("/auth/register", json=register_payload())
    resp = client.post(
        "/auth/login",
        json=login_payload(password="wrong"),
    )
    assert resp.status_code == 403


def test_login_unknown_email(client):
    resp = client.post(
        "/auth/login",
        json=login_payload(email="nobody@test.com"),
    )
    assert resp.status_code == 400


def test_me_with_valid_token(client, admin_user, admin_token):
    resp = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == admin_user.email
    assert data["role"] == "ADMIN"


def test_me_with_invalid_token(client):
    resp = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401


def test_me_without_token(client):
    # Missing cookie and header should both be rejected.
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_logout_clears_cookie(client):
    client.post("/auth/register", json=register_payload())
    login_resp = client.post("/auth/login", json=login_payload())
    assert login_resp.status_code == 200

    logout_resp = client.post("/auth/logout")
    assert logout_resp.status_code == 200
    set_cookie = logout_resp.headers.get("set-cookie", "")
    assert "worksync_access_token=" in set_cookie
    assert "Max-Age=0" in set_cookie or "expires=" in set_cookie.lower()

    me_resp = client.get("/auth/me")
    assert me_resp.status_code == 401
