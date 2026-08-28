"use strict";
/**
 * Standalone embed widget for Relay.
 *
 * Loaded as a tiny IIFE on a third-party site via:
 *   <script src="./embed.js?token=..." async></script>
 *
 * Fetches /api/public/handoffs/{token} and renders a "Human-verified" badge
 * linking back to /share/{token}. Surfaces "Verification unavailable" on
 * invalid tokens without throwing.
 */
(function () {
    const scripts = document.getElementsByTagName('script');
    const current = scripts[scripts.length - 1];
    const src = current && current.src ? current.src : '';
    const url = new URL(src || window.location.href);
    const token = url.searchParams.get('token') || '';
    if (!token) {
        console.error('[relay] embed: missing token query param');
        return;
    }
    const base = url.origin;
    fetch(`${base}/api/public/handoffs/${encodeURIComponent(token)}`, { credentials: 'omit' })
        .then((r) => {
        if (r.status === 404)
            throw new Error('not_available');
        if (r.status === 429)
            throw new Error('rate_limited');
        if (!r.ok)
            throw new Error('http_' + r.status);
        return r.json();
    })
        .then((data) => {
        const accent = (data && data.workspace && data.workspace.accent_color) || '#2f6b3a';
        const name = (data && data.workspace && data.workspace.name) || 'Relay';
        const a = document.createElement('a');
        a.href = `${base}/share/${encodeURIComponent(token)}`;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.setAttribute('aria-label', `Human-verified by ${name}`);
        a.style.cssText = [
            'display:inline-flex',
            'align-items:center',
            'gap:8px',
            'padding:6px 12px',
            'border-radius:999px',
            'background:#e6efd9',
            'color:#2f6b3a',
            'font:600 13px/1.2 system-ui, sans-serif',
            'text-decoration:none',
            'border:1px solid ' + accent,
        ].join(';');
        a.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12l4 4 10-10" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg> Human-verified by ${name.replace(/[<>&]/g, '')}`;
        current.parentNode && current.parentNode.insertBefore(a, current.nextSibling);
    })
        .catch((err) => {
        console.error('[relay] verification unavailable:', err && err.message);
        const span = document.createElement('span');
        span.textContent = 'Verification unavailable';
        span.style.cssText = 'display:inline-block;padding:6px 12px;border-radius:999px;background:#eee;color:#666;font:13px system-ui;';
        current.parentNode && current.parentNode.insertBefore(span, current.nextSibling);
    });
})();
