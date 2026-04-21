import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

const REGION_COORDS = {
  'Chesapeake Bay':            [37.8,  -76.1],
  'Ocean City Atlantic Coast': [38.33, -74.9],
  'Delaware Bay':              [39.1,  -75.35],
  'Rehoboth Beach Shelf':      [38.65, -74.95],
  'Sandy Hook Bay':            [40.45, -74.0],
  'Barnegat Bay':              [39.77, -74.1],
  'NJ Atlantic Shelf':         [39.4,  -73.6],
}

const CATEGORY_COLORS = {
  fish:      '#38bdf8',
  shark:     '#f87171',
  ray:       '#fb923c',
  shellfish: '#a78bfa',
  other:     '#94a3b8',
}

export default function OceanMap() {
  const [creatures, setCreatures] = useState([])
  const [selected, setSelected] = useState(null)
  const [activeCategory, setActiveCategory] = useState('all')

  useEffect(() => {
    fetch('/api/map-data')
      .then(r => r.json())
      .then(setCreatures)
      .catch(() => {})
  }, [])

  const filtered = activeCategory === 'all'
    ? creatures
    : creatures.filter(c => c.category === activeCategory)

  const toShow = selected ? [selected] : filtered

  const regionCounts = {}
  const pins = []
  toShow.forEach(creature => {
    creature.region_associations.forEach(a => {
      const coords = REGION_COORDS[a.region?.name]
      if (!coords) return
      const key = a.region.name
      regionCounts[key] = (regionCounts[key] || 0) + 1
      pins.push({ coords, creature, assoc: a, regionKey: key })
    })
  })

  // Jitter pins that share the same region so they don't overlap
  const regionIndexes = {}
  pins.forEach(pin => {
    const key = pin.regionKey
    const total = regionCounts[key]
    const idx = regionIndexes[key] ?? 0
    regionIndexes[key] = idx + 1
    if (total > 1) {
      const angle = (2 * Math.PI * idx) / total
      const radius = 0.04 + Math.floor(idx / 8) * 0.025
      pin.coords = [
        pin.coords[0] + radius * Math.cos(angle),
        pin.coords[1] + radius * Math.sin(angle),
      ]
    }
  })

  return (
    <div className="ocean-map-page">
      <div className="map-header">
        <h2>Ocean Map</h2>
        <p>Habitat ranges across Maryland, Delaware &amp; New Jersey waters.</p>
      </div>

      <div className="map-controls">
        {['all', 'fish', 'shark', 'ray', 'shellfish'].map(cat => (
          <button
            key={cat}
            className={`map-filter-btn ${activeCategory === cat ? 'active' : ''}`}
            onClick={() => { setActiveCategory(cat); setSelected(null) }}
          >
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}

        <select
          className="map-creature-select"
          value={selected?.id ?? ''}
          onChange={e => {
            const id = parseInt(e.target.value)
            setSelected(creatures.find(c => c.id === id) || null)
            setActiveCategory('all')
          }}
        >
          <option value="">— All species —</option>
          {[...creatures]
            .sort((a, b) => a.common_name.localeCompare(b.common_name))
            .map(c => <option key={c.id} value={c.id}>{c.common_name}</option>)}
        </select>
      </div>

      <div className="map-wrapper">
        <MapContainer center={[39.2, -75.2]} zoom={7} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {pins.map((pin, i) => (
            <CircleMarker
              key={`${pin.creature.id}-${i}`}
              center={pin.coords}
              radius={selected ? 12 : 8}
              pathOptions={{
                fillColor: CATEGORY_COLORS[pin.creature.category] || '#94a3b8',
                fillOpacity: 0.85,
                color: '#1e293b',
                weight: 1.5,
              }}
            >
              <Tooltip direction="top" offset={[0, -6]}>
                <strong>{pin.creature.common_name}</strong><br />
                {pin.assoc.region?.name}
                {pin.assoc.abundance && <><br />Abundance: {pin.assoc.abundance}</>}
              </Tooltip>
              <Popup>
                <div style={{ minWidth: 160 }}>
                  {pin.creature.image_url && (
                    <img src={pin.creature.image_url} alt={pin.creature.common_name}
                      style={{ width: '100%', borderRadius: 4, marginBottom: 6 }} />
                  )}
                  <strong>{pin.creature.common_name}</strong><br />
                  <em style={{ fontSize: '0.8em', color: '#64748b' }}>{pin.creature.scientific_name}</em>
                  <br /><br />
                  <strong>Region:</strong> {pin.assoc.region?.name}<br />
                  {pin.assoc.abundance && <><strong>Abundance:</strong> {pin.assoc.abundance}<br /></>}
                  {pin.assoc.best_season && <><strong>Season:</strong> {pin.assoc.best_season}</>}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="map-legend">
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <span key={cat} className="legend-item">
            <span className="legend-dot" style={{ background: color }} />
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </span>
        ))}
      </div>
    </div>
  )
}
