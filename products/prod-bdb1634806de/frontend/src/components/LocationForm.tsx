import React, { useState } from 'react';

interface LocationFormProps {
  onSubmit: (lat: number, lon: number) => void;
}

export default function LocationForm({ onSubmit }: LocationFormProps) {
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const latNum = parseFloat(lat);
    const lonNum = parseFloat(lon);
    if (!isNaN(latNum) && !isNaN(lonNum)) {
      onSubmit(latNum, lonNum);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div>
        <label htmlFor="lat">Latitude</label>
        <input
          id="lat"
          type="number"
          step="0.1"
          min="-90"
          max="90"
          className="input"
          value={lat}
          onChange={e => setLat(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="lon">Longitude</label>
        <input
          id="lon"
          type="number"
          step="0.1"
          min="-180"
          max="180"
          className="input"
          value={lon}
          onChange={e => setLon(e.target.value)}
          required
        />
      </div>
      <button type="submit" className="btn">Check Safety</button>
      <p className="location-form-note">Location rounded to ~1 decimal degree; exact coordinates not stored.</p>
    </form>
  );
}
