import api from './client';
import type { Company } from '../types';

export const getCompanies = (params?: { status?: string; search?: string }) =>
  api.get<Company[]>('/companies', { params }).then((r) => r.data);

export const createCompany = (data: Partial<Company>) =>
  api.post<Company>('/companies', data).then((r) => r.data);

export const updateCompany = (id: number, data: Partial<Company>) =>
  api.patch<Company>(`/companies/${id}`, data).then((r) => r.data);

export const deleteCompany = (id: number) => api.delete(`/companies/${id}`);

export const scrapeJobs = (keywords: string, location: string, limit = 20) =>
  api.post('/pipeline/scrape', { keywords, location, limit }).then((r) => r.data);

export const runPipeline = (companyId: number) =>
  api.post(`/pipeline/analyze/${companyId}`).then((r) => r.data);

export const runBatch = () => api.post('/pipeline/run-batch').then((r) => r.data);
