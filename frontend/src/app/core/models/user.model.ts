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
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface UserSummary {
  id: number;
  name: string;
  email: string;
  role: Role;
}
