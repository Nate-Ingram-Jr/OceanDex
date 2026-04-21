import { useEffect, useState, useRef, useCallback, useMemo } from 'react'
import { geoNaturalEarth1, geoPath, geoGraticule } from 'd3-geo'
import { feature } from 'topojson-client'
import worldTopo from 'world-atlas/countries-110m.json'

// ── Module-level topology (never changes) ────────────────────────────────────

const W = 960, H = 500
const BASE_SCALE  = 153
const MIN_ZOOM    = 0.8
const MAX_ZOOM    = 20

const landFeature      = feature(worldTopo, worldTopo.objects.land)
const countriesFeature = feature(worldTopo, worldTopo.objects.countries)
const graticuleFeature = geoGraticule()()

// ── Helpers ──────────────────────────────────────────────────────────────────

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)) }

// ── Constants ────────────────────────────────────────────────────────────────

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

const KEYFRAMES = `
  @keyframes om-ping {
    0%   { transform: scale(1);   opacity: 0.65; }
    100% { transform: scale(3.2); opacity: 0;    }
  }
`

// ── Component ────────────────────────────────────────────────────────────────

export default function OceanMap() {
  const [creatures, setCreatures]           = useState([])
  const [selected, setSelected]             = useState(null)
  const [activeCategory, setActiveCategory] = useState('all')
  const [hovered, setHovered]               = useState(null)  // { pin }
  const [zoom, setZoom]                     = useState(1)     // scale multiplier
  const [rot, setRot]                       = useState([0, 0]) // [λ, φ] longitude/latitude rotation
  const [isDragging, setIsDragging]         = useState(false)

  const svgRef  = useRef(null)
  const dragRef = useRef(null)  // { cx, cy, rot: [λ, φ] }

  useEffect(() => {
    fetch('/api/map-data')
      .then(r => r.json())
      .then(setCreatures)
      .catch(() => {})
  }, [])

  // ── Reactive projection — rebuilds when zoom or rotation changes ──────────
  // d3 rotate([λ, φ]) takes negative values relative to what we store,
  // so we negate: rotate([-λ, -φ]) keeps the convention "rot = center of map".

  const proj = useMemo(() =>
    geoNaturalEarth1()
      .scale(BASE_SCALE * zoom)
      .translate([W / 2, H / 2])
      .rotate([-rot[0], -rot[1]])
  , [zoom, rot])

  const pg       = useMemo(() => geoPath(proj), [proj])
  const sphereD  = useMemo(() => pg({ type: 'Sphere' }), [pg])
  const gratD    = useMemo(() => pg(graticuleFeature), [pg])
  const landD    = useMemo(() => pg(landFeature), [pg])
  const bordersD = useMemo(() => pg(countriesFeature), [pg])

  // ── Zoom ─────────────────────────────────────────────────────────────────

  const handleWheel = useCallback((e) => {
    e.preventDefault()
    setHovered(null)
    setZoom(prev => clamp(prev * (e.deltaY < 0 ? 1.18 : 1 / 1.18), MIN_ZOOM, MAX_ZOOM))
  }, [])

  useEffect(() => {
    const svg = svgRef.current
    svg.addEventListener('wheel', handleWheel, { passive: false })
    return () => svg.removeEventListener('wheel', handleWheel)
  }, [handleWheel])

  // ── Drag-to-rotate ───────────────────────────────────────────────────────
  // Converts pixel delta to degree delta using the current projection scale.
  // Longitude (λ) wraps naturally — no clamping needed.
  // Latitude  (φ) is clamped to [-62, 62] to avoid polar flip.

  const onMouseDown = (e) => {
    if (e.button !== 0) return
    dragRef.current = { cx: e.clientX, cy: e.clientY, rot: [...rot] }
    setIsDragging(true)
    e.preventDefault()
  }

  const onMouseMove = (e) => {
    if (!dragRef.current) return
    const r     = svgRef.current.getBoundingClientRect()
    const scale = BASE_SCALE * zoom
    // pixel → SVG user unit → degrees
    const dx = (e.clientX - dragRef.current.cx) * W / r.width
    const dy = (e.clientY - dragRef.current.cy) * H / r.height
    const dλ = -dx * 180 / (scale * Math.PI)
    const dφ =  dy * 180 / (scale * Math.PI) * 0.55   // slight vertical damping
    setRot([
      dragRef.current.rot[0] + dλ,
      clamp(dragRef.current.rot[1] + dφ, -62, 62),
    ])
  }

  const onMouseUp = () => { dragRef.current = null; setIsDragging(false) }

  const onDblClick = () => setZoom(prev => clamp(prev * 2.5, MIN_ZOOM, MAX_ZOOM))

  const zoomIn  = () => setZoom(prev => clamp(prev * 1.5,     MIN_ZOOM, MAX_ZOOM))
  const zoomOut = () => setZoom(prev => clamp(prev / 1.5,     MIN_ZOOM, MAX_ZOOM))
  const reset   = () => { setZoom(1); setRot([0, 0]) }

  // ── Build pin list ────────────────────────────────────────────────────────

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
      pins.push({ coords: [...coords], creature, assoc: a, regionKey: key })
    })
  })

  const regionIndexes = {}
  pins.forEach(pin => {
    const key   = pin.regionKey
    const total = regionCounts[key]
    const idx   = regionIndexes[key] ?? 0
    regionIndexes[key] = idx + 1
    if (total > 1) {
      const angle  = (2 * Math.PI * idx) / total
      const radius = 0.08 + Math.floor(idx / 8) * 0.05
      pin.coords = [
        pin.coords[0] + radius * Math.cos(angle),
        pin.coords[1] + radius * Math.sin(angle),
      ]
    }
  })

  // ── Render ────────────────────────────────────────────────────────────────

  // Stroke widths scale down with zoom to keep geo lines crisp; pins stay constant
  const sw      = (base) => Math.max(0.08, base / zoom)
  const pinR    = 3.5
  const pinRHov = 5
  const pingR   = 6

  // Tooltip: compute position fresh each render using current proj
  const hovPos = hovered ? proj([hovered.pin.coords[1], hovered.pin.coords[0]]) : null

  return (
    <div className="ocean-map-page">
      <style>{KEYFRAMES}</style>

      <div className="map-header">
        <h2>Ocean Map</h2>
        <p>Drag to rotate · Scroll to zoom · Double-click to zoom in</p>
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

      {/* Map area */}
      <div className="map-wrapper" style={{ position: 'relative' }}>

        {/* Zoom controls */}
        <div style={styles.zoomControls}>
          <button style={styles.zoomBtn} onClick={zoomIn}  title="Zoom in">+</button>
          <button style={styles.zoomBtn} onClick={zoomOut} title="Zoom out">−</button>
          <button style={{ ...styles.zoomBtn, fontSize: 13 }} onClick={reset} title="Reset view">⊙</button>
        </div>

        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          preserveAspectRatio="xMidYMid meet"
          style={{ width: '100%', height: '100%', display: 'block', cursor: isDragging ? 'grabbing' : 'grab' }}
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={() => { onMouseUp(); setHovered(null) }}
          onDoubleClick={onDblClick}
        >
          <defs>
            <radialGradient id="om-ocean" cx="50%" cy="45%" r="70%">
              <stop offset="0%"   stopColor="#0d3c64" />
              <stop offset="100%" stopColor="#04121f" />
            </radialGradient>

            {/* Sphere mask — clips all content to the globe outline */}
            <mask id="om-sphere-mask" maskUnits="userSpaceOnUse"
              x="0" y="0" width={W} height={H}>
              <path d={sphereD} fill="white" />
            </mask>
          </defs>

          {/* Ocean fill (behind everything) */}
          <path d={sphereD} fill="url(#om-ocean)" />

          {/* All geographic content clipped to the sphere */}
          <g mask="url(#om-sphere-mask)">
            <path d={gratD}    fill="none" stroke="#0d2e3d" strokeWidth={sw(0.4)} />
            <path d={landD}    fill="#1a3a4a" stroke="#122a38" strokeWidth={sw(0.5)} />
            <path d={bordersD} fill="none"    stroke="#0e2a3a" strokeWidth={sw(0.3)} />

            {/* Pins */}
            <g style={{ pointerEvents: isDragging ? 'none' : 'auto' }}>
              {pins.map((pin, i) => {
                const [lat, lng] = pin.coords
                const pos = proj([lng, lat])
                if (!pos) return null
                const [mapX, mapY] = pos
                const color = CATEGORY_COLORS[pin.creature.category] || '#94a3b8'
                const isHov = hovered?.pin === pin

                return (
                  <g
                    key={`${pin.creature.id}-${i}`}
                    transform={`translate(${mapX},${mapY})`}
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={() => setHovered({ pin })}
                    onMouseLeave={() => setHovered(null)}
                  >
                    {isHov && (
                      <circle
                        r={pingR}
                        fill="none"
                        stroke={color}
                        strokeOpacity="0.45"
                        strokeWidth={sw(1.5)}
                        style={{ animation: 'om-ping 1.4s ease-out infinite', transformOrigin: '0px 0px' }}
                      />
                    )}
                    <circle
                      r={isHov ? pinRHov : pinR}
                      fill={color}
                      opacity={isHov ? 1 : 0.85}
                      stroke={isHov ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.4)'}
                      strokeWidth={sw(isHov ? 1 : 0.7)}
                    />
                  </g>
                )
              })}
            </g>
          </g>

          {/* Sphere outline — always on top */}
          <path d={sphereD} fill="none" stroke="#1a4a6a" strokeWidth="1" />

          {/* Tooltip — rendered in root SVG coords, always current via proj */}
          {hovered && hovPos && (() => {
            const { pin } = hovered
            const [sx, sy] = hovPos
            const lines = [
              pin.creature.common_name,
              pin.assoc.region?.name,
              pin.assoc.abundance   ? `Abundance: ${pin.assoc.abundance}`  : null,
              pin.assoc.best_season ? `Season: ${pin.assoc.best_season}`   : null,
            ].filter(Boolean)

            const BOX_W  = 180
            const LINE_H = 16
            const PAD    = 10
            const BOX_H  = lines.length * LINE_H + PAD * 2 - 4
            const showAbove = sy > BOX_H + 16
            const tipX = clamp(sx + 10, 4, W - BOX_W - 4)
            const tipY = showAbove ? sy - BOX_H - 10 : sy + 10

            return (
              <g pointerEvents="none">
                <rect
                  x={tipX} y={tipY} width={BOX_W} height={BOX_H} rx="4"
                  fill="rgba(4,18,31,0.93)" stroke="rgba(91,200,245,0.25)" strokeWidth="1"
                />
                {lines.map((line, i) => (
                  <text
                    key={i}
                    x={tipX + PAD}
                    y={tipY + PAD + 4 + i * LINE_H}
                    fontSize="11"
                    fill={i === 0 ? '#5bc8f5' : 'rgba(200,235,255,0.65)'}
                    fontWeight={i === 0 ? 'bold' : 'normal'}
                    fontFamily="monospace"
                  >
                    {line}
                  </text>
                ))}
              </g>
            )
          })()}
        </svg>
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

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = {
  zoomControls: {
    position:      'absolute',
    top:           12,
    right:         12,
    zIndex:        10,
    display:       'flex',
    flexDirection: 'column',
    gap:           4,
  },
  zoomBtn: {
    width:           30,
    height:          30,
    background:      'rgba(4,18,31,0.88)',
    border:          '1px solid rgba(91,200,245,0.22)',
    color:           '#5bc8f5',
    borderRadius:    5,
    cursor:          'pointer',
    fontSize:        18,
    fontWeight:      'bold',
    lineHeight:      1,
    display:         'flex',
    alignItems:      'center',
    justifyContent:  'center',
    padding:         0,
    userSelect:      'none',
  },
}
