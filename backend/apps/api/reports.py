from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from apps.db.database import get_db
from apps.models.user import User
from apps.core.security import get_current_user
from apps.schemas.reports import (
    TaskOverviewReport,
    CompletionTrendReport,
    TaskDistributionReport,
    TeamWorkloadReport,
    CycleTimeReport,
)
from apps.services.reports import (
    get_task_overview,
    get_completion_trends,
    get_task_distribution,
    get_team_workload,
    get_cycle_time_report,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports & Analytics"],
)


@router.get("/overview", response_model=TaskOverviewReport)
def overview_report(
    project_id: Optional[int] = Query(None),
    assignee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_task_overview(db, project_id=project_id, assignee_id=assignee_id)


@router.get("/trends", response_model=CompletionTrendReport)
def completion_trends_report(
    days: int = Query(14, ge=1, le=90),
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_completion_trends(db, days=days, project_id=project_id)


@router.get("/distribution", response_model=TaskDistributionReport)
def distribution_report(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_task_distribution(db, project_id=project_id)


@router.get("/workload", response_model=TeamWorkloadReport)
def workload_report(
    department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_team_workload(db, department_id=department_id)


@router.get("/cycle-time", response_model=CycleTimeReport)
def cycle_time_report(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_cycle_time_report(db, project_id=project_id)
