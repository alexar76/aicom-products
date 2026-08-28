import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, ApiError } from '../api';

export function NewHandoff() {
  const navigate = useNavigate();
  const [clientName, setClientName] = useState('');
  const [projectName, setProjectName] = useState('');
  const [sourceAiTool, setSourceAiTool] = useState('ChatGPT');
  const [draftText, setDraftText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const h = await api.createHandoff({ client_name: clientName, project_name: projectName, source_ai_tool: sourceAiTool, draft_text: draftText });
      navigate(`/handoffs/${h.id}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 413) setError('Draft is too long (50,000 character limit).');
      else setError(err instanceof Error ? err.message : 'failed to create handoff');
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="container" style={{ padding: '32px 0 64px' }}>
      <h1>New handoff</h1>
      <p>Paste an AI draft. You will run a skeptic pass next.</p>
      <form className="widget-form" onSubmit={onSubmit}>
        <label>
          Client name
          <input value={clientName} onChange={(e) => setClientName(e.target.value)} required />
        </label>
        <label>
          Project name
          <input value={projectName} onChange={(e) => setProjectName(e.target.value)} required />
        </label>
        <label>
          Source AI tool
          <input value={sourceAiTool} onChange={(e) => setSourceAiTool(e.target.value)} required />
        </label>
        <label>
          Draft text (≥ 20 characters)
          <textarea rows={10} value={draftText} onChange={(e) => setDraftText(e.target.value)} required minLength={20} />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="btn" type="submit" disabled={busy} data-testid="create-handoff">
          {busy ? 'Creating…' : 'Create handoff'}
        </button>
      </form>
    </main>
  );
}
