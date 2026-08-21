import { useEffect, useState } from "react";

interface SpendData {
  total_spend_usd: number;
  daily_spend_usd: number;
  budget_usd: number;
  invokes_total: number;
  invokes_24h: number;
  advisories_served: number;
  receipts_verified: number;
  errors_24h: number;
  cache_hit_rate: number;
}

interface AllowanceData {
  used: number;
  max: number;
  window_seconds: number;
  renews_at: string;
}

interface WalletData {
  wallet_enabled: boolean;
  address_truncated?: string;
  chain?: string;
}

interface AuditItem {
  id: string;
  capability: string;
  cost_usd: number;
  receipt: string;
  latency_ms: number;
  status: string;
  created_at: string;
}

export default function OperatorDashboard() {
  const [token] = useState(() => localStorage.getItem("sentinel_token"));
  const [spend, setSpend] = useState<SpendData | null>(null);
  const [allowance, setAllowance] = useState<AllowanceData | null>(null);
  const [wallet, setWallet] = useState<WalletData | null>(null);
  const [audit, setAudit] = useState<AuditItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  const authHeaders = { Authorization: `Bearer ${token}` };

  const loadData = async () => {
    if (!token) return;
    try {
      const [spendRes, allowanceRes, walletRes, auditRes] = await Promise.all([
        fetch("/api/operator/spend", { headers: authHeaders }),
        fetch("/api/operator/allowance", { headers: authHeaders }),
        fetch("/api/operator/wallet", { headers: authHeaders }),
        fetch("/api/operator/audit?page=1&per_page=5", { headers: authHeaders }),
      ]);
      if (!spendRes.ok || !allowanceRes.ok || !walletRes.ok || !auditRes.ok) {
        throw new Error("Failed to load operator data");
      }
      setSpend(await spendRes.json());
      setAllowance((await allowanceRes.json()) || null);
      setWallet(await walletRes.json());
      const auditData = await auditRes.json();
      setAudit(auditData.items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const handleLogout = () => {
    localStorage.removeItem("sentinel_token");
    window.location.hash = "#/login";
  };

  if (!token) {
    return (
      <div>
        <h1>Operator Dashboard</h1>
        <p>Please <a href="#/login">login</a> first.</p>
      </div>
    );
  }

  return (
    <div>
      <h1>Operator Dashboard</h1>
      <p className="muted">Audit, spend, allowance and wallet status.</p>
      {error && <div className="card"><p style={{ color: "var(--danger)" }}>{error}</p></div>}
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "1rem" }}>
        <button className="btn btn-secondary" onClick={handleLogout}>Logout</button>
      </div>

      <div className="grid-3">
        <div className="card">
          <h2>Spend</h2>
          {spend ? (
            <>
              <p>Total: <strong>${spend.total_spend_usd.toFixed(2)}</strong></p>
              <p>Today: ${spend.daily_spend_usd.toFixed(2)}</p>
              <p>Budget: ${spend.budget_usd.toFixed(2)}</p>
              <p>Invokes (24h): {spend.invokes_24h}</p>
              <p>Cache hit rate: {(spend.cache_hit_rate * 100).toFixed(0)}%</p>
            </>
          ) : <p>Loading...</p>}
        </div>
        <div className="card">
          <h2>Allowance</h2>
          {allowance ? (
            <>
              <p>Used: {allowance.used} / {allowance.max}</p>
              <p>Window: {allowance.window_seconds}s</p>
              <p>Renews: {new Date(allowance.renews_at).toLocaleString()}</p>
            </>
          ) : <p>No allowance data</p>}
        </div>
        <div className="card">
          <h2>Wallet</h2>
          {wallet ? (
            wallet.wallet_enabled ? (
              <>
                <p>Enabled: Yes</p>
                <p>Address: {wallet.address_truncated || "N/A"}</p>
                <p>Chain: {wallet.chain || "N/A"}</p>
              </>
            ) : (
              <p>Free allowance mode</p>
            )
          ) : <p>Loading...</p>}
        </div>
      </div>

      <div className="card">
        <h2>Recent invoke audit</h2>
        {audit.length > 0 ? (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>Capability</th>
                <th>Cost</th>
                <th>Receipt</th>
                <th>Latency</th>
                <th>Status</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {audit.map((item) => (
                <tr key={item.id}>
                  <td>{item.capability}</td>
                  <td>${item.cost_usd.toFixed(2)}</td>
                  <td className="mono" style={{ maxWidth: "200px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.receipt}</td>
                  <td>{item.latency_ms}ms</td>
                  <td>{item.status}</td>
                  <td>{new Date(item.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p>No audit entries yet.</p>}
      </div>
    </div>
  );
}
