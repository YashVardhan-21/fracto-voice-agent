import api from './client';
import type { VoiceAgent } from '../types';

export const getAgents = () =>
  api.get<VoiceAgent[]>('/agents').then((r) => r.data);
