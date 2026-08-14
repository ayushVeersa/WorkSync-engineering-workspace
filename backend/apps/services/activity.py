import json
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any

from apps.models.activity import ActivityLog
from apps.models.employee import Employee
from apps.schemas.activity import ActivityLogResponse
from apps.core.logging import get_logger

logger = get_logger(__name__)


def record_activity(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: int,
    actor_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> ActivityLog:
    """
    Append-only recording of system and user activity events.
    """
    metadata_str = json.dumps(metadata) if metadata else None

    log = ActivityLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata_str,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    logger.info(
        "Recorded activity action=%s entity_type=%s entity_id=%s actor_id=%s",
        action,
        entity_type,
        entity_id,
        actor_id,
    )
    return log


def get_activities(
    db: Session,
    actor_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[ActivityLogResponse]:
    """
    Fetch activity logs with optional filtering and pagination.
    """
    query = db.query(ActivityLog)

    if actor_id is not None:
        query = query.filter(ActivityLog.actor_id == actor_id)

    if action is not None:
        query = query.filter(ActivityLog.action == action)

    if entity_type is not None:
        query = query.filter(ActivityLog.entity_type == entity_type)

    if entity_id is not None:
        query = query.filter(ActivityLog.entity_id == entity_id)

    query = query.order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())

    logs = query.offset(skip).limit(limit).all()

    result = []
    for log in logs:
        actor_name = None
        if log.actor and log.actor.user:
            actor_name = log.actor.user.name

        meta = None
        if log.metadata_json:
            try:
                meta = json.loads(log.metadata_json)
            except Exception:
                meta = None

        result.append(
            ActivityLogResponse(
                id=log.id,
                actor_id=log.actor_id,
                actor_name=actor_name,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                metadata=meta,
                created_at=log.created_at,
            )
        )

    return result
