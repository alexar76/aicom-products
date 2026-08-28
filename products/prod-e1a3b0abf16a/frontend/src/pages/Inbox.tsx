import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api, Handoff } from '../api';

type Status = 'pending' | 'approved' | 'rejected';

export function Inbox() {
  const [tab, setTab] = useState<Status>('pending');
  const { data, isLoading, error } = useQuery({
    queryKey: ['handoffs', tab],
    queryFn: () => api.listHandoffs(tab),
  });

  return (
    <main className="inbox container">
      <header className="app-nav" style={{ margin: '-32px -24px 24px', borderRadius: 0 }}>
        <Link className="brand" to="/inbox">Relay</Link>
        <nav className="links">
          <Link to="/handoffs/new">New handoff</Link>
          <Link to="/settings/branding">Branding</Link>
        </nav>
      </header>

      <h1>Inbox</h1>
      <p>Pending, approved, and rejected handoffs in your workspace.</p>

      <div className="tabs" role="tablist">
        {(['pending', 'approved', 'rejected'] as Status[]).map((s) => (
          <button
            key={s}
            role="tab"
            aria-selected={tab === s}
            className="tab"
            onClick={() => setTab(s)}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)} ({data?.counts[s] ?? 0})
          </button>
        ))}
      </div>

      {isLoading && <div className="skeleton" style={{ height: 64 }} />}
      {error && <p className="error">Failed to load handoffs.</p>}

      {data && data.items.length === 0 && (
        <div className="surface empty">
          <p>No handoffs here yet.</p>
          <Link to="/handoffs/new" className="btn btn--secondary">Start a handoff</Link>
        </div>
      )}

      {data && data.items.length > 0 && (
        <div className="grid">
          {data.items.map((h: Handoff) => (
            <Link key={h.id} to={`/handoffs/${h.id}`} className="card surface" style={{ color: 'inherit', borderBottom: 'none' }}>
              <h3>{h.client_name}</h3>
              <div className="meta">{h.project_name} · {h.source_ai_tool}</div>
              <div className="meta" style={{ marginTop: 8 }}>{new Date(h.created_at).toLocaleString()}</div>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
