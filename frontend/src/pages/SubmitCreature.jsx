import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth, authHeaders } from '../context/AuthContext'
import { CATEGORIES } from '../utils/constants'

const BLANK = {
  common_name: '', scientific_name: '', category: 'fish', diet: '',
  max_length_cm: '', weight: '', lifespan: '', habitat: '',
  migratory: false, about: '', legal_notice: '', encounter_tip: '',
}
const BLANK_CONSERVATION = {
  iucn_level: 'Least Concern', population_trend: 'Stable',
  threat_score: '', aware_fact: '', last_assessed: '',
}
const IUCN_LEVELS = ['Least Concern', 'Near Threatened', 'Vulnerable', 'Endangered', 'Critically Endangered', 'Data Deficient']
const TRENDS = ['Increasing', 'Stable', 'Decreasing', 'Unknown']

export default function SubmitCreature() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(BLANK)
  const [conservation, setConservation] = useState(BLANK_CONSERVATION)
  const [includeConservation, setIncludeConservation] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  if (!user) {
    return (
      <div className="submit-page">
        <div className="submit-gate">
          <p>You must be signed in to submit a species.</p>
          <button className="btn-primary" onClick={() => navigate('/login')}>Sign In</button>
        </div>
      </div>
    )
  }

  const setF = (k) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm(f => ({ ...f, [k]: val }))
  }
  const setC = (k) => (e) => setConservation(c => ({ ...c, [k]: e.target.value }))

  async function submit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    const body = {
      ...form,
      max_length_cm: form.max_length_cm ? parseFloat(form.max_length_cm) : null,
      conservation: includeConservation ? {
        ...conservation,
        threat_score: conservation.threat_score ? parseInt(conservation.threat_score) : null,
      } : null,
    }
    try {
      const r = await fetch('/api/submissions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify(body),
      })
      const data = await r.json()
      if (!r.ok) { setError(data.detail || 'Submission failed'); return }
      setSuccess(true)
    } catch {
      setError('Could not reach server')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="submit-page">
        <div className="submit-gate">
          <p className="submit-success-title">Submission received!</p>
          <p className="submit-success-sub">An admin will review your entry before it goes live.</p>
          <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
            <button className="btn-primary" onClick={() => { setForm(BLANK); setConservation(BLANK_CONSERVATION); setSuccess(false) }}>
              Submit another
            </button>
            <button className="btn-secondary" onClick={() => navigate('/')}>Back to Explore</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="submit-page">
      <div className="submit-header">
        <h2>Submit a Species</h2>
        <p>Your submission will be reviewed by an admin before appearing publicly.</p>
      </div>

      <form className="submit-form" onSubmit={submit}>

        <section className="submit-section">
          <h3 className="submit-section-title">Core Info</h3>
          <div className="submit-grid">
            <label className="submit-label">Common Name *
              <input className="submit-input" value={form.common_name} onChange={setF('common_name')} required />
            </label>
            <label className="submit-label">Scientific Name *
              <input className="submit-input" value={form.scientific_name} onChange={setF('scientific_name')} required />
            </label>
            <label className="submit-label">Category *
              <select className="submit-input" value={form.category} onChange={setF('category')}>
                {CATEGORIES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
              </select>
            </label>
            <label className="submit-label">Diet *
              <input className="submit-input" value={form.diet} onChange={setF('diet')} required placeholder="e.g. Carnivore — fish, squid" />
            </label>
          </div>
        </section>

        <section className="submit-section">
          <h3 className="submit-section-title">Physical Details</h3>
          <div className="submit-grid">
            <label className="submit-label">Max Length (cm)
              <input className="submit-input" type="number" value={form.max_length_cm} onChange={setF('max_length_cm')} />
            </label>
            <label className="submit-label">Weight
              <input className="submit-input" value={form.weight} onChange={setF('weight')} placeholder="e.g. Up to 3 kg" />
            </label>
            <label className="submit-label">Lifespan
              <input className="submit-input" value={form.lifespan} onChange={setF('lifespan')} placeholder="e.g. Up to 20 years" />
            </label>
            <label className="submit-label submit-checkbox-label">
              <input type="checkbox" checked={form.migratory} onChange={setF('migratory')} />
              Migratory species
            </label>
          </div>
        </section>

        <section className="submit-section">
          <h3 className="submit-section-title">Habitat & Behavior</h3>
          <label className="submit-label">Habitat
            <input className="submit-input" value={form.habitat} onChange={setF('habitat')} placeholder="e.g. Rocky intertidal zones, coastal bays" />
          </label>
          <label className="submit-label">About
            <textarea className="submit-textarea" value={form.about} onChange={setF('about')} rows={4} placeholder="Background, ecology, interesting facts…" />
          </label>
          <label className="submit-label">Encounter Tip
            <textarea className="submit-textarea" value={form.encounter_tip} onChange={setF('encounter_tip')} rows={2} />
          </label>
          <label className="submit-label">Legal Notice
            <textarea className="submit-textarea" value={form.legal_notice} onChange={setF('legal_notice')} rows={2} />
          </label>
        </section>

        <section className="submit-section">
          <label className="submit-checkbox-label" style={{ fontSize: '0.95rem', fontWeight: 600 }}>
            <input type="checkbox" checked={includeConservation} onChange={e => setIncludeConservation(e.target.checked)} />
            Include conservation status
          </label>

          {includeConservation && (
            <div className="submit-grid" style={{ marginTop: 16 }}>
              <label className="submit-label">IUCN Level
                <select className="submit-input" value={conservation.iucn_level} onChange={setC('iucn_level')}>
                  {IUCN_LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
                </select>
              </label>
              <label className="submit-label">Population Trend
                <select className="submit-input" value={conservation.population_trend} onChange={setC('population_trend')}>
                  {TRENDS.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </label>
              <label className="submit-label">Threat Score (0–100)
                <input className="submit-input" type="number" min={0} max={100} value={conservation.threat_score} onChange={setC('threat_score')} />
              </label>
              <label className="submit-label">Last Assessed (year)
                <input className="submit-input" value={conservation.last_assessed} onChange={setC('last_assessed')} placeholder="e.g. 2023" />
              </label>
              <label className="submit-label" style={{ gridColumn: '1 / -1' }}>Conservation Awareness Fact *
                <textarea className="submit-textarea" value={conservation.aware_fact} onChange={setC('aware_fact')} rows={3} required={includeConservation} />
              </label>
            </div>
          )}
        </section>

        {error && <p className="auth-error">{error}</p>}

        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'Submitting…' : 'Submit for Review'}
          </button>
          <button className="btn-secondary" type="button" onClick={() => navigate('/')}>Cancel</button>
        </div>
      </form>
    </div>
  )
}
