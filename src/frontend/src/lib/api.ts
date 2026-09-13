import type { Alert, Incident, DashboardStats, TimelineEvent, GraphData, Evidence, MitreTechnique, BlufData, CounterfactualResult } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  getHealth: () => fetchApi('/api/health'),
  getDashboardStats: () => fetchApi<DashboardStats>('/api/dashboard/stats'),
  getAlerts: (params?: { limit?: number; offset?: number }) => fetchApi<Alert[]>(`/api/alerts?limit=${params?.limit || 50}&offset=${params?.offset || 0}`),
  getAlert: (id: number) => fetchApi<Alert>(`/api/alerts/${id}`),
  getIncidents: () => fetchApi<Incident[]>('/api/incidents'),
  getIncident: (id: number) => fetchApi<Incident>(`/api/incidents/${id}`),
  getTimeline: (id: number) => fetchApi<TimelineEvent[]>(`/api/incidents/${id}/timeline`),
  getGraph: (id: number) => fetchApi<GraphData>(`/api/incidents/${id}/graph`),
  getEvidence: (id: number) => fetchApi<Evidence[]>(`/api/incidents/${id}/evidence`),
  getMitre: (id: number) => fetchApi<MitreTechnique[]>(`/api/incidents/${id}/mitre`),
  getBluf: (id: number) => fetchApi<BlufData>(`/api/incidents/${id}/bluf`),
  runCounterfactual: (incidentId: number, alertId: number) => fetchApi<CounterfactualResult>(`/api/incidents/${incidentId}/counterfactual`, { method: 'POST', body: JSON.stringify({ remove_alert_id: alertId }) }),
  rebuildIncidents: () => fetchApi('/api/incidents/rebuild', { method: 'POST' }),
  chatWithBob: (message: string) => fetchApi<{ response: string; tool_calls: string[] }>('/api/bob/chat', { method: 'POST', body: JSON.stringify({ message }) }),
};
