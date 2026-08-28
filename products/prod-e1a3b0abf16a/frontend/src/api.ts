/**
 * Single shared API client for the Relay SPA.
 *
 * Every page imports `api` from here. The base URL is `/api` so the dev
 * proxy and Vercel rewrites resolve the same way in both environments.
 */

const BASE = import.meta.env.VITE_API_BASE || '/api';
const TOKEN_KEY = 'relay_access_token';

export interface Operator {
  id: string;
  email: string;
  role: string;
  workspace_id: string;
  created_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  logo_url: string | null;
  accent_color: string;
  tier: string;
  created_at: string;
}

export interface AuthSession {
  operator: Operator;
  workspace: Workspace;
  access_token?: string;
  token_type?: string;
}

export interface Handoff {
  id: string;
  workspace_id: string;
  client_name: string;
  project_name: string;
  source_ai_tool: string;
  draft_text: string;
  approved_text: string | null;
  status: 'pending' | 'approved' | 'rejected';
  share_token: string;
  content_sha256: string;
  verification_source: 'local' | 'metis' | 'unavailable';
  created_by: string | null;
  approved_by: string | null;
  approved_at: string | null;
  rejected_reason: string | null;
  created_at: string;
}

export interface HandoffList {
  items: Handoff[];
  counts: { pending: number; approved: number; rejected: number };
}

export interface PublicHandoff {
  id: string;
  client_name: string;
  project_name: string;
  source_ai_tool: string;
  approved_text: string;
  approved_at: string | null;
  content_sha256: string;
}

export interface PublicRead {
  handoff: PublicHandoff;
  workspace: { name: string; logo_url: string | null; accent_color: string; tier: string };
  verification_source: 'local' | 'metis' | 'unavailable';
}

export function setAccessToken(token: string | null) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* private mode */
  }
}

function accessToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function csrfTokenFromCookie(): string | null {
  const meta = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement | null;
  return meta ? meta.content : null;
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  withCsrf = false,
): Promise<T> {
  const headers: Record<string, string> = {
    'content-type': 'application/json',
    ...((init.headers as Record<string, string>) || {}),
  };
  const token = accessToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (withCsrf) {
    const csrf = csrfTokenFromCookie();
    if (csrf) headers['x-relay-csrf'] = csrf;
  }
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    credentials: 'include',
    headers,
  });
  if (!res.ok) {
    const text = await res.text();
    let detail: unknown = text;
    try {
      detail = JSON.parse(text).detail;
    } catch {
      /* leave as text */
    }
    throw new ApiError(res.status, String(detail));
  }
  if (res.status === 204) return undefined as unknown as T;
  return (await res.json()) as T;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export const api = {
  signup: async (body: { email: string; password: string; workspace_name: string }) => {
    const r = await request<AuthSession>('/auth/signup', { method: 'POST', body: JSON.stringify(body) });
    if (r.access_token) setAccessToken(r.access_token);
    return r;
  },
  login: async (body: { email: string; password: string }) => {
    const r = await request<AuthSession>('/auth/login', { method: 'POST', body: JSON.stringify(body) });
    if (r.access_token) setAccessToken(r.access_token);
    return r;
  },
  logout: async () => {
    try {
      await request<{ ok: true }>('/auth/logout', { method: 'POST' }, true);
    } finally {
      setAccessToken(null);
    }
  },
  me: () => request<{ operator: Operator; workspace: Workspace }>('/auth/me'),
  csrf: () => request<{ csrf_token: string }>('/auth/csrf'),

  createHandoff: (body: {
    client_name: string;
    project_name: string;
    source_ai_tool: string;
    draft_text: string;
  }) => request<Handoff>('/handoffs', { method: 'POST', body: JSON.stringify(body) }, true),
  listHandoffs: (status?: 'pending' | 'approved' | 'rejected') =>
    request<HandoffList>(`/handoffs${status ? `?status=${status}` : ''}`, {}, true),
  getHandoff: (id: string) => request<Handoff>(`/handoffs/${id}`, {}, true),
  verifyHandoff: (id: string, items: { category: string; passed: boolean; notes: string }[], useMetis = false) =>
    request<{ verification_items: unknown[]; verification_source: string }>(
      `/handoffs/${id}/verify`,
      { method: 'POST', body: JSON.stringify({ items, use_metis: useMetis }) },
      true,
    ),
  approveHandoff: (id: string, body: { approved_text?: string; override_rejection?: boolean } = {}) =>
    request<Handoff>(`/handoffs/${id}/approve`, { method: 'POST', body: JSON.stringify(body) }, true),
  rejectHandoff: (id: string, reason: string) =>
    request<Handoff>(`/handoffs/${id}/reject`, { method: 'POST', body: JSON.stringify({ reason }) }, true),
  receipt: (id: string) =>
    request<Record<string, unknown>>(`/handoffs/${id}/receipt.json`, {}, true),
  embedSnippet: (id: string) =>
    request<{ script: string; iframe: string }>(`/handoffs/${id}/embed-snippet`, {}, true),

  readPublic: (token: string) => request<PublicRead>(`/public/handoffs/${token}`),

  getBranding: () => request<Workspace>('/workspace/branding', {}, true),
  putBranding: (body: { name?: string; logo_url?: string; accent_color?: string }) =>
    request<Workspace>('/workspace/branding', { method: 'PUT', body: JSON.stringify(body) }, true),
};
