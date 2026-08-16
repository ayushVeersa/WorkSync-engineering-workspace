import { Role } from './role.model';
import { UserSummary } from './user.model';
import { DepartmentSummary } from './department.model';

export interface EmployeeRegistrationRequest {
  name: string;
  email: string;
  password: string;
  designation: string;
  department_id: number;
  role: Role;
  age?: number;
}

export interface EmployeeUpdate {
  age?: number;
  designation?: string;
}

export interface EmployeeResponse {
  id: number;
  user: UserSummary;
  age: number;
  designation: string;
  department: DepartmentSummary;
  is_active: boolean;
}

export interface BulkImportRowError {
  row: number;
  email?: string;
  error: string;
}

export interface BulkImportResponse {
  total_records: number;
  imported_count: number;
  failed_count: number;
  imported_emails: string[];
  errors: BulkImportRowError[];
}
