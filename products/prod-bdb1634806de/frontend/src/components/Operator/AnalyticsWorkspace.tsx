import { useEffect, useState } from 'react';
import { fetchDashboards, createDashboard, updateDashboard, shareDashboard } from '../../api/analytics';

export default function AnalyticsWorkspace() {
  const [dashboards, setDashboards] = useState<any[]>([]);
  const [newName, setNewName] = useState('');

  useEffect(() => {
    fetchDashboards().then(setDashboards).catch(console.error);
  }, []);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    await createDashboard(newName);
    setNewName('');
    fetchDashboards().then(setDashboards);
  };

  const handlePublish = async (id: string) => {
    await updateDashboard(id, { state: 'published' });
    fetchDashboards().then(setDashboards);
  };

  const handleShare = async (id: string) => {
    const share = await shareDashboard(id);
    alert(`Shared URL: ${share.share_url}`);
  };

  return (
    <div>
      <h3>Analytics Workspace</h3>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <input
          className="input"
          placeholder="New dashboard name"
          value={newName}
          onChange={e => setNewName(e.target.value)}
        />
        <button className="btn" onClick={handleCreate}>Create</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
        {dashboards.map((d: any) => (
          <div className="card" key={d.id}>
            <h4>{d.name}</h4>
            <p>State: {d.state}</p>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {d.state === 'draft' && <button className="btn btn-secondary" onClick={() => handlePublish(d.id)}>Publish</button>}
              {d.state === 'archived' && <button className="btn btn-secondary" onClick={() => handlePublish(d.id)}>Republish</button>}
              <button className="btn btn-secondary" onClick={() => handleShare(d.id)}>Share</button>
            </div>
          </div>
        ))}
      </div>
      <p>CSV/XLSX export: create charts and metrics via API for full functionality.</p>
    </div>
  );
}
