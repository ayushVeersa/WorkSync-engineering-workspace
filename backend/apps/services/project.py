from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.project import Project
from apps.models.employee_project import EmployeeProject
from apps.models.user import User
from apps.schemas.role import Role
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
    assigned_to: str | None = None,
    current_user: User = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(Project)

    if current_user and current_user.role == Role.EMPLOYEE:
        query = query.join(
            EmployeeProject,
            EmployeeProject.project_id == Project.id,
        ).filter(
            EmployeeProject.employee_id == current_user.employee.id
        )
    
    elif assigned_to:
        if assigned_to.lower() == "me" and current_user:
            target_id = current_user.employee.id
        else:
            try:
                target_id = int(assigned_to)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="assigned_to must be an integer or 'me'"
                )
        
        query = query.filter(Project.owner_id == target_id)

    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))

    if status is not None:
        query = query.filter(Project.status == status)

    projects = query.offset(skip).limit(limit).all()
    
    logger.info(
        "Fetched projects, count=%s, search=%s, status=%s, assigned_to=%s, skip=%s, limit=%s",
        len(projects), search, status, assigned_to, skip, limit,
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
    except Exception as e:
        db.rollback()
        logger.exception("Failed to create project %s: %s", project.name, e)
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
