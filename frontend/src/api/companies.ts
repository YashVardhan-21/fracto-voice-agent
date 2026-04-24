import api from './client';
import type { Company } from '../types';

export const getCompanies = (params?: { status?: string; search?: string }) =>
  api.get<Company[]>('/companies/', { params }).then((r) => r.data);

export const getTopLeads = (params?: { search?: string; limit?: number }) =>
  api.get<Company[]>('/companies/top-leads', { params }).then((r) => r.data);

export const createCompany = (data: Partial<Company>) =>
  api.post<Company>('/companies/', data).then((r) => r.data);

export const updateCompany = (id: number, data: Partial<Company>) =>
  api.patch<Company>(`/companies/${id}`, data).then((r) => r.data);

export const deleteCompany = (id: number) => api.delete(`/companies/${id}`);

export const scrapeJobs = (keywords: string, location: string, limit = 20) =>
  api.post('/pipeline/scrape', { keywords, location, limit }).then((r) => r.data);

export const runPipeline = (companyId: number) =>
  api.post(`/pipeline/analyze/${companyId}`).then((r) => r.data);

export const runBatch = () => api.post('/pipeline/run-batch').then((r) => r.data);

export const reanalyzeCompanies = (mode: 'top' | 'all' = 'top', limit = 50) =>
  api.post('/pipeline/reanalyze', { mode, limit, only_with_website: true }).then((r) => r.data);
