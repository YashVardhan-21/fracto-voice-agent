import api from './client';
import type { User } from '../types';

export interface LoginResponse {
  access_token: string;
  user_id: number;
  email: string;
  full_name: string;
  role: string;
}

export const login = (email: string, password: string) =>
  api.post<LoginResponse>('/auth/login', { email, password }).then((r) => r.data);
