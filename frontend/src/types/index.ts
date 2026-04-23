export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'agent' | 'manager' | 'admin';
}

export interface Company {
  id: number;
  name: string;
  website?: string;
  location?: string;
  business_type?: string;
  services?: string[];
  phone?: string;
  analysis_score?: number;
  status: 'pending' | 'analyzing' | 'prompt_ready' | 'agent_created' | 'vapi_failed';
  created_at: string;
}

export interface VoiceAgent {
  id: number;
  company_id: number;
  name: string;
  vapi_agent_id?: string;
  system_prompt?: string;
  status: 'draft' | 'active' | 'paused';
  total_calls: number;
  successful_calls: number;
  created_at: string;
}

export interface Campaign {
  id: number;
  name: string;
  description?: string;
  target_type?: string;
  status: 'draft' | 'running' | 'paused' | 'completed';
  metrics?: Record<string, number>;
  created_at: string;
}

export interface DashboardStats {
  total_companies: number;
  active_agents: number;
  total_campaigns: number;
  total_calls: number;
}
