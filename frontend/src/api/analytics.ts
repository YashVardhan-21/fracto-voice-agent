import api from './client';
import type { DashboardStats } from '../types';

export const getDashboardStats = () =>
  api.get<DashboardStats>('/analytics/dashboard').then((r) => r.data);
