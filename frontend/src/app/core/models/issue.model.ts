export enum IssueType {
  TASK = 'TASK',
  BUG = 'BUG',
  STORY = 'STORY'
}

export enum IssuePriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export enum IssueStatus {
  BACKLOG = 'BACKLOG',
  TODO = 'TODO',
  IN_PROGRESS = 'IN_PROGRESS',
  REVIEW = 'REVIEW',
  TESTING = 'TESTING',
  DONE = 'DONE'
}

export interface IssueCreate {
  title: string;
  description?: string;
  issue_type?: IssueType;
  priority?: IssuePriority;
  status?: IssueStatus;
  assignee_id: number;
  project_id: number;
  due_date?: string;
}

export interface IssueUpdate {
  title?: string;
  description?: string;
  priority?: IssuePriority;
  status?: IssueStatus;
  assignee_id?: number;
  due_date?: string;
}

export interface IssueResponse {
  id: number;
  title: string;
  description?: string;
  issue_type: IssueType;
  priority: IssuePriority;
  status: IssueStatus;
  project_id: number;
  assignee_id: number;
  reporter_id: number;
  due_date?: string;
  created_at: string;
  updated_at: string;
}
