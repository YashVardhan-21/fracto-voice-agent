import api from './client';
import type { Campaign } from '../types';

export const getCampaigns = () =>
  api.get<Campaign[]>('/campaigns').then((r) => r.data);

export const createCampaign = (data: Partial<Campaign>) =>
  api.post<Campaign>('/campaigns', data).then((r) => r.data);
