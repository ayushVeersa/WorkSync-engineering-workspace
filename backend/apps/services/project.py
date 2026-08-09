from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.project import Project
from apps.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectStatus,
)
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_projects(
    db: Session,
    search: str | None = None,
    status: ProjectStatus | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(Project)

    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))

    if status is not None:
        query = query.filter(Project.status == status)

    projects = query.offset(skip).limit(limit).all()
    logger.info(
        "Fetched all projects, count=%s, search=%s, status=%s, skip=%s, limit=%s",
        len(projects),
        search,
        status,
        skip,
        limit,
    )
    return projects


def get_project(db: Session, project_id: int):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        logger.warning("Project not found for id=%s", project_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    logger.info("Fetched project id=%s", project_id)
    return project


def create_project(
    db: Session,
    project: ProjectCreate,
    owner_id: int,
):
    db_project = Project(
        name=project.name,
        description=project.description,
        status=project.status,
        owner_id=owner_id,
    )

    try:
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
    except Exception:
        db.rollback()
        logger.exception("Failed to create project %s", project.name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    logger.info("Created project id=%s name=%s owner_id=%s", db_project.id, db_project.name, owner_id)
    return db_project


def update_project(
    db: Session,
    project_id: int,
    project_update: ProjectUpdate,
):
    db_project = get_project(db, project_id)

    update_data = project_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_project, key, value)

    try:
        db.commit()
        db.refresh(db_project)
    except Exception:
        db.rollback()
        logger.exception("Failed to update project id=%s", project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    logger.info("Updated project id=%s with fields=%s", project_id, list(update_data.keys()))
    return db_project


def delete_project(
    db: Session,
    project_id: int,
):
    db_project = get_project(db, project_id)

    try:
        db.delete(db_project)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to delete project id=%s", project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    logger.info("Deleted project id=%s", project_id)
    return {
        "message": "Project deleted successfully"
    }
