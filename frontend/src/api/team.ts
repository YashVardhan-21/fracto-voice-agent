import api from './client';

export type TeamRole = 'agent' | 'manager' | 'admin';

export interface TeamUser {
  id: number;
  email: string;
  full_name: string;
  role: TeamRole;
  is_admin: boolean;
  is_active: boolean;
  tenant_id: string;
}

export interface TeamUserCreatePayload {
  email: string;
  full_name: string;
  role: TeamRole;
  temporary_password: string;
}

export interface TeamUserUpdatePayload {
  full_name?: string;
  role?: TeamRole;
  is_active?: boolean;
  reset_password?: string;
}

export const getTeamUsers = () => api.get<TeamUser[]>('/team/users').then((r) => r.data);

export const createTeamUser = (payload: TeamUserCreatePayload) =>
  api.post<TeamUser>('/team/users', payload).then((r) => r.data);

export const updateTeamUser = (userId: number, payload: TeamUserUpdatePayload) =>
  api.patch<TeamUser>(`/team/users/${userId}`, payload).then((r) => r.data);
