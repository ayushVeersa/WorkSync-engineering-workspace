from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from apps.db.database import get_db
from apps.models.user import User
from apps.core.security import get_current_user
from apps.schemas.activity import ActivityLogResponse
from apps.services.activity import get_activities

router = APIRouter(
    prefix="/activity",
    tags=["Activity Log"],
)


@router.get("", response_model=List[ActivityLogResponse])
def get_activity_log(
    actor_id: Optional[int] = Query(None, description="Filter by actor/employee ID"),
    action: Optional[str] = Query(None, description="Filter by action name"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (issue, project, etc.)"),
    entity_id: Optional[int] = Query(None, description="Filter by specific entity ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Get audit activity logs with optional filtering and pagination.
    """
    return get_activities(
        db=db,
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit,
    )
