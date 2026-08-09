from sqlalchemy.orm import Session

from apps.models.issue import Issue
from apps.services.project import get_project
from apps.schemas.issue import IssueStatus
from apps.schemas.board import BoardResponse, BoardColumn
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_project_board(db: Session, project_id: int) -> BoardResponse:
    """
    Return a Kanban-style board for a project, with issues grouped by status.

    All IssueStatus columns are always returned (even if empty) so the frontend
    can render a consistent board layout.
    """
    project = get_project(db, project_id)

    issues = (
        db.query(Issue)
        .filter(Issue.project_id == project_id)
        .order_by(Issue.created_at)
        .all()
    )

    columns = []
    for status in IssueStatus:
        column_issues = [issue for issue in issues if issue.status == status]
        columns.append(
            BoardColumn(
                status=status,
                issues=column_issues,
            )
        )

    logger.info(
        "Fetched board for project_id=%s, total_issues=%s, columns=%s",
        project_id,
        len(issues),
        len(columns),
    )

    return BoardResponse(
        project_id=project.id,
        project_name=project.name,
        columns=columns,
    )
