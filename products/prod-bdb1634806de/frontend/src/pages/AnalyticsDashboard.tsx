import { useEffect, useState, FormEvent } from "react";

interface Dashboard {
  id: string;
  name: string;
  state: "draft" | "published" | "archived";
  updated_at?: string;
}

interface Metric {
  id: string;
  name: string;
  source: string;
}

export default function AnalyticsDashboard() {
  const [token] = useState(() => localStorage.getItem("sentinel_token"));
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [newName, setNewName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const authHeaders = { Authorization: `Bearer ${token}` };

  const loadData = async () => {
    if (!token) return;
    try {
      const [dashRes, metricRes] = await Promise.all([
        fetch("/api/analytics/dashboards", { headers: authHeaders }),
        fetch("/api/analytics/metrics", { headers: authHeaders }),
      ]);
      if (!dashRes.ok || !metricRes.ok) throw new Error("Failed to load analytics");
      setDashboards(await dashRes.json());
      setMetrics(await metricRes.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load analytics data");
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const createDashboard = async (e: FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      const response = await fetch("/api/analytics/dashboards", {
        method: "POST",
        headers: { ...authHeaders, "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName }),
      });
      if (!response.ok) throw new Error("Failed to create dashboard");
      setNewName("");
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create dashboard");
    }
  };

  const transitionState = async (id: string, targetState: string) => {
    try {
      const response = await fetch(`/api/analytics/dashboards/${id}`, {
        method: "PATCH",
        headers: { ...authHeaders, "Content-Type": "application/json" },
        body: JSON.stringify({ state: targetState }),
      });
      if (!response.ok) throw new Error("Failed to update dashboard");
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update dashboard");
    }
  };

  const shareDashboard = async (id: string) => {
    try {
      const response = await fetch(`/api/analytics/dashboards/${id}/share`, {
        method: "POST",
        headers: authHeaders,
      });
      if (!response.ok) throw new Error("Failed to share dashboard");
      const data = await response.json();
      alert(`Share link: ${data.share_url || data.share_token || "generated"}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to share");
    }
  };

  if (!token) {
    return (
      <div>
        <h1>Analytics Workspace</h1>
        <p>Please <a href="#/login">login</a> first.</p>
      </div>
    );
  }

  return (
    <div>
      <h1>Analytics / BI Workspace</h1>
      <p className="muted">Define metrics, build charts, share dashboards with lifecycle states.</p>
      {error && <div className="card"><p style={{ color: "var(--danger)" }}>{error}</p></div>}

      <div className="card">
        <h2>Create Dashboard</h2>
        <form onSubmit={createDashboard} style={{ display: "flex", gap: "0.75rem" }}>
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Dashboard name"
            required
            style={{ flex: "1" }}
          />
          <button className="btn" type="submit">Create</button>
        </form>
      </div>

      <div className="grid-3">
        {dashboards.map((d) => (
          <div key={d.id} className="card">
            <h3>{d.name}</h3>
            <p className="muted">State: {d.state}</p>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {d.state === "draft" && (
                <button className="btn btn-secondary" onClick={() => transitionState(d.id, "published")}>Publish</button>
              )}
              {d.state === "published" && (
                <>
                  <button className="btn btn-secondary" onClick={() => transitionState(d.id, "archived")}>Archive</button>
                  <button className="btn btn-secondary" onClick={() => shareDashboard(d.id)}>Share</button>
                </>
              )}
              {d.state === "archived" && (
                <button className="btn btn-secondary" onClick={() => transitionState(d.id, "published")}>Republish</button>
              )}
              <a className="btn btn-secondary" href={`/api/analytics/dashboards/${d.id}/export?format=csv`} style={{ textDecoration: "none" }}>CSV</a>
              <a className="btn btn-secondary" href={`/api/analytics/dashboards/${d.id}/export?format=xlsx`} style={{ textDecoration: "none" }}>XLSX</a>
            </div>
          </div>
        ))}
        {dashboards.length === 0 && <p>No dashboards yet.</p>}
      </div>

      <div className="card">
        <h2>Available Metrics</h2>
        {metrics.length > 0 ? (
          <ul>
            {metrics.map((m) => (
              <li key={m.id}>{m.name} ({m.source})</li>
            ))}
          </ul>
        ) : (
          <p>No metrics defined.</p>
        )}
      </div>
    </div>
  );
}
