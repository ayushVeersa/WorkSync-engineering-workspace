export interface TaskOverviewReport {
  total_tasks: number;
  completed: number;
  open: number;
  in_progress: number;
  overdue: number;
  completion_rate_percentage: number;
}

export interface TrendDataPoint {
  date: string;
  completed: number;
  created: number;
}

export interface CompletionTrendReport {
  trends: TrendDataPoint[];
}

export interface KeyCount {
  key: string;
  count: number;
}

export interface TaskDistributionReport {
  by_status: KeyCount[];
  by_priority: KeyCount[];
  by_type: KeyCount[];
  by_project: KeyCount[];
}

export interface UserWorkload {
  employee_id: number;
  employee_name: string;
  active_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  workload_status: string; // OPTIMAL | HIGH | OVERLOADED
}

export interface TeamWorkloadReport {
  workload: UserWorkload[];
}

export interface CycleTimeReport {
  avg_cycle_time_days: number;
  median_cycle_time_days: number;
  avg_lead_time_days: number;
  by_project: any[];
  by_type: any[];
}
