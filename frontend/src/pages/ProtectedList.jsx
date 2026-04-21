import { useState, useEffect } from 'react'
import { STATUS_COLORS } from '../utils/constants'

const IUCN_FILTERS = ['Critically Endangered', 'Endangered', 'Vulnerable']

export default function ProtectedList() {
  const [creatures, setCreatures] = useState([])
  const [stats, setStats] = useState(null)
  const [iucn, setIucn] = useState('')
  const [category, setCategory] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/protected-stats')
      .then(r => r.ok ? r.json() : null)
      .then(data => setStats(data))
      .catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams()
    if (iucn) params.set('iucn', iucn)
    if (category) params.set('category', category)
    fetch(`/api/protected?${params}`)
      .then((r) => {
        if (!r.ok) throw new Error('Fetch failed')
        return r.json()
      })
      .then((data) => { setCreatures(data); setLoading(false) })
      .catch(() => { setCreatures([]); setLoading(false) })
  }, [iucn, category])

  const statBoxes = stats
    ? [
        { val: stats.total_threatened,         desc: 'Threatened Species' },
        { val: `${stats.critically_endangered}`, desc: 'Critically Endangered' },
        { val: `${stats.pct_declining}%`,        desc: 'Population Declining' },
        { val: `${stats.pct_sharks_threatened}%`,desc: 'Sharks Threatened' },
        { val: `${stats.pct_rays_threatened}%`,  desc: 'Rays Threatened' },
        { val: stats.harvest_banned,             desc: 'Harvest Prohibited' },
      ]
    : [
        { val: '…', desc: 'Threatened Species' },
        { val: '…', desc: 'Critically Endangered' },
        { val: '…', desc: 'Population Declining' },
        { val: '…', desc: 'Sharks Threatened' },
        { val: '…', desc: 'Rays Threatened' },
        { val: '…', desc: 'Harvest Prohibited' },
      ]

  return (
    <div className="protected-page">
      <div className="protected-stats">
        {statBoxes.map((s, i) => (
          <div className="stat-box" key={i}>
            <p className="stat-val">{s.val}</p>
            <p className="stat-desc">{s.desc}</p>
          </div>
        ))}
      </div>

      <div className="protected-filters">
        <button className={`pill ${!iucn ? 'active' : ''}`} onClick={() => setIucn('')}>All</button>
        {IUCN_FILTERS.map((f) => (
          <button key={f} className={`pill ${iucn === f ? 'active' : ''}`} onClick={() => setIucn(f)}>
            {f}
          </button>
        ))}
        {[
          { value: 'fish',      label: 'Fish Only' },
          { value: 'shark',     label: 'Sharks Only' },
          { value: 'ray',       label: 'Rays Only' },
          { value: 'shellfish', label: 'Shellfish Only' },
        ].map(({ value, label }) => (
          <button
            key={value}
            className={`pill ${category === value ? 'active' : ''}`}
            onClick={() => setCategory(category === value ? '' : value)}
          >
            {label}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="state-msg">Loading...</p>
      ) : (
        <div className="table-wrapper">
          <table className="protected-table">
            <thead>
              <tr>
                <th>Species</th>
                <th>Category</th>
                <th>IUCN Status</th>
                <th>Harvest Legal?</th>
                <th>Permit Req.</th>
              </tr>
            </thead>
            <tbody>
              {creatures.map((c) => {
                const iucnLevel = c.conservation?.iucn_level || '—'
                const color = STATUS_COLORS[iucnLevel] || '#9ca3af'
                return (
                  <tr key={c.id}>
                    <td>
                      <div className="ptable-name-cell">
                        <div className="ptable-img">
                          {c.image_url ? (
                            <img src={c.image_url} alt={c.common_name} />
                          ) : (
                            <div className="ptable-img-placeholder">■</div>
                          )}
                        </div>
                        <div>
                          <p className="ptable-common">{c.common_name}</p>
                          <p className="ptable-sci">{c.scientific_name}</p>
                        </div>
                      </div>
                    </td>
                    <td>{c.category.charAt(0).toUpperCase() + c.category.slice(1)}</td>
                    <td>
                      <span className="iucn-tag" style={{ color }}>
                        ● {iucnLevel}
                      </span>
                    </td>
                    <td className={c.regulations?.some((r) => !r.harvest_legal) ? 'status-denied' : 'status-allowed'}>
                      {c.regulations?.length > 0
                        ? c.regulations.some((r) => !r.harvest_legal) ? 'PROHIBITED' : 'Allowed'
                        : '—'}
                    </td>
                    <td>
                      {c.regulations?.length > 0
                        ? c.regulations.some((r) => r.permit_required) ? 'Yes' : 'No'
                        : '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
