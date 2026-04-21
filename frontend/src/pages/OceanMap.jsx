import { useEffect, useState, useRef, useCallback } from 'react'
import { geoNaturalEarth1, geoPath, geoGraticule } from 'd3-geo'
import { feature } from 'topojson-client'
import worldTopo from 'world-atlas/countries-110m.json'

// ── Static geometry (module-level, runs once) ───────────────────────────────

const W = 960, H = 500
const MIN_K = 0.8, MAX_K = 30

const projection = geoNaturalEarth1().scale(153).translate([W / 2, H / 2])
const pathGen     = geoPath(projection)
const SPHERE_D    = pathGen({ type: 'Sphere' })
const GRATICULE_D = pathGen(geoGraticule()())
const LAND_D      = pathGen(feature(worldTopo, worldTopo.objects.land))
const BORDERS_D   = pathGen(feature(worldTopo, worldTopo.objects.countries))

// ── Helpers ─────────────────────────────────────────────────────────────────

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)) }

function zoomStep(prev, factor, cx, cy) {
  const newK  = clamp(prev.k * factor, MIN_K, MAX_K)
  const ratio = newK / prev.k
  return { k: newK, x: cx - (cx - prev.x) * ratio, y: cy - (cy - prev.y) * ratio }
}

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
  const [creatures, setCreatures]   = useState([])
  const [selected, setSelected]     = useState(null)
  const [activeCategory, setActiveCategory] = useState('all')
  const [hovered, setHovered]       = useState(null)   // { pin, mapX, mapY }
  const [tf, setTf]                 = useState({ x: 0, y: 0, k: 1 })
  const [isDragging, setIsDragging] = useState(false)

  const svgRef  = useRef(null)
  const dragRef = useRef(null)   // { startCx, startCy, startTx, startTy }

  useEffect(() => {
    fetch('/api/map-data')
      .then(r => r.json())
      .then(setCreatures)
      .catch(() => {})
  }, [])

  // ── Zoom / pan handlers ───────────────────────────────────────────────────

  // Converts a ClientX/Y into SVG root user-unit coordinates.
  const toSvgCoords = useCallback((cx, cy) => {
    const r = svgRef.current.getBoundingClientRect()
    return [(cx - r.left) / r.width * W, (cy - r.top) / r.height * H]
  }, [])

  // Wheel zoom — attached imperatively so we can call preventDefault.
  const handleWheel = useCallback((e) => {
    e.preventDefault()
    const [mx, my] = toSvgCoords(e.clientX, e.clientY)
    setTf(prev => zoomStep(prev, e.deltaY < 0 ? 1.18 : 1 / 1.18, mx, my))
  }, [toSvgCoords])

  useEffect(() => {
    const svg = svgRef.current
    svg.addEventListener('wheel', handleWheel, { passive: false })
    return () => svg.removeEventListener('wheel', handleWheel)
  }, [handleWheel])

  // Drag pan
  const onMouseDown = (e) => {
    if (e.button !== 0) return
    dragRef.current = { startCx: e.clientX, startCy: e.clientY, startTx: tf.x, startTy: tf.y }
    setIsDragging(true)
    e.preventDefault()
  }

  const onMouseMove = (e) => {
    if (!dragRef.current) return
    const r  = svgRef.current.getBoundingClientRect()
    const dx = (e.clientX - dragRef.current.startCx) / r.width  * W
    const dy = (e.clientY - dragRef.current.startCy) / r.height * H
    setTf(prev => ({ ...prev, x: dragRef.current.startTx + dx, y: dragRef.current.startTy + dy }))
  }

  const onMouseUp = () => { dragRef.current = null; setIsDragging(false) }

  // Double-click zooms in centered on cursor
  const onDblClick = (e) => {
    const [mx, my] = toSvgCoords(e.clientX, e.clientY)
    setTf(prev => zoomStep(prev, 2.5, mx, my))
  }

  // Button zoom — centered on the map
  const zoomIn  = () => setTf(prev => zoomStep(prev, 1.5,     W / 2, H / 2))
  const zoomOut = () => setTf(prev => zoomStep(prev, 1 / 1.5, W / 2, H / 2))
  const reset   = () => setTf({ x: 0, y: 0, k: 1 })

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

  // ── Tooltip position (root SVG coords from map coords + current tf) ───────

  const tooltipPos = hovered
    ? { sx: hovered.mapX * tf.k + tf.x, sy: hovered.mapY * tf.k + tf.y }
    : null

  // ── Render ────────────────────────────────────────────────────────────────

  // Stroke widths that stay visually constant as the map scales
  const sw = (base) => Math.max(0.08, base / tf.k)
  // Pin radius constant in screen space
  const pinR     = 3.5 / tf.k
  const pinRHov  = 5   / tf.k
  const pingR    = 6   / tf.k

  return (
    <div className="ocean-map-page">
      <style>{KEYFRAMES}</style>

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

            {/* Sphere mask — clips transformed content to the globe oval */}
            <mask id="om-sphere-mask" maskUnits="userSpaceOnUse"
              x="0" y="0" width={W} height={H}>
              <path d={SPHERE_D} fill="white" />
            </mask>
          </defs>

          {/* Ocean background (not transformed — always fills the sphere) */}
          <path d={SPHERE_D} fill="url(#om-ocean)" />

          {/* All map content masked to the sphere, then zoomed/panned */}
          <g mask="url(#om-sphere-mask)">
            <g transform={`translate(${tf.x},${tf.y}) scale(${tf.k})`}>

              {/* Graticule */}
              <path d={GRATICULE_D} fill="none" stroke="#0d2e3d" strokeWidth={sw(0.4)} />

              {/* Land */}
              <path d={LAND_D} fill="#1a3a4a" stroke="#122a38" strokeWidth={sw(0.5)} />

              {/* Country borders */}
              <path d={BORDERS_D} fill="none" stroke="#0e2a3a" strokeWidth={sw(0.3)} />

              {/* Pins — pointer events off while dragging to avoid stray hovers */}
              <g style={{ pointerEvents: isDragging ? 'none' : 'auto' }}>
                {pins.map((pin, i) => {
                  const [lat, lng] = pin.coords
                  const pos = projection([lng, lat])
                  if (!pos) return null
                  const [mapX, mapY] = pos
                  const color = CATEGORY_COLORS[pin.creature.category] || '#94a3b8'
                  const isHov = hovered?.pin === pin

                  return (
                    <g
                      key={`${pin.creature.id}-${i}`}
                      transform={`translate(${mapX},${mapY})`}
                      style={{ cursor: 'pointer' }}
                      onMouseEnter={() => setHovered({ pin, mapX, mapY })}
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
                        stroke={isHov ? `rgba(255,255,255,0.5)` : 'rgba(0,0,0,0.4)'}
                        strokeWidth={sw(isHov ? 1 : 0.7)}
                      />
                    </g>
                  )
                })}
              </g>
            </g>
          </g>

          {/* Sphere outline — on top, not transformed */}
          <path d={SPHERE_D} fill="none" stroke="#1a4a6a" strokeWidth="1" />

          {/* Tooltip — rendered in root SVG coords outside the group */}
          {hovered && tooltipPos && (() => {
            const { pin }  = hovered
            const { sx, sy } = tooltipPos
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
