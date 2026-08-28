import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { api } from '../api';

export function Share() {
  const { token = '' } = useParams();
  const q = useQuery({
    queryKey: ['public', token],
    queryFn: () => api.readPublic(token),
    enabled: !!token,
    retry: false,
  });

  if (q.isLoading) return <main className="share-page"><div className="skeleton" style={{ height: 64, maxWidth: 720, margin: '0 auto' }} /></main>;
  if (q.isError || !q.data) {
    return (
      <main className="share-page">
        <div className="share-card">
          <h1>Not available</h1>
          <p>This handoff is either pending review, rejected, or has been removed. No draft content is shown.</p>
        </div>
      </main>
    );
  }
  const { handoff, workspace, verification_source } = q.data;
  return (
    <main className="share-page">
      <article
        className="share-card"
        style={{ borderLeft: `6px solid ${workspace.accent_color}` }}
      >
        <div className="verified-badge" role="status" aria-label={`Human-verified by ${workspace.name}`}>
          <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M5 12l4 4 10-10" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Human-verified by {workspace.name}
        </div>
        <h1 style={{ marginTop: 16 }}>{handoff.client_name} — {handoff.project_name}</h1>
        <p className="byline">
          Approved {handoff.approved_at ? new Date(handoff.approved_at).toLocaleString() : ''} · source: {handoff.source_ai_tool} · review source: {verification_source}
        </p>
        <div className="body">{handoff.approved_text}</div>
        <p className="byline mono">Content hash: <code>{handoff.content_sha256}</code></p>
        {workspace.tier === 'free' && <p className="footer-mark">Made with Relay</p>}
      </article>
    </main>
  );
}
