export interface DashboardSummary {
  total_employees: number;
  total_departments: number;
  total_projects: number;
  total_issues: number;
  total_comments: number;
  active_projects: number;
}

export interface MyWorkSummary {
  assigned_issues: number;
  completed_issues: number;
  projects: number;
  comments: number;
}

export interface IssueStatusSummary {
  status: string;
  count: number;
}

export interface IssuePrioritySummary {
  priority: string;
  count: number;
}

export interface ProjectOverview {
  id: number;
  name: string;
  members: number;
  issues: number;
}
