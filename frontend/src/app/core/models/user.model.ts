import { Role } from './role.model';

export interface UserRegister {
  name: string;
  email: string;
  password: string;
  age: number;
  role: Role;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserResponse {
  id: number;
  name: string;
  email: string;
  age: number;
  role: Role;
  profile_image?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserSummary {
  id: number;
  name: string;
  email: string;
  role: Role;
  profile_image?: string;
}
