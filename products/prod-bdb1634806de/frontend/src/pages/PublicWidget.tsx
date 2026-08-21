import { useState } from "react";

interface Hazard {
  type: string;
  level: string;
  measurement?: string;
  distance_km?: number;
  receipt?: string;
  timestamp?: string;
  is_cached?: boolean;
  sim?: boolean;
  explanation?: string;
}

interface AdvisoryResponse {
  overall?: { level: string; reason?: string; receipt?: string };
  hazards?: Hazard[];
  thresholds?: { name: string; condition: string; fired: boolean }[];
  location?: { lat: number; lon: number; rounded: boolean };
  cached?: boolean;
  cached_at?: string;
  renews?: string;
}

const levelClass = (level: string) => {
  switch (level.toUpperCase()) {
    case "CALM": return "badge calm";
    case "WATCH": return "badge watch";
    case "WARNING": return "badge warning";
    case "EMERGENCY": return "badge emergency";
    default: return "badge unknown";
  }
};

export default function PublicWidget() {
  const [lat, setLat] = useState<string>("52.52");
  const [lon, setLon] = useState<string>("13.40");
  const [manualCity, setManualCity] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [advisory, setAdvisory] = useState<AdvisoryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [privacyNote] = useState("Location rounded to ~1 decimal degree; exact coordinates not stored.");

  const handleGeolocate = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat((Math.round(pos.coords.latitude * 10) / 10).toFixed(1));
        setLon((Math.round(pos.coords.longitude * 10) / 10).toFixed(1));
      },
      () => {
        alert("Location permission denied. Please enter coordinates manually.");
      }
    );
  };

  const handleCitySearch = async () => {
    if (!manualCity.trim()) return;
    try {
      const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(manualCity)}`);
      const data = await response.json();
      if (data && data.length > 0) {
        setLat((Math.round(parseFloat(data[0].lat) * 10) / 10).toFixed(1));
        setLon((Math.round(parseFloat(data[0].lon) * 10) / 10).toFixed(1));
      }
    } catch {
      alert("City lookup failed. Please enter coordinates manually.");
    }
  };

  const getAdvisory = async () => {
    setLoading(true);
    setError(null);
    try {
      const roundedLat = parseFloat(lat).toFixed(1);
      const roundedLon = parseFloat(lon).toFixed(1);
      const response = await fetch(`/api/advisory?lat=${roundedLat}&lon=${roundedLon}`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data: AdvisoryResponse = await response.json();
      setAdvisory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch advisory");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="public-widget">
      <h1>Sentinel Verified Safety Companion</h1>
      <p className="muted">Weather, wildfire and flood advisory with signed evidence receipts — no black-box AI.</p>

      <div className="card location-form">
        <h2>Your location</h2>
        <p className="muted" style={{ marginBottom: "1rem" }}>{privacyNote}</p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", alignItems: "center" }}>
          <input
            type="text"
            placeholder="City (optional)"
            value={manualCity}
            onChange={(e) => setManualCity(e.target.value)}
            style={{ flex: "1 1 200px" }}
          />
          <button className="btn btn-secondary" onClick={handleCitySearch}>Look up city</button>
          <button className="btn btn-secondary" onClick={handleGeolocate}>Use my location</button>
        </div>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", marginTop: "0.75rem" }}>
          <label>
            Lat:
            <input type="number" step="0.1" value={lat} onChange={(e) => setLat(e.target.value)} style={{ width: "80px" }} />
          </label>
          <label>
            Lon:
            <input type="number" step="0.1" value={lon} onChange={(e) => setLon(e.target.value)} style={{ width: "80px" }} />
          </label>
          <button className="btn" onClick={getAdvisory} disabled={loading}>
            {loading ? "Checking..." : "Get safety report"}
          </button>
        </div>
      </div>

      {error && <div className="card"><p style={{ color: "var(--danger)" }}>Error: {error}</p></div>}

      {advisory && (
        <>
          <div className="card status-ring-card">
            <h2>Overall status</h2>
            {advisory.overall ? (
              <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                <span className={levelClass(advisory.overall.level)}>{advisory.overall.level}</span>
                {advisory.overall.reason && <p className="muted">{advisory.overall.reason}</p>}
              </div>
            ) : (
              <p className="muted">No overall level reported.</p>
            )}
            {advisory.cached && advisory.cached_at && (
              <p className="muted">Cached reading — from {new Date(advisory.cached_at).toLocaleString()}</p>
            )}
            {advisory.renews && <p className="muted">Free allowance renews: {advisory.renews}</p>}
          </div>

          <div className="grid-3">
            {advisory.hazards && advisory.hazards.map((h, i) => (
              <div key={i} className="card hazard-card">
                <h3>{h.type}</h3>
                <span className={levelClass(h.level)}>{h.level}</span>
                {h.measurement && <p>{h.measurement}</p>}
                {h.distance_km !== undefined && <p className="muted">Distance: {h.distance_km.toFixed(1)} km</p>}
                {h.sim && <p className="muted">SIM data</p>}
                {h.explanation && <p className="muted">{h.explanation}</p>}
                {h.receipt && (
                  <details>
                    <summary style={{ cursor: "pointer", color: "var(--accent)" }}>Evidence receipt</summary>
                    <p className="mono" style={{ wordBreak: "break-all" }}>{h.receipt}</p>
                  </details>
                )}
                {h.is_cached && <p className="muted">Cached</p>}
              </div>
            ))}
          </div>

          {advisory.thresholds && advisory.thresholds.length > 0 && (
            <div className="card">
              <h3>How this was decided</h3>
              <ul style={{ listStyle: "none" }}>
                {advisory.thresholds.map((t, i) => (
                  <li key={i} style={{ padding: "0.5rem 0", borderBottom: "1px solid var(--border)" }}>
                    <strong>{t.name}</strong>: {t.condition} — {t.fired ? "fired" : "not fired"}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      <div className="card embed-snippet">
        <h2>Embed Sentinel on your site</h2>
        <p className="muted">Add this script tag to any page:</p>
        <pre className="mono" style={{ background: "var(--surface-2)", padding: "1rem", borderRadius: "8px", overflowX: "auto" }}>
          {`<script src="./api/embed.js"></script>`}
        </pre>
      </div>
    </div>
  );
}
