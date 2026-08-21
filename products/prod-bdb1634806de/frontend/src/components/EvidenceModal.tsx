

interface EvidenceModalProps {
  receipt?: string;
  onClose: () => void;
}

export default function EvidenceModal({ receipt, onClose }: EvidenceModalProps) {
  if (!receipt) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal" onClick={e => e.stopPropagation()}>
          <h3>No receipt available</h3>
          <p>This advisory has no signed evidence.</p>
          <button className="btn" onClick={onClose}>Close</button>
        </div>
      </div>
    );
  }
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h3>Evidence Receipt</h3>
        <pre style={{ overflowX: 'auto', padding: '1rem', background: 'var(--surface-2)', borderRadius: '8px' }}>
          {receipt}
        </pre>
        <button className="btn" onClick={onClose}>Close</button>
      </div>
    </div>
  );
}
