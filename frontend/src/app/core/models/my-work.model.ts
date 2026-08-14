import { IssueResponse } from './issue.model';

export interface WorkSummary {
  assigned: number;
  in_progress: number;
  due_soon: number;
  overdue: number;
  completed: number;
}

export interface MyWorkResponse {
  summary: WorkSummary;
  today: IssueResponse[];
  upcoming: IssueResponse[];
  overdue: IssueResponse[];
  recently_completed: IssueResponse[];
}
