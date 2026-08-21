import apiClient from './client';

export async function fetchDashboards(state?: string) {
  const response = await apiClient.get('/api/analytics/dashboards', { params: state ? { state } : {} });
  return response.data;
}

export async function createDashboard(name: string) {
  const response = await apiClient.post('/api/analytics/dashboards', { name });
  return response.data;
}

export async function updateDashboard(id: string, payload: { name?: string; state?: string }) {
  const response = await apiClient.patch(`/api/analytics/dashboards/${id}`, payload);
  return response.data;
}

export async function shareDashboard(id: string) {
  const response = await apiClient.post(`/api/analytics/dashboards/${id}/share`);
  return response.data;
}
