import { AdvisoryResponse } from '../api/advisory';

interface ThresholdPanelProps {
  thresholds: AdvisoryResponse['thresholds'];
}

export default function ThresholdPanel({ thresholds }: ThresholdPanelProps) {
  return (
    <div className="card" style={{ marginTop: '1rem' }}>
      <h3>How this was decided</h3>
      <ul style={{ listStyle: 'none', marginTop: '0.5rem' }}>
        {thresholds.map((t, idx) => (
          <li key={idx} style={{ padding: '0.5rem 0', borderBottom: '1px solid var(--border)' }}>
            <strong>{t.name}</strong>: {t.condition} {t.fired ? '🔥' : '✓'}
          </li>
        ))}
      </ul>
    </div>
  );
}
