import { useState, FormEvent } from "react";

export default function OperatorLogin() {
  const [email, setEmail] = useState(import.meta.env.VITE_SANDBOX_DEMO_EMAIL || "operator@sentinel.local");
  const [password, setPassword] = useState(import.meta.env.VITE_SANDBOX_DEMO_PASSWORD || "SentinelDemo123!");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        throw new Error(`Login failed: ${response.status}`);
      }
      const data = await response.json();
      if (data.access_token) {
        localStorage.setItem("sentinel_token", data.access_token);
      }
      window.location.hash = "#/operator";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <h1>Operator Login</h1>
      <div className="card" style={{ maxWidth: "420px", margin: "0 auto" }}>
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: "1rem" }}>
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label htmlFor="password">Password</label>
            <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
          <button className="btn" type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="muted" style={{ marginTop: "1rem" }}>
          Demo credentials prefilled from environment.
        </p>
      </div>
    </div>
  );
}
