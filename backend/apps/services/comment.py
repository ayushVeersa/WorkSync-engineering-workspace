from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.comment import Comment
from apps.models.issue import Issue
from apps.models.employee import Employee
from apps.models.employee_project import EmployeeProject
from apps.schemas.role import Role
from apps.schemas.comment import (
    CommentCreate,
    CommentUpdate,
)
from apps.core.logging import get_logger

logger = get_logger(__name__)


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
        logger.warning("Comment not found for id=%s", comment_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    logger.info("Fetched comment id=%s", comment_id)
    return comment


def get_issue_comments(
    db: Session,
    issue_id: int,
):
    """
    Fetch comments of an Issue using Issue ID.
    """
    comments = (
        db.query(Comment)
        .filter(Comment.issue_id == issue_id)
        .all()
    )
    logger.info("Fetched comments for issue_id=%s, count=%s", issue_id, len(comments))
    return comments


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
        logger.warning("Issue not found for id=%s while creating comment", issue_id)
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
        logger.warning("Employee %s not part of project %s while creating comment",
                       employee_id, issue.project_id)
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
        logger.exception("Failed to create comment on issue_id=%s", issue_id)
        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    logger.info("Created comment id=%s on issue_id=%s by employee_id=%s",
                comment.id, issue_id, employee_id)
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
        logger.warning("Unauthorized comment update attempt on comment_id=%s by employee_id=%s",
                       comment_id, current_employee.id)
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
        logger.exception("Failed to update comment id=%s", comment_id)
        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    logger.info("Updated comment id=%s by employee_id=%s", comment_id, current_employee.id)
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
        logger.warning("Unauthorized comment delete attempt on comment_id=%s by employee_id=%s",
                       comment_id, current_employee.id)
        raise HTTPException(
            status_code=403,
            detail="Not authorized",
        )

    try:
        db.delete(comment)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to delete comment id=%s", comment_id)
        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    logger.info("Deleted comment id=%s by employee_id=%s", comment_id, current_employee.id)
    return {
        "message": "Comment deleted successfully"
    }
