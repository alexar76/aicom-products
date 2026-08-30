/**
 * Single shared API client for the Relay SPA.
 *
 * Every page imports `api` from here. The base URL is `/api` so the dev
 * proxy and Vercel rewrites resolve the same way in both environments.
 */
const BASE = import.meta.env.VITE_API_BASE || '/api';
const TOKEN_KEY = 'relay_access_token';
export function setAccessToken(token) {
    try {
        if (token)
            localStorage.setItem(TOKEN_KEY, token);
        else
            localStorage.removeItem(TOKEN_KEY);
    }
    catch {
        /* private mode */
    }
}
function accessToken() {
    try {
        return localStorage.getItem(TOKEN_KEY);
    }
    catch {
        return null;
    }
}
function csrfTokenFromCookie() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : null;
}
async function request(path, init = {}, withCsrf = false) {
    const headers = {
        'content-type': 'application/json',
        ...(init.headers || {}),
    };
    const token = accessToken();
    if (token)
        headers.Authorization = `Bearer ${token}`;
    if (withCsrf) {
        const csrf = csrfTokenFromCookie();
        if (csrf)
            headers['x-relay-csrf'] = csrf;
    }
    const res = await fetch(`${BASE}${path}`, {
        ...init,
        credentials: 'include',
        headers,
    });
    if (!res.ok) {
        const text = await res.text();
        let detail = text;
        try {
            detail = JSON.parse(text).detail;
        }
        catch {
            /* leave as text */
        }
        throw new ApiError(res.status, String(detail));
    }
    if (res.status === 204)
        return undefined;
    return (await res.json());
}
export class ApiError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}
export const api = {
    signup: async (body) => {
        const r = await request('/auth/signup', { method: 'POST', body: JSON.stringify(body) });
        if (r.access_token)
            setAccessToken(r.access_token);
        return r;
    },
    login: async (body) => {
        const r = await request('/auth/login', { method: 'POST', body: JSON.stringify(body) });
        if (r.access_token)
            setAccessToken(r.access_token);
        return r;
    },
    logout: async () => {
        try {
            await request('/auth/logout', { method: 'POST' }, true);
        }
        finally {
            setAccessToken(null);
        }
    },
    me: () => request('/auth/me'),
    csrf: () => request('/auth/csrf'),
    createHandoff: (body) => request('/handoffs', { method: 'POST', body: JSON.stringify(body) }, true),
    listHandoffs: (status) => request(`/handoffs${status ? `?status=${status}` : ''}`, {}, true),
    getHandoff: (id) => request(`/handoffs/${id}`, {}, true),
    verifyHandoff: (id, items, useMetis = false) => request(`/handoffs/${id}/verify`, { method: 'POST', body: JSON.stringify({ items, use_metis: useMetis }) }, true),
    approveHandoff: (id, body = {}) => request(`/handoffs/${id}/approve`, { method: 'POST', body: JSON.stringify(body) }, true),
    rejectHandoff: (id, reason) => request(`/handoffs/${id}/reject`, { method: 'POST', body: JSON.stringify({ reason }) }, true),
    receipt: (id) => request(`/handoffs/${id}/receipt.json`, {}, true),
    embedSnippet: (id) => request(`/handoffs/${id}/embed-snippet`, {}, true),
    readPublic: (token) => request(`/public/handoffs/${token}`),
    getBranding: () => request('/workspace/branding', {}, true),
    putBranding: (body) => request('/workspace/branding', { method: 'PUT', body: JSON.stringify(body) }, true),
};
