
interface StatusRingProps {
  level: string;
  isCached?: boolean;
}

export default function StatusRing({ level, isCached = false }: StatusRingProps) {
  return (
    <div className={`status-ring ${isCached ? 'status-ring-cached' : ''}`} data-level={isCached ? 'CACHED' : level}>
      {level}
    </div>
  );
}
