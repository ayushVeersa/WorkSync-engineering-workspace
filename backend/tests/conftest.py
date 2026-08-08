"""
Shared pytest fixtures and configuration for the FastAPI test suite.

The test suite uses an in-memory SQLite database (with StaticPool) so that
every test session gets an isolated, fast database. The FastAPI dependency
``get_db`` is overridden to use this test session.
"""

import os

# Must be set before importing the application modules so that the
# Settings singleton picks up the test database URL.
os.environ.setdefault("DB_URL", "sqlite:///./test_dev.db")
os.environ.setdefault("JWT_SECRET", "test-secret-key")
os.environ.setdefault("JWT_EXPIRY", "30")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.db.database import Base, get_db
from apps.db import base  # noqa: F401  (registers all models on Base.metadata)
from apps.main import app
from apps.schemas.role import Role

# ---------------------------------------------------------------
# Test database
# ---------------------------------------------------------------
engine = create_engine(
    "sqlite:///./test_dev.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once per test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _clean_db():
    """Truncate all tables between tests to keep them isolated."""
    db = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


@pytest.fixture
def db():
    """Provide a clean SQLAlchemy session for direct service tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """Provide a FastAPI TestClient with the overridden DB dependency."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------
# Data factories
# ---------------------------------------------------------------
from apps.models.user import User
from apps.models.department import Department
from apps.models.employee import Employee
from apps.models.project import Project
from apps.models.issue import Issue
from apps.models.employee_project import EmployeeProject
from apps.schemas.project import ProjectStatus
from apps.schemas.issue import IssueType, IssueStatus, IssuePriority
from apps.services.auth import hash_password
from apps.services.jwt import create_access_token


def _make_user(
    db,
    name="Test User",
    email="user@test.com",
    password="secret123",
    role=Role.EMPLOYEE,
    is_active=True,
):
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        age=22,
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_employee(db, user, department_id, designation="Engineer", age=25):
    employee = Employee(
        user_id=user.id,
        department_id=department_id,
        designation=designation,
        age=age,
        is_active=True,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def _make_department(db, name="Engineering", description="Eng dept"):
    dept = Department(name=name, description=description)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def _make_project(db, name, owner_employee_id, status=ProjectStatus.PLANNING):
    project = Project(
        name=name,
        description="Project description",
        status=status,
        owner_id=owner_employee_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def _assign(db, employee_id, project_id):
    assignment = EmployeeProject(
        employee_id=employee_id,
        project_id=project_id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def _make_issue(
    db,
    title,
    project_id,
    assignee_id,
    reporter_id,
    status=IssueStatus.TODO,
    priority=IssuePriority.MEDIUM,
    issue_type=IssueType.TASK,
):
    issue = Issue(
        title=title,
        description="Issue description",
        issue_type=issue_type,
        priority=priority,
        status=status,
        project_id=project_id,
        assignee_id=assignee_id,
        reporter_id=reporter_id,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def _user_token(user, db):
    return create_access_token(data={"sub": user.email})


@pytest.fixture
def make_user(db):
    return lambda **kw: _make_user(db, **kw)


@pytest.fixture
def make_employee(db):
    return lambda user, department_id, **kw: _make_employee(
        db, user, department_id, **kw
    )


@pytest.fixture
def make_department(db):
    return lambda **kw: _make_department(db, **kw)


@pytest.fixture
def make_project(db):
    return lambda name, owner_employee_id, **kw: _make_project(
        db, name, owner_employee_id, **kw
    )


@pytest.fixture
def assign(db):
    return lambda employee_id, project_id: _assign(db, employee_id, project_id)


@pytest.fixture
def make_issue(db):
    return lambda **kw: _make_issue(db, **kw)


@pytest.fixture
def auth_headers(db):
    """Return a helper generating auth headers for a given role."""
    def _headers(role=Role.ADMIN, **kw):
        u = _make_user(db, role=role, **kw)
        t = _user_token(u, db)
        return u, {"Authorization": f"Bearer {t}"}
    return _headers


@pytest.fixture
def make_user_with_token(db):
    """Return a helper that creates a user and returns (user, auth_headers)."""
    def _make(role=Role.ADMIN, **kw):
        u = _make_user(db, role=role, **kw)
        t = _user_token(u, db)
        return u, {"Authorization": f"Bearer {t}"}
    return _make


@pytest.fixture
def admin_user(db):
    return _make_user(db, name="Admin", email="admin@test.com", role=Role.ADMIN)


@pytest.fixture
def manager_user(db):
    return _make_user(db, name="Manager", email="manager@test.com", role=Role.MANAGER)


@pytest.fixture
def employee_user(db):
    return _make_user(db, name="Employee", email="employee@test.com", role=Role.EMPLOYEE)


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(data={"sub": admin_user.email})


@pytest.fixture
def manager_token(manager_user):
    return create_access_token(data={"sub": manager_user.email})


@pytest.fixture
def employee_token(employee_user):
    return create_access_token(data={"sub": employee_user.email})
