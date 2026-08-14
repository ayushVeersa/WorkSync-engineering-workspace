from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class TaskOverviewReport(BaseModel):
    total_tasks: int
    completed: int
    open: int
    in_progress: int
    overdue: int
    completion_rate_percentage: float


class TrendDataPoint(BaseModel):
    date: str
    completed: int
    created: int


class CompletionTrendReport(BaseModel):
    trends: List[TrendDataPoint]


class KeyCount(BaseModel):
    key: str
    count: int


class TaskDistributionReport(BaseModel):
    by_status: List[KeyCount]
    by_priority: List[KeyCount]
    by_type: List[KeyCount]
    by_project: List[KeyCount]


class UserWorkload(BaseModel):
    employee_id: int
    employee_name: str
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int
    workload_status: str  # OPTIMAL, HIGH, OVERLOADED


class TeamWorkloadReport(BaseModel):
    workload: List[UserWorkload]


class CycleTimeReport(BaseModel):
    avg_cycle_time_days: float
    median_cycle_time_days: float
    avg_lead_time_days: float
    by_project: List[Dict[str, Any]] = []
    by_type: List[Dict[str, Any]] = []
