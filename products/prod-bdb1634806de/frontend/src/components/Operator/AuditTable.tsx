import { useEffect, useState } from 'react';
import { fetchAudit } from '../../api/operator';

export default function AuditTable() {
  const [data, setData] = useState<any>(null);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchAudit(page).then(setData).catch(console.error);
  }, [page]);

  if (!data) return <div>Loading audit...</div>;

  return (
    <div className="card">
      <h3>Audit Log</h3>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>Time</th>
              <th>Capability</th>
              <th>Cost</th>
              <th>Receipt</th>
              <th>Status</th>
              <th>Latency</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item: any) => (
              <tr key={item.id}>
                <td>{new Date(item.created_at).toLocaleString()}</td>
                <td>{item.capability}</td>
                <td>${item.cost_usd.toFixed(2)}</td>
                <td>{item.receipt?.substring(0,10)}...</td>
                <td>{item.status}</td>
                <td>{item.latency_ms}ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
        <button className="btn btn-secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Prev</button>
        <button className="btn btn-secondary" onClick={() => setPage(p => p + 1)}>Next</button>
      </div>
    </div>
  );
}
