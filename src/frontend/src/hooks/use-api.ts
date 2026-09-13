import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useDashboardStats() {
  return useQuery({ queryKey: ['dashboard-stats'], queryFn: api.getDashboardStats, refetchInterval: 30000 });
}

export function useIncidents() {
  return useQuery({ queryKey: ['incidents'], queryFn: api.getIncidents });
}

export function useIncident(id: number) {
  return useQuery({ queryKey: ['incident', id], queryFn: () => api.getIncident(id), enabled: !!id });
}

export function useTimeline(id: number) {
  return useQuery({ queryKey: ['timeline', id], queryFn: () => api.getTimeline(id), enabled: !!id });
}

export function useGraph(id: number) {
  return useQuery({ queryKey: ['graph', id], queryFn: () => api.getGraph(id), enabled: !!id });
}

export function useEvidence(id: number) {
  return useQuery({ queryKey: ['evidence', id], queryFn: () => api.getEvidence(id), enabled: !!id });
}

export function useMitre(id: number) {
  return useQuery({ queryKey: ['mitre', id], queryFn: () => api.getMitre(id), enabled: !!id });
}

export function useBluf(id: number) {
  return useQuery({ queryKey: ['bluf', id], queryFn: () => api.getBluf(id), enabled: !!id });
}

export function useAlerts(limit = 50, offset = 0) {
  return useQuery({ queryKey: ['alerts', limit, offset], queryFn: () => api.getAlerts({ limit, offset }) });
}

export function useCounterfactual() {
  return useMutation({ 
    mutationFn: ({ incidentId, alertId }: { incidentId: number; alertId: number }) => 
      api.runCounterfactual(incidentId, alertId) 
  });
}

export function useRebuildIncidents() {
  const queryClient = useQueryClient();
  return useMutation({ 
    mutationFn: api.rebuildIncidents,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
    }
  });
}

export function useBobChat() {
  return useMutation({ mutationFn: (message: string) => api.chatWithBob(message) });
}
