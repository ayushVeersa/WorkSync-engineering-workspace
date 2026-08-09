"""
Mock data population script.

Run from the ``backend`` directory:

    python populate.py            # add data (skips anything that already exists)
    python populate.py --reset    # wipe all tables, then populate fresh

Generates a rich set of mock data across every module so the frontend can be
tested end-to-end without having to create records manually:

    - Departments
    - Users (ADMIN / MANAGER / EMPLOYEE roles)
    - Employees (linked to a user + department)
    - Projects (with various statuses)
    - Employee <-> Project assignments
    - Issues (all types, priorities and statuses)
    - Comments (posted by project members)
    - Attachments (mock files stored on disk under uploads/issues)

All users share the password ``password123`` so you can log in with any of the
seeded emails.
"""

import os
import sys
import uuid
from datetime import datetime, timedelta

# Make sure the backend directory is importable regardless of where the script
# is invoked from.
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from apps.db import base  # noqa: F401  -- registers all models on Base.metadata
from apps.db.database import SessionLocal, Base, engine
from apps.models.user import User
from apps.models.employee import Employee
from apps.models.department import Department
from apps.models.project import Project
from apps.models.employee_project import EmployeeProject
from apps.models.issue import Issue
from apps.models.comment import Comment
from apps.models.attachment import Attachment
from apps.schemas.role import Role
from apps.schemas.project import ProjectStatus
from apps.schemas.issue import IssueType, IssueStatus, IssuePriority
from apps.services.auth import hash_password

PASSWORD = "password123"

UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads", "issues")

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

DEPARTMENTS = [
    ("Engineering", "Builds and maintains the core product and platform."),
    ("Product", "Owns the roadmap, vision and feature prioritisation."),
    ("Design", "Crafts user interfaces and brand experiences."),
    ("Marketing", "Runs campaigns, growth and brand awareness."),
    ("HR", "Handles hiring, onboarding and people operations."),
    ("Sales", "Owns the pipeline, demos and closing deals."),
    ("Operations", "Keeps internal tools and processes running smoothly."),
    ("Support", "Helps customers and resolves reported issues."),
]

# (name, email, role, department_index, age, designation)
PEOPLE = [
    # Admin
    ("Alice Admin", "admin@workspace.dev", Role.ADMIN, 0, 34, "System Administrator"),
    # Managers
    ("Bob Manager", "manager@workspace.dev", Role.MANAGER, 0, 41, "Engineering Manager"),
    ("Carol Lead", "carol@workspace.dev", Role.MANAGER, 1, 38, "Product Lead"),
    ("David Head", "david@workspace.dev", Role.MANAGER, 2, 36, "Design Head"),
    # Engineers
    ("Eve Engineer", "eve@workspace.dev", Role.EMPLOYEE, 0, 26, "Backend Engineer"),
    ("Frank Dev", "frank@workspace.dev", Role.EMPLOYEE, 0, 29, "Frontend Engineer"),
    ("Grace Coder", "grace@workspace.dev", Role.EMPLOYEE, 0, 24, "Full Stack Engineer"),
    ("Hank QA", "hank@workspace.dev", Role.EMPLOYEE, 0, 31, "QA Engineer"),
    ("Ivy DevOps", "ivy@workspace.dev", Role.EMPLOYEE, 0, 33, "DevOps Engineer"),
    # Product / Design
    ("Jack PM", "jack@workspace.dev", Role.EMPLOYEE, 1, 28, "Product Manager"),
    ("Kim Designer", "kim@workspace.dev", Role.EMPLOYEE, 2, 27, "UI/UX Designer"),
    ("Leo UX", "leo@workspace.dev", Role.EMPLOYEE, 2, 25, "UX Researcher"),
    # Marketing / HR / Sales / Ops / Support
    ("Mia Marketer", "mia@workspace.dev", Role.EMPLOYEE, 3, 30, "Growth Marketer"),
    ("Nina HR", "nina@workspace.dev", Role.EMPLOYEE, 4, 35, "HR Business Partner"),
    ("Oscar Sales", "oscar@workspace.dev", Role.EMPLOYEE, 5, 32, "Account Executive"),
    ("Paul Ops", "paul@workspace.dev", Role.EMPLOYEE, 6, 29, "Ops Specialist"),
    ("Quinn Support", "quinn@workspace.dev", Role.EMPLOYEE, 7, 26, "Support Engineer"),
    ("Rita Analyst", "rita@workspace.dev", Role.EMPLOYEE, 6, 30, "Data Analyst"),
]

# (name, description, status, owner_people_index)
PROJECTS = [
    ("Workspace Platform", "Core internal engineering workspace web app.",
     ProjectStatus.ACTIVE, 1),
    ("Mobile App", "Cross-platform companion mobile application.",
     ProjectStatus.ACTIVE, 1),
    ("Design System", "Shared component library and design tokens.",
     ProjectStatus.ACTIVE, 3),
    ("AI Assistant", "Experimental AI-powered assistant for the workspace.",
     ProjectStatus.PLANNING, 2),
    ("Marketing Site Redesign", "Refreshing the public marketing website.",
     ProjectStatus.ACTIVE, 12),
    ("Onboarding Revamp", "Improving the new-hire onboarding experience.",
     ProjectStatus.ON_HOLD, 13),
    ("Legacy Migration", "Migrating legacy services to the new stack.",
     ProjectStatus.COMPLETED, 1),
    ("Sales CRM Integration", "Integrating the CRM with the platform.",
     ProjectStatus.PLANNING, 14),
]

# (project_index, employee_people_index) -- assign employees to projects
ASSIGNMENTS = [
    # Workspace Platform
    (0, 1), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10),
    # Mobile App
    (1, 1), (1, 4), (1, 5), (1, 6), (1, 7),
    # Design System
    (2, 3), (2, 10), (2, 11),
    # AI Assistant
    (3, 2), (3, 9), (3, 4), (3, 11),
    # Marketing Site Redesign
    (4, 12), (4, 10), (4, 6),
    # Onboarding Revamp
    (5, 13), (5, 9), (5, 10),
    # Legacy Migration
    (6, 1), (6, 4), (6, 8), (6, 5),
    # Sales CRM Integration
    (7, 14), (7, 4), (7, 17),
]

# (project_index, title, type, priority, status, assignee_people_index, due_in_days)
# assignee_people_index must be assigned to that project.
ISSUES = [
    # Workspace Platform
    (0, "User authentication flow", IssueType.STORY, IssuePriority.HIGH,
     IssueStatus.DONE, 4, -2),
    (0, "Fix login redirect bug", IssueType.BUG, IssuePriority.CRITICAL,
     IssueStatus.DONE, 5, -6),
    (0, "Implement role-based permissions", IssueType.TASK, IssuePriority.HIGH,
     IssueStatus.IN_PROGRESS, 4, 5),
    (0, "Design dashboard overview", IssueType.TASK, IssuePriority.MEDIUM,
     IssueStatus.REVIEW, 10, 3),
    (0, "Add comment notifications", IssueType.STORY, IssuePriority.LOW,
     IssueStatus.TODO, 6, 12),
    (0, "Optimise database queries", IssueType.TASK, IssuePriority.MEDIUM,
     IssueStatus.BACKLOG, 8, 20),
    (0, "Fix flaky board drag-and-drop", IssueType.BUG, IssuePriority.HIGH,
     IssueStatus.TESTING, 7, 2),
    # Mobile App
    (1, "Set up mobile CI pipeline", IssueType.TASK, IssuePriority.MEDIUM,
     IssueStatus.IN_PROGRESS, 8, 7),
    (1, "Push notification support", IssueType.STORY, IssuePriority.MEDIUM,
     IssueStatus.TODO, 6, 15),
    (1, "Offline mode caching", IssueType.TASK, IssuePriority.LOW,
     IssueStatus.BACKLOG, 5, 25),
    # Design System
    (2, "Create button component spec", IssueType.TASK, IssuePriority.HIGH,
     IssueStatus.DONE, 10, -4),
    (2, "Document colour tokens", IssueType.TASK, IssuePriority.LOW,
     IssueStatus.IN_PROGRESS, 11, 6),
    (2, "Accessibility audit", IssueType.TASK, IssuePriority.HIGH,
     IssueStatus.TODO, 3, 10),
    # AI Assistant
    (3, "Research LLM integration options", IssueType.STORY, IssuePriority.MEDIUM,
     IssueStatus.IN_PROGRESS, 9, 14),
    (3, "Draft prompt templates", IssueType.TASK, IssuePriority.LOW,
     IssueStatus.TODO, 11, 18),
    # Marketing Site Redesign
    (4, "Wireframe new homepage", IssueType.TASK, IssuePriority.MEDIUM,
     IssueStatus.REVIEW, 10, 4),
    (4, "Copy for product pages", IssueType.TASK, IssuePriority.LOW,
     IssueStatus.TODO, 12, 9),
    (4, "SEO meta improvements", IssueType.BUG, IssuePriority.MEDIUM,
     IssueStatus.IN_PROGRESS, 12, 6),
    # Onboarding Revamp
    (5, "Map current onboarding flow", IssueType.TASK, IssuePriority.MEDIUM,
     IssueStatus.BACKLOG, 9, 20),
    (5, "Interview new hires for pain points", IssueType.STORY,
     IssuePriority.MEDIUM, IssueStatus.TODO, 13, 22),
    # Legacy Migration
    (6, "Migrate auth service", IssueType.TASK, IssuePriority.HIGH,
     IssueStatus.DONE, 4, -15),
    (6, "Migrate reporting service", IssueType.TASK, IssuePriority.MEDIUM,
     IssueStatus.DONE, 8, -10),
    (6, "Decommission old scheduler", IssueType.TASK, IssuePriority.LOW,
     IssueStatus.DONE, 8, -3),
    # Sales CRM Integration
    (7, "Design CRM sync schema", IssueType.TASK, IssuePriority.MEDIUM,
     IssueStatus.BACKLOG, 17, 30),
    (7, "OAuth handshake with CRM", IssueType.STORY, IssuePriority.HIGH,
     IssueStatus.BACKLOG, 4, 35),
]

# (issue_index, comment_employee_people_index, content)
# comment authors must be assigned to the issue's project.
COMMENTS = [
    (0, 4, "Auth flow is live and verified in staging."),
    (0, 5, "Added coverage for the new session handling."),
    (1, 5, "Reproduced locally, root cause was a stale cookie."),
    (1, 7, "Reqression tests added and passing."),
    (2, 4, "Permission middleware is wired up, needs final review."),
    (2, 1, "Looking good, please document the new roles."),
    (3, 10, "Dashboard mockups attached for reference."),
    (3, 0, "Can we add a yearly comparisons chart?"),
    (4, 6, "Notification service is scoped, ready to implement."),
    (7, 8, "CI pipeline green on the mobile branch."),
    (10, 10, "Button spec approved by design."),
    (13, 9, "Shortlisted three providers, comparing pricing."),
    (15, 10, "First wireframe iteration is uploaded."),
    (21, 4, "Migration completed, service decommissioned on time."),
]

# (issue_index, uploader_people_index, original_name, content_type, size)
# uploader must be assigned to the issue's project.
ATTACHMENTS = [
    (0, 4, "auth-flow-diagram.png", "image/png", 204800),
    (3, 10, "dashboard-wireframes.png", "image/png", 512000),
    (15, 10, "homepage-wireframe.png", "image/png", 409600),
    (13, 9, "llm-provider-comparison.md", "text/markdown", 8192),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def wipe_all(db):
    """Delete every row in dependency-safe order."""
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    print("Cleared all existing data.")


def ensure_departments(db):
    dept_rows = {}
    for name, desc in DEPARTMENTS:
        existing = db.query(Department).filter(Department.name == name).first()
        if existing:
            dept_rows[name] = existing
            continue
        dept = Department(name=name, description=desc)
        db.add(dept)
        db.flush()
        dept_rows[name] = dept
        print(f"  + Department: {name}")
    db.commit()
    return dept_rows


def ensure_people(db, dept_rows):
    """Create users + employees. Returns list of employee objects."""
    employees = []
    for name, email, role, dept_idx, age, designation in PEOPLE:
        dept_name = DEPARTMENTS[dept_idx][0]
        dept = dept_rows[dept_name]

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            user = User(
                name=name,
                email=email,
                password_hash=hash_password(PASSWORD),
                age=age,
                role=role,
                is_active=True,
            )
            db.add(user)
            db.flush()
            print(f"  + User: {email} ({role.value})")

        employee = db.query(Employee).filter(Employee.user_id == user.id).first()
        if employee is None:
            employee = Employee(
                user_id=user.id,
                department_id=dept.id,
                age=age,
                designation=designation,
                is_active=True,
            )
            db.add(employee)
            db.flush()
            print(f"  + Employee: {name} -> {dept_name}")
        employees.append(employee)

    db.commit()
    return employees


def ensure_projects(db, employees):
    """Create projects. Returns list of project objects."""
    projects = []
    now = datetime.now()
    for name, desc, status, owner_idx in PROJECTS:
        owner = employees[owner_idx]
        existing = db.query(Project).filter(Project.name == name).first()
        if existing:
            projects.append(existing)
            continue
        project = Project(
            name=name,
            description=desc,
            status=status,
            owner_id=owner.id,
            created_at=now,
            updated_at=now,
        )
        db.add(project)
        db.flush()
        print(f"  + Project: {name} ({status.value}) owner={owner.user.name}")
        projects.append(project)
    db.commit()
    return projects


def ensure_assignments(db, employees, projects):
    count = 0
    for proj_idx, emp_idx in ASSIGNMENTS:
        project = projects[proj_idx]
        employee = employees[emp_idx]
        existing = (
            db.query(EmployeeProject)
            .filter(
                EmployeeProject.employee_id == employee.id,
                EmployeeProject.project_id == project.id,
            )
            .first()
        )
        if existing:
            continue
        db.add(EmployeeProject(employee_id=employee.id, project_id=project.id))
        count += 1
    db.commit()
    if count:
        print(f"  + Assigned {count} employee(s) to projects.")


def ensure_issues(db, projects, employees):
    """Create issues. Returns list of issue objects."""
    issues = []
    now = datetime.now()
    for (
        proj_idx, title, i_type, priority, status, assignee_idx, due_in_days
    ) in ISSUES:
        project = projects[proj_idx]
        assignee = employees[assignee_idx]
        reporter = project.owner
        due_date = now + timedelta(days=due_in_days) if due_in_days is not None else None

        existing = (
            db.query(Issue)
            .filter(
                Issue.title == title,
                Issue.project_id == project.id,
            )
            .first()
        )
        if existing:
            issues.append(existing)
            continue

        issue = Issue(
            title=title,
            description=f"Mock issue: {title} for project {project.name}.",
            issue_type=i_type,
            priority=priority,
            status=status,
            project_id=project.id,
            assignee_id=assignee.id,
            reporter_id=reporter.id,
            due_date=due_date,
            created_at=now,
            updated_at=now,
        )
        db.add(issue)
        db.flush()
        print(f"  + Issue: {title} [{status.value}] -> {project.name}")
        issues.append(issue)
    db.commit()
    return issues


def ensure_comments(db, issues, employees):
    count = 0
    for issue_idx, emp_idx, content in COMMENTS:
        issue = issues[issue_idx]
        employee = employees[emp_idx]
        existing = (
            db.query(Comment)
            .filter(
                Comment.issue_id == issue.id,
                Comment.employee_id == employee.id,
                Comment.content == content,
            )
            .first()
        )
        if existing:
            continue
        db.add(Comment(
            content=content,
            issue_id=issue.id,
            employee_id=employee.id,
        ))
        count += 1
    db.commit()
    if count:
        print(f"  + {count} comment(s) added.")


def ensure_attachments(db, issues, employees, reset=False):
    """Create mock attachment records + placeholder files on disk."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    count = 0
    for issue_idx, emp_idx, original_name, content_type, size in ATTACHMENTS:
        issue = issues[issue_idx]
        employee = employees[emp_idx]

        existing = (
            db.query(Attachment)
            .filter(
                Attachment.issue_id == issue.id,
                Attachment.original_name == original_name,
            )
            .first()
        )
        if existing:
            continue

        stored_name = f"{uuid.uuid4()}{os.path.splitext(original_name)[1]}"
        file_path = os.path.join(UPLOAD_DIR, stored_name)

        # Write a small placeholder file so the static server can serve it.
        with open(file_path, "wb") as fh:
            fh.write(b"mock attachment content\n" * max(1, size // 32))

        db.add(Attachment(
            original_name=original_name,
            stored_name=stored_name,
            file_path=file_path,
            content_type=content_type,
            file_size=size,
            issue_id=issue.id,
            uploaded_by=employee.id,
        ))
        count += 1
        print(f"  + Attachment: {original_name} on issue #{issue.id}")
    db.commit()
    if count == 0:
        print("  • No new attachments needed.")


def summary(db):
    print("\n========== SUMMARY ==========")
    print(f"Departments : {db.query(Department).count()}")
    print(f"Users       : {db.query(User).count()}")
    print(f"Employees   : {db.query(Employee).count()}")
    print(f"Projects    : {db.query(Project).count()}")
    print(f"Assignments : {db.query(EmployeeProject).count()}")
    print(f"Issues      : {db.query(Issue).count()}")
    print(f"Comments    : {db.query(Comment).count()}")
    print(f"Attachments : {db.query(Attachment).count()}")
    print("==============================")
    print(f"\nAll seeded users use the password: {PASSWORD}")
    print("Admin login  -> admin@workspace.dev")
    print("Manager login-> manager@workspace.dev")
    print("Employee     -> e.g. eve@workspace.dev, frank@workspace.dev, ...")


def main():
    reset = "--reset" in sys.argv
    db = SessionLocal()
    try:
        # Ensure schema exists (idempotent; safe to run even if already migrated).
        Base.metadata.create_all(bind=engine)

        if reset:
            wipe_all(db)

        print("Populating departments...")
        dept_rows = ensure_departments(db)

        print("Populating users & employees...")
        employees = ensure_people(db, dept_rows)

        print("Populating projects...")
        projects = ensure_projects(db, employees)

        print("Assigning employees to projects...")
        ensure_assignments(db, employees, projects)

        print("Populating issues...")
        issues = ensure_issues(db, projects, employees)

        print("Populating comments...")
        ensure_comments(db, issues, employees)

        print("Populating attachments...")
        ensure_attachments(db, issues, employees, reset=reset)

        summary(db)

    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(f"\nERROR: {exc}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
