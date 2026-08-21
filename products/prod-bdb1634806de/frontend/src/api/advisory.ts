import apiClient from './client';

export interface AdvisoryResponse {
  overall: {
    level: string;
    reason: string;
    receipt?: string;
  };
  hazards: Array<{
    type: string;
    level: string;
    measurement?: string;
    distance_km?: number;
    receipt?: string;
    timestamp?: string;
    is_cached: boolean;
    sim: boolean;
  }>;
  thresholds: Array<{
    name: string;
    condition: string;
    fired: boolean;
  }>;
  location: { lat: number; lon: number; rounded: boolean };
}

export async function fetchAdvisory(lat: number, lon: number): Promise<AdvisoryResponse> {
  const response = await apiClient.get<AdvisoryResponse>('/api/advisory', {
    params: { lat, lon },
  });
  return response.data;
}
