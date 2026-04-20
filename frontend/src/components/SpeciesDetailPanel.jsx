import { useState } from 'react'
import { STATUS_COLORS } from '../utils/constants'

const TABS = ['Overview', 'Legal & Regs', 'Ecology', 'Conservation']

function DepthBar({ minM = 0, maxM }) {
  if (!maxM) return null
  const scale = 4000
  const left = (minM / scale) * 100
  const width = Math.min(((maxM - minM) / scale) * 100, 100 - left)

  return (
    <div className="depth-bar-section">
      <p className="section-label">DEPTH RANGE</p>
      <div className="depth-track">
        <div className="depth-fill" style={{ left: `${left}%`, width: `${width}%` }} />
      </div>
      <div className="depth-labels">
        <span>Surface</span>
        <span>200m</span>
        <span>1,000m</span>
        <span>4,000m</span>
      </div>
    </div>
  )
}

function OverviewTab({ c }) {
  const lengthM = c.max_length_cm ? (c.max_length_cm / 100).toFixed(1) + 'm avg' : '—'
  const trend = c.conservation?.population_trend || '—'

  return (
    <div className="tab-content">
      {c.about && (
        <div className="about-section">
          <p className="section-label">ABOUT</p>
          <div className="about-box">
            <p>{c.about}</p>
          </div>
        </div>
      )}
      <div className="key-facts-section">
        <p className="section-label">KEY FACTS</p>
        <div className="key-facts-grid">
          {c.weight && (
            <div className="fact-item">
              <span className="fact-label">Weight</span>
              <span className="fact-value">{c.weight}</span>
            </div>
          )}
          {c.habitat && (
            <div className="fact-item">
              <span className="fact-label">Habitat</span>
              <span className="fact-value">{c.habitat}</span>
            </div>
          )}
          {c.depth_min_m != null && c.depth_max_m != null && (
            <div className="fact-item">
              <span className="fact-label">Depth Range</span>
              <span className="fact-value">{c.depth_min_m}–{c.depth_max_m}m</span>
            </div>
          )}
          <div className="fact-item">
            <span className="fact-label">Type</span>
            <span className="fact-value">{c.category.charAt(0).toUpperCase() + c.category.slice(1)}</span>
          </div>
          {c.diet && (
            <div className="fact-item">
              <span className="fact-label">Diet</span>
              <span className="fact-value">{c.diet}</span>
            </div>
          )}
          {c.lifespan && (
            <div className="fact-item">
              <span className="fact-label">Lifespan</span>
              <span className="fact-value">{c.lifespan}</span>
            </div>
          )}
        </div>
      </div>
      <DepthBar minM={c.depth_min_m} maxM={c.depth_max_m} />
    </div>
  )
}

function LegalTab({ c }) {
  const regs = c.regulations || []
  const isProtected = regs.some((r) => !r.harvest_legal)
  const hasLimits = regs.some((r) => r.harvest_legal && (r.min_size_cm || r.bag_limit))

  return (
    <div className="tab-content">
      <p className="section-label">LEGAL STATUS & REGULATIONS</p>
      <div className="legal-cards">
        {c.legal_notice && (
          <div className={`legal-card ${isProtected ? 'card-red' : 'card-orange'}`}>
            <p className="legal-card-title">
              {isProtected ? '■ Protected Species — Federal Law' : '■ Harvest Regulations'}
            </p>
            <p>{c.legal_notice}</p>
          </div>
        )}
        {hasLimits && (
          <div className="legal-card card-orange">
            <p className="legal-card-title">■■ Size & Bag Limits</p>
            {regs
              .filter((r) => r.harvest_legal && (r.min_size_cm || r.bag_limit))
              .map((r) => (
                <p key={r.id}>
                  <strong>{r.state.name}:</strong>{' '}
                  {r.min_size_cm ? `Min ${r.min_size_cm}cm` : ''}
                  {r.bag_limit != null ? `, Bag limit: ${r.bag_limit}` : ''}
                </p>
              ))}
          </div>
        )}
        {c.encounter_tip && (
          <div className="legal-card card-blue">
            <p className="legal-card-title">■■ {isProtected ? 'If You Encounter One' : 'Fishing Tips'}</p>
            <p>{c.encounter_tip}</p>
          </div>
        )}
      </div>

      {regs.length > 0 && (
        <>
          <p className="section-label" style={{ marginTop: 24 }}>FISHING REGULATIONS BY REGION</p>
          <div className="table-wrapper">
            <table className="regulations-table">
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Status</th>
                  <th>Min Size</th>
                  <th>Bag Limit</th>
                  <th>Season</th>
                  <th>Permit</th>
                  <th>Authority</th>
                </tr>
              </thead>
              <tbody>
                {regs.map((reg) => (
                  <tr key={reg.id}>
                    <td>{reg.state.name}</td>
                    <td className={reg.harvest_legal ? 'status-allowed' : 'status-denied'}>
                      {reg.harvest_legal ? 'Allowed' : 'PROHIBITED'}
                    </td>
                    <td>{reg.min_size_cm ? `${reg.min_size_cm}cm` : 'N/A'}</td>
                    <td>{reg.bag_limit != null ? reg.bag_limit : '—'}</td>
                    <td>{reg.season || 'N/A'}</td>
                    <td>{reg.permit_required || 'No'}</td>
                    <td>{reg.authority}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}

function EcologyTab({ c }) {
  const assocs = c.region_associations || []

  return (
    <div className="tab-content">
      {c.habitat && (
        <div className="ecology-section">
          <p className="section-label">HABITAT</p>
          <p>{c.habitat}</p>
        </div>
      )}
      <div className="ecology-section">
        <p className="section-label">DIET</p>
        <p>{c.diet}</p>
      </div>
      {c.migratory && (
        <div className="ecology-section">
          <p className="section-label">MIGRATORY</p>
          <p>This species undertakes seasonal migrations.</p>
        </div>
      )}
      {assocs.length > 0 && (
        <div className="ecology-section">
          <p className="section-label">KNOWN REGIONS</p>
          <div className="region-cards">
            {assocs.map((a) => (
              <div key={a.region.id} className="region-card">
                <p className="region-name">{a.region.name}</p>
                <p className="region-state">{a.region.state.name} · {a.region.water_type}</p>
                {a.abundance && <p className="region-detail">Abundance: {a.abundance}</p>}
                {a.best_season && <p className="region-detail">Best season: {a.best_season}</p>}
                {a.depth_notes && <p className="region-detail">{a.depth_notes}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function ConservationTab({ c }) {
  const cons = c.conservation
  if (!cons) return <div className="tab-content"><p>No conservation data available.</p></div>

  const score = cons.threat_score || 0
  const iucn = cons.iucn_level
  const statusColor = STATUS_COLORS[iucn] || '#9ca3af'
  const threats = cons.main_threats || []
  const actions = cons.conservation_actions || []

  return (
    <div className="tab-content">
      <div className="conservation-header">
        <div className="threat-donut-wrap">
          <p className="section-label">THREAT LEVEL</p>
          <div className="threat-donut-row">
            <div
              className="threat-donut"
              style={{
                background: `conic-gradient(${statusColor} ${score}%, #e5e7eb 0)`,
              }}
            >
              <div className="threat-donut-inner">
                <span className="threat-score">{score}%</span>
              </div>
            </div>
            <div className="threat-label-col">
              <p className="threat-iucn" style={{ color: statusColor }}>{iucn}</p>
              <p className="threat-trend">Population trend: {cons.population_trend}</p>
              <p className="threat-sub">Score reflects fishing pressure, habitat loss, and climate change.</p>
            </div>
          </div>
        </div>
      </div>

      {threats.length > 0 && (
        <div className="threats-section">
          <p className="section-label">MAIN THREATS</p>
          {threats.map((t, i) => (
            <div key={i} className="threat-bar-row">
              <span className="threat-bar-label">{t.name}</span>
              <div className="threat-bar-track">
                <div className="threat-bar-fill" style={{ width: `${t.percentage}%` }} />
              </div>
              <span className="threat-bar-pct">{t.percentage}%</span>
            </div>
          ))}
        </div>
      )}

      {cons.aware_fact && (
        <div className="awareness-section">
          <p className="section-label">CONSERVATION AWARENESS</p>
          <div className="awareness-box">
            <strong>Did You Know?</strong>
            <p>{cons.aware_fact}</p>
          </div>
        </div>
      )}

      {actions.length > 0 && (
        <div className="actions-section">
          <p className="section-label">CONSERVATION ACTIONS</p>
          <ul className="actions-list">
            {actions.map((a, i) => (
              <li key={i} className={a.done ? 'action-done' : 'action-pending'}>
                <span className="action-icon">{a.done ? '✓' : '✗'}</span>
                {a.text}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default function SpeciesDetailPanel({ creature }) {
  const [tab, setTab] = useState('Overview')

  const iucn = creature.conservation?.iucn_level
  const statusColor = STATUS_COLORS[iucn] || '#9ca3af'
  const lengthM = creature.max_length_cm ? (creature.max_length_cm / 100).toFixed(1) + 'm avg' : '—'
  const trend = creature.conservation?.population_trend || '—'

  return (
    <div className="detail-panel-content">
      <div className="dp-header">
        <div className="dp-img-wrap">
          {creature.image_url ? (
            <img src={creature.image_url} alt={creature.common_name} className="dp-img" />
          ) : (
            <div className="dp-img-placeholder">■</div>
          )}
        </div>
        <div className="dp-title-wrap">
          <h1 className="dp-name">{creature.common_name}</h1>
          <p className="dp-scientific">{creature.scientific_name}</p>
          <span className="dp-iucn-badge" style={{ backgroundColor: statusColor }}>
            ● {iucn} — IUCN Red List
          </span>
          <div className="dp-stats">
            <div className="dp-stat">
              <span className="dp-stat-val">{lengthM}</span>
              <span className="dp-stat-label">Length</span>
            </div>
            {creature.lifespan && (
              <div className="dp-stat">
                <span className="dp-stat-val">{creature.lifespan}</span>
                <span className="dp-stat-label">Lifespan</span>
              </div>
            )}
            <div className="dp-stat">
              <span className="dp-stat-val">{creature.diet?.split(' — ')[0] || creature.diet}</span>
              <span className="dp-stat-label">Diet</span>
            </div>
            <div className="dp-stat">
              <span className="dp-stat-val">{trend}</span>
              <span className="dp-stat-label">Trend</span>
            </div>
          </div>
        </div>
      </div>

      <div className="dp-tabs">
        {TABS.map((t) => (
          <button
            key={t}
            className={`dp-tab ${tab === t ? 'active' : ''}`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === 'Overview' && <OverviewTab c={creature} />}
      {tab === 'Legal & Regs' && <LegalTab c={creature} />}
      {tab === 'Ecology' && <EcologyTab c={creature} />}
      {tab === 'Conservation' && <ConservationTab c={creature} />}
    </div>
  )
}
