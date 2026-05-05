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

export interface IntegrationConfigured {
  configured: boolean;
}

export interface IntegrationsRead {
  vapi: {
    api_key: IntegrationConfigured;
    voice_id?: string;
    phone_number_id?: string;
  };
  llm: {
    openai_api_key: IntegrationConfigured;
    gemini_api_key: IntegrationConfigured;
    deepseek_api_key: IntegrationConfigured;
  };
  leads: {
    google_places_api_key: IntegrationConfigured;
    adzuna_app_id: IntegrationConfigured;
    adzuna_app_key: IntegrationConfigured;
    adzuna_country?: string;
  };
}

export interface IntegrationsPatch {
  vapi?: { api_key?: string; voice_id?: string; phone_number_id?: string };
  llm?: { openai_api_key?: string; gemini_api_key?: string; deepseek_api_key?: string };
  leads?: {
    google_places_api_key?: string;
    adzuna_app_id?: string;
    adzuna_app_key?: string;
    adzuna_country?: string;
  };
}

export async function getIntegrations(): Promise<IntegrationsRead> {
  const { data } = await api.get<IntegrationsRead>('/settings/integrations');
  return data;
}

export async function updateIntegrations(payload: IntegrationsPatch): Promise<void> {
  await api.patch('/settings/integrations', payload);
}
