import { useState, useEffect } from 'react'
import { STATUS_COLORS } from '../utils/constants'

const IUCN_FILTERS = ['Critically Endangered', 'Endangered', 'Vulnerable']

export default function ProtectedList() {
  const [creatures, setCreatures] = useState([])
  const [iucn, setIucn] = useState('')
  const [category, setCategory] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams()
    if (iucn) params.set('iucn', iucn)
    if (category) params.set('category', category)
    fetch(`/api/protected?${params}`)
      .then((r) => r.json())
      .then((data) => { setCreatures(data); setLoading(false) })
  }, [iucn, category])

  const protected_count = creatures.length
  const sharks_threatened = creatures.filter((c) => c.category === 'shark').length

  return (
    <div className="protected-page">
      <div className="protected-stats">
        <div className="stat-box">
          <p className="stat-val">{protected_count}</p>
          <p className="stat-desc">Protected Species</p>
        </div>
        <div className="stat-box">
          <p className="stat-val">31%</p>
          <p className="stat-desc">Sharks Threatened</p>
        </div>
        <div className="stat-box">
          <p className="stat-val">14</p>
          <p className="stat-desc">US States w/ Fin Bans</p>
        </div>
        <div className="stat-box">
          <p className="stat-val">CITES</p>
          <p className="stat-desc">Int'l Framework</p>
        </div>
      </div>

      <div className="protected-filters">
        <button className={`pill ${!iucn ? 'active' : ''}`} onClick={() => setIucn('')}>All</button>
        {IUCN_FILTERS.map((f) => (
          <button key={f} className={`pill ${iucn === f ? 'active' : ''}`} onClick={() => setIucn(f)}>
            {f}
          </button>
        ))}
        <button
          className={`pill ${category === 'shark' ? 'active' : ''}`}
          onClick={() => setCategory(category === 'shark' ? '' : 'shark')}
        >
          Sharks Only
        </button>
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
                    <td className="status-denied">NO</td>
                    <td>N/A</td>
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
