import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, ApiError } from '../api';

export function Branding() {
  const qc = useQueryClient();
  const ws = useQuery({ queryKey: ['branding'], queryFn: () => api.getBranding(), retry: false });
  const [name, setName] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [accent, setAccent] = useState('#8a1c2b');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ws.data) {
      setName(ws.data.name || '');
      setLogoUrl(ws.data.logo_url || '');
      setAccent(ws.data.accent_color || '#8a1c2b');
    }
  }, [ws.data]);

  const save = useMutation({
    mutationFn: () => api.putBranding({ name, logo_url: logoUrl, accent_color: accent }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['branding'] });
      setError(null);
    },
    onError: (e) => setError(e instanceof Error ? e.message : 'save failed'),
  });

  if (ws.isLoading) {
    return (
      <main className="page-shell">
        <div className="skeleton" style={{ height: 64 }} />
      </main>
    );
  }

  if (ws.isError) {
    const status = ws.error instanceof ApiError ? ws.error.status : 0;
    return (
      <main className="page-shell" style={{ padding: '32px 0 64px' }}>
        <h1>Branding</h1>
        <p className="error" role="alert">
          {status === 401
            ? 'Sign in to edit workspace branding.'
            : ws.error instanceof Error
              ? ws.error.message
              : 'Could not load branding.'}
        </p>
        {status === 401 && (
          <p>
            <Link to="/login">Sign in</Link>
          </p>
        )}
      </main>
    );
  }

  return (
    <main className="page-shell" style={{ padding: '32px 0 64px' }}>
      <h1>Branding</h1>
      <p>Customize how your share page and embed badge look to clients.</p>
      <form
        className="widget-form"
        onSubmit={(e) => {
          e.preventDefault();
          save.mutate(undefined);
        }}
      >
        <label>
          Workspace name
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          Logo URL (https only)
          <input value={logoUrl} onChange={(e) => setLogoUrl(e.target.value)} placeholder="https://" />
        </label>
        <label>
          Accent color
          <input value={accent} onChange={(e) => setAccent(e.target.value)} />
        </label>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button className="btn" type="submit" disabled={save.isPending}>
          {save.isPending ? 'Saving…' : 'Save'}
        </button>
      </form>
    </main>
  );
}
