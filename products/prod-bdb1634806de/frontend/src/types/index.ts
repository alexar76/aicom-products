export interface HazardInfo {
  type: string
  level: string
  measurement?: string
  distance_km?: number
  receipt?: string
  timestamp: string
  is_cached: boolean
  sim: boolean
}

export interface AdvisoryResponse {
  overall: {
    level: string
    reason: string
    receipt?: string
  }
  hazards: HazardInfo[]
  thresholds: { name: string; condition: string; fired: boolean }[]
  location: { lat: number; lon: number; rounded: boolean }
}

export interface SpendSummary {
  total_spend_usd: number
  daily_spend_usd: number
  budget_usd: number
  invokes_total: number
  invokes_24h: number
  advisories_served: number
  receipts_verified: number
  errors_24h: number
  cache_hit_rate: number
}

export interface AllowanceInfo {
  used: number
  max: number
  window_seconds: number
  renews_at: string | null
}

export interface WalletInfo {
  wallet_enabled: boolean
  address_truncated?: string
  chain?: string
}

export interface AuditItem {
  id: string
  capability: string
  cost_usd: number
  receipt?: string
  latency_ms: number
  status: string
  created_at: string
}

export interface AuditList {
  items: AuditItem[]
  total: number
  page: number
  per_page: number
}

export interface Dashboard {
  id: string
  name: string
  state: 'draft' | 'published' | 'archived'
  updated_at: string
}

export interface Metric {
  id: string
  name: string
  data_source: string
}
