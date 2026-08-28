import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';

export function Signup() {
  const navigate = useNavigate();
  const [email, setEmail] = useState(import.meta.env.VITE_DEMO_EMAIL || '');
  const [password, setPassword] = useState(import.meta.env.VITE_DEMO_PASSWORD || '');
  const [workspace, setWorkspace] = useState('My Studio');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await api.signup({ email, password, workspace_name: workspace });
      const csrf = await api.csrf();
      let meta = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement | null;
      if (!meta) {
        meta = document.createElement('meta');
        meta.name = 'csrf-token';
        document.head.appendChild(meta);
      }
      meta.content = csrf.csrf_token;
      navigate('/inbox');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'signup failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page surface">
      <h1>Create your workspace</h1>
      <p>One workspace per team on the free tier.</p>
      <form className="widget-form" onSubmit={onSubmit}>
        <label>
          Workspace name
          <input value={workspace} onChange={(e) => setWorkspace(e.target.value)} required />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Password (≥ 10 characters)
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={10} />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="btn" type="submit" disabled={busy} data-testid="signup-submit">
          {busy ? 'Creating…' : 'Create workspace'}
        </button>
      </form>
    </main>
  );
}
