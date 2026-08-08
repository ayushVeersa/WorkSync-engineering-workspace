export interface DepartmentSummary {
  id: number;
  name: string;
  description: string;
}

export interface DepartmentRequest {
  name: string;
  description: string;
}

export interface DepartmentUpdate {
  name?: string;
  description?: string;
}

export interface DepartmentResponse {
  id: number;
  name: string;
  description: string;
}
