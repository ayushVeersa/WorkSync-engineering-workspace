export interface CommentCreate {
  content: string;
}

export interface CommentUpdate {
  content: string;
}

export interface CommentResponse {
  id: number;
  content: string;
  issue_id: number;
  employee_id: number;
  created_at: string;
  updated_at: string;
}
