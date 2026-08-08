from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.project import Project
from apps.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)


def get_projects(db: Session):
    return db.query(Project).all()


def get_project(db: Session, project_id: int):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {
        "message": "Project deleted successfully"
    }
