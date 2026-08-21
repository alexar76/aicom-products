import apiClient from './client';

export interface SpendData {
  total_spend_usd: number;
  daily_spend_usd: number;
  budget_usd: number;
  invokes_total: number;
  invokes_24h: number;
  advisories_served: number;
  receipts_verified: number;
  errors_24h: number;
  cache_hit_rate: number;
}

export async function fetchSpend(): Promise<SpendData> {
  const response = await apiClient.get<SpendData>('/api/operator/spend');
  return response.data;
}

export async function fetchAllowance() {
  const response = await apiClient.get('/api/operator/allowance');
  return response.data;
}

export async function fetchWallet() {
  const response = await apiClient.get('/api/operator/wallet');
  return response.data;
}

export async function fetchAudit(page = 1, perPage = 20) {
  const response = await apiClient.get('/api/operator/audit', { params: { page, per_page: perPage } });
  return response.data;
}
