import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth, authHeaders } from '../context/AuthContext'

const STATUS_LABELS = { pending: 'Pending', approved: 'Approved', rejected: 'Rejected' }
const STATUS_COLORS = { pending: '#f59e0b', approved: '#22c55e', rejected: '#ef4444' }

export default function AdminDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [tab, setTab] = useState('pending')
  const [submissions, setSubmissions] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)
  const [rejectNote, setRejectNote] = useState('')
  const [rejectTarget, setRejectTarget] = useState(null)
  const [actionLoading, setActionLoading] = useState(false)

  if (user && user.role !== 'admin') {
    return (
      <div className="admin-gate">
        <p>Admin access required.</p>
        <button className="btn-secondary" onClick={() => navigate('/')}>Go back</button>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="admin-gate">
        <p>You must be signed in as an admin.</p>
        <button className="btn-primary" onClick={() => navigate('/login')}>Sign In</button>
      </div>
    )
  }

  const load = useCallback(async () => {
    setLoading(true)
    const r = await fetch(`/api/submissions?status=${tab}`, { headers: authHeaders() })
    if (r.ok) setSubmissions(await r.json())
    setLoading(false)
  }, [tab])

  useEffect(() => { load() }, [load])

  async function approve(id) {
    setActionLoading(true)
    await fetch(`/api/submissions/${id}/approve`, { method: 'POST', headers: authHeaders() })
    setActionLoading(false)
    setExpanded(null)
    load()
  }

  async function reject(id) {
    setActionLoading(true)
    const url = `/api/submissions/${id}/reject${rejectNote ? `?note=${encodeURIComponent(rejectNote)}` : ''}`
    await fetch(url, { method: 'POST', headers: authHeaders() })
    setActionLoading(false)
    setRejectTarget(null)
    setRejectNote('')
    load()
  }

  const pending = submissions.filter(s => s.status === 'pending').length

  return (
    <div className="admin-page">
      <div className="admin-header">
        <div>
          <h2>Admin Dashboard</h2>
          <p>Review and manage species submissions</p>
        </div>
        {tab === 'pending' && pending > 0 && (
          <span className="admin-badge">{pending} pending</span>
        )}
      </div>

      <div className="admin-tabs">
        {['pending', 'approved', 'rejected'].map(s => (
          <button
            key={s}
            className={`admin-tab ${tab === s ? 'active' : ''}`}
            onClick={() => { setTab(s); setExpanded(null) }}
          >
            {STATUS_LABELS[s]}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="admin-empty">Loading…</p>
      ) : submissions.length === 0 ? (
        <p className="admin-empty">No {tab} submissions.</p>
      ) : (
        <div className="admin-list">
          {submissions.map(sub => {
            const cd = sub.creature_data
            const isOpen = expanded === sub.id
            return (
              <div key={sub.id} className={`admin-card ${isOpen ? 'open' : ''}`}>
                <div className="admin-card-header" onClick={() => setExpanded(isOpen ? null : sub.id)}>
                  <div className="admin-card-meta">
                    <span className="admin-card-name">{cd.common_name}</span>
                    <span className="admin-card-sci">{cd.scientific_name}</span>
                    <span className="admin-card-cat">{cd.category}</span>
                  </div>
                  <div className="admin-card-right">
                    <span className="admin-card-submitter">by {sub.submitter.username}</span>
                    <span className="admin-card-date">{new Date(sub.created_at).toLocaleDateString()}</span>
                    <span className="admin-status-dot" style={{ background: STATUS_COLORS[sub.status] }} />
                    <span className="admin-chevron">{isOpen ? '▲' : '▼'}</span>
                  </div>
                </div>

                {isOpen && (
                  <div className="admin-card-body">
                    <div className="admin-detail-grid">
                      {cd.diet       && <Field label="Diet"      value={cd.diet} />}
                      {cd.habitat    && <Field label="Habitat"   value={cd.habitat} />}
                      {cd.lifespan   && <Field label="Lifespan"  value={cd.lifespan} />}
                      {cd.weight     && <Field label="Weight"    value={cd.weight} />}
                      {cd.max_length_cm && <Field label="Max Length" value={`${cd.max_length_cm} cm`} />}
                      <Field label="Migratory" value={cd.migratory ? 'Yes' : 'No'} />
                    </div>
                    {cd.about && (
                      <div className="admin-detail-block">
                        <span className="admin-field-label">About</span>
                        <p className="admin-field-text">{cd.about}</p>
                      </div>
                    )}
                    {cd.conservation && (
                      <div className="admin-detail-block">
                        <span className="admin-field-label">Conservation</span>
                        <p className="admin-field-text">
                          {cd.conservation.iucn_level} · {cd.conservation.population_trend}
                          {cd.conservation.threat_score != null && ` · Score: ${cd.conservation.threat_score}`}
                        </p>
                        {cd.conservation.aware_fact && (
                          <p className="admin-field-text" style={{ marginTop: 4 }}>{cd.conservation.aware_fact}</p>
                        )}
                      </div>
                    )}
                    {sub.review_note && (
                      <div className="admin-detail-block">
                        <span className="admin-field-label">Review Note</span>
                        <p className="admin-field-text">{sub.review_note}</p>
                      </div>
                    )}

                    {sub.status === 'pending' && (
                      <>
                        {rejectTarget === sub.id ? (
                          <div className="admin-reject-box">
                            <textarea
                              className="submit-textarea"
                              placeholder="Reason for rejection (optional)"
                              value={rejectNote}
                              onChange={e => setRejectNote(e.target.value)}
                              rows={2}
                            />
                            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                              <button className="btn-danger" disabled={actionLoading} onClick={() => reject(sub.id)}>
                                Confirm Reject
                              </button>
                              <button className="btn-secondary" onClick={() => { setRejectTarget(null); setRejectNote('') }}>
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="admin-actions">
                            <button className="btn-approve" disabled={actionLoading} onClick={() => approve(sub.id)}>
                              Approve &amp; Publish
                            </button>
                            <button className="btn-danger" disabled={actionLoading} onClick={() => setRejectTarget(sub.id)}>
                              Reject
                            </button>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function Field({ label, value }) {
  return (
    <div className="admin-field">
      <span className="admin-field-label">{label}</span>
      <span className="admin-field-value">{value}</span>
    </div>
  )
}
