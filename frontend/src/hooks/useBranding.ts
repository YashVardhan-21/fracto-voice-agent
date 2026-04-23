import { useQuery } from '@tanstack/react-query';
import { getBranding } from '../api/settings';

export function useBranding() {
  return useQuery({ queryKey: ['branding'], queryFn: getBranding, staleTime: Infinity });
}
