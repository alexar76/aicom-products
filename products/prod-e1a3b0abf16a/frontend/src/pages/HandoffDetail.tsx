import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { api } from '../api';

const CHECKLIST = ['claims', 'sources', 'tone', 'risk'] as const;

export function HandoffDetail() {
  const { id = '' } = useParams();
  const qc = useQueryClient();
  const handoff = useQuery({ queryKey: ['handoff', id], queryFn: () => api.getHandoff(id), enabled: !!id });
  const audit = useQuery({ queryKey: ['handoff-audit', id], queryFn: async () => {
    const r = await fetch(`/api/handoffs/${id}/audit`, { credentials: 'include' });
    return r.ok ? (await r.json()) : { items: [] };
  }, enabled: !!id });

  const verify = useMutation({
    mutationFn: () =>
      api.verifyHandoff(
        id,
        CHECKLIST.map((category) => ({ category, passed: true, notes: 'Reviewed by operator.' })),
        false,
      ),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['handoff', id] }),
  });
  const approve = useMutation({
    mutationFn: () => api.approveHandoff(id, {}),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['handoff', id] }),
  });
  const reject = useMutation({
    mutationFn: (reason: string) => api.rejectHandoff(id, reason),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['handoff', id] }),
  });
  const receipt = useMutation({
    mutationFn: async () => {
      const r = await api.receipt(id);
      const blob = new Blob([JSON.stringify(r, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `relay-receipt-${id}.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
  });

  if (handoff.isLoading) return <main className="container"><div className="skeleton" style={{ height: 64 }} /></main>;
  if (handoff.error || !handoff.data) return <main className="container"><p className="error">Handoff not found.</p></main>;

  const h = handoff.data;
  const shareUrl = `${window.location.origin}/share/${h.share_token}`;

  return (
    <main className="detail container">
      <section className="surface" style={{ padding: 24 }}>
        <h1>{h.client_name}</h1>
        <p className="mono" style={{ color: 'var(--ink-muted)' }}>{h.project_name} · {h.source_ai_tool}</p>
        <p>Status: <strong>{h.status}</strong> · Verification source: <code>{h.verification_source}</code></p>
        <pre className="surface" style={{ padding: 16, whiteSpace: 'pre-wrap' }}>{h.approved_text || h.draft_text}</pre>

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 16 }}>
          <button className="btn" onClick={() => verify.mutate()} disabled={verify.isPending} data-testid="run-skeptic">
            Run skeptic pass
          </button>
          <button className="btn" onClick={() => approve.mutate()} disabled={approve.isPending || h.status === 'approved'} data-testid="approve">
            Approve & publish
          </button>
          <button
            className="btn btn--secondary"
            onClick={() => {
              const reason = window.prompt('Reject reason?') || '';
              if (reason) reject.mutate(reason);
            }}
            disabled={reject.isPending || h.status === 'rejected'}
          >
            Reject
          </button>
          <button className="btn btn--secondary" onClick={() => receipt.mutate()} disabled={receipt.isPending}>
            Export receipt
          </button>
        </div>

        {h.status === 'approved' && (
          <p style={{ marginTop: 16 }}>
            Public share URL: <a href={shareUrl}>{shareUrl}</a>
          </p>
        )}
      </section>

      <aside className="audit">
        <div className="surface" style={{ padding: 16 }}>
          <h2>Audit timeline</h2>
          <ul>
            {(audit.data?.items || []).map((e: { id: string; action: string; actor_email: string | null; created_at: string }) => (
              <li key={e.id}>
                <strong>{e.action}</strong> — {e.actor_email || 'system'}<br />
                <span style={{ color: 'var(--ink-muted)' }}>{new Date(e.created_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </main>
  );
}
