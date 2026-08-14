from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from apps.db.database import get_db
from apps.models.user import User
from apps.core.security import get_current_user
from apps.schemas.issue import IssueStatus, IssuePriority
from apps.schemas.my_work import MyWorkResponse
from apps.services.my_work import get_my_work_data

router = APIRouter(
    prefix="/me/work",
    tags=["My Work"],
)


@router.get("", response_model=MyWorkResponse)
def get_my_work(
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by task priority"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    search: Optional[str] = Query(None, description="Search by title or description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current employee's personal work dashboard data, including summary cards
    and categorized task sections (Today, Upcoming, Overdue, Recently Completed).
    """
    return get_my_work_data(
        db=db,
        user=current_user,
        status_filter=status,
        priority_filter=priority,
        project_id=project_id,
        search=search,
        skip=skip,
        limit=limit,
    )
