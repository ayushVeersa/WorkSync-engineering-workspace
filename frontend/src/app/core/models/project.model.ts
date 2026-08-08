export enum ProjectStatus {
  PLANNING = 'PLANNING',
  ACTIVE = 'ACTIVE',
  COMPLETED = 'COMPLETED',
  ON_HOLD = 'ON_HOLD'
}

export interface ProjectCreate {
  name: string;
  description?: string;
  status?: ProjectStatus;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  status?: ProjectStatus;
}

export interface ProjectResponse {
  id: number;
  name: string;
  description?: string;
  status: ProjectStatus;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface AssignmentResponse {
  message?: string;
  status?: string;
}
