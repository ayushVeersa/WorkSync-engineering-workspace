from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.comment import Comment
from apps.models.issue import Issue
from apps.models.employee import Employee
from apps.models.employee_project import EmployeeProject
from backend.apps.schemas.role import Role
from apps.schemas.comment import (
    CommentCreate,
    CommentUpdate,
)


def get_comment(
    db: Session,
    comment_id: int,
) -> Comment:
    """
    Fetch comment using comment ID.
    """

    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    return comment


def get_issue_comments(
    db: Session,
    issue_id: int,
):
    """
    Fetch comments of an Issue using Issue ID.
    """
    return (
        db.query(Comment)
        .filter(Comment.issue_id == issue_id)
        .all()
    )


def create_comment(
    db: Session,
    issue_id: int,
    payload: CommentCreate,
    employee_id: int,
):
    """
    Add/Create comments on a particular issues.
    """
    issue = (
        db.query(Issue)
        .filter(Issue.id == issue_id)
        .first()
    )

    if not issue:
        raise HTTPException(
            status_code=404,
            detail="Issue not found",
        )

    assignment = (
        db.query(EmployeeProject)
        .filter(
            EmployeeProject.employee_id == employee_id,
            EmployeeProject.project_id == issue.project_id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=403,
            detail="Employee is not part of this project",
        )

    comment = Comment(
        content=payload.content,
        issue_id=issue_id,
        employee_id=employee_id,
    )

    try:
        db.add(comment)
        db.commit()
        db.refresh(comment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    return comment


def update_comment(
    db: Session,
    comment_id: int,
    payload: CommentUpdate,
    current_employee: Employee,
):
    """
    Update comments using comment ID.
    """
    comment = get_comment(db, comment_id)

    if (
        comment.employee_id != current_employee.id
        and current_employee.role != Role.ADMIN
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized",
        )

    comment.content = payload.content

    try:
        db.commit()
        db.refresh(comment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    return comment


def delete_comment(
    db: Session,
    comment_id: int,
    current_employee: Employee,
):
    """
    Delete Comments using comment ID.
    """
    comment = get_comment(db, comment_id)

    if (
        comment.employee_id != current_employee.id
        and current_employee.role != Role.ADMIN
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized",
        )

    try:
        db.delete(comment)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    return {
        "message": "Comment deleted successfully"
    }