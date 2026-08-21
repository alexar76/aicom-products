

interface HazardCardProps {
  type: string;
  level: string;
  measurement?: string;
  distance_km?: number;
  receipt?: string;
  isCached: boolean;
  sim: boolean;
  onEvidenceClick: () => void;
}

function getLevelClass(level: string): string {
  switch (level) {
    case 'CALM': return 'level-calm';
    case 'WATCH': return 'level-watch';
    case 'WARNING': return 'level-warning';
    case 'EMERGENCY': return 'level-emergency';
    default: return 'level-unknown';
  }
}

function HazardIcon({ type }: { type: string }) {
  switch (type) {
    case 'WEATHER': return <span role="img" aria-label="weather">🌤️</span>;
    case 'WILDFIRE': return <span role="img" aria-label="fire">🔥</span>;
    case 'FLOOD': return <span role="img" aria-label="flood">🌊</span>;
    default: return null;
  }
}

export default function HazardCard({ type, level, measurement, distance_km, isCached, sim, onEvidenceClick }: HazardCardProps) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3><HazardIcon type={type} /> {type}</h3>
        <span className={`level-badge ${getLevelClass(level)}`}>
          {level}
          {isCached && <small>cached</small>}
          {sim && <small>SIM</small>}
        </span>
      </div>
      {measurement && <p>{measurement}</p>}
      {distance_km !== undefined && <p>Distance: {distance_km} km</p>}
      <button className="btn btn-secondary" onClick={onEvidenceClick} style={{ marginTop: '0.5rem' }}>
        Evidence
      </button>
    </div>
  );
}
