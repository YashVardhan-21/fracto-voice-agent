import api from './client';

export interface Branding {
  company_name: string;
  primary_color: string;
  logo_url?: string;
}

export async function getBranding(): Promise<Branding> {
  const { data } = await api.get<Branding>('/settings/branding');
  return data;
}

export async function updateBranding(payload: Partial<Branding>): Promise<void> {
  await api.patch('/settings/branding', payload);
}
