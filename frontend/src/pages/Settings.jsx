import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth, authHeaders } from '../context/AuthContext'

const ROLES = [
  { id: 'enthusiast',       label: 'Enthusiast',       desc: 'Ocean lover, diver, or curious explorer' },
  { id: 'fisher',           label: 'Fisher',            desc: 'Recreational or commercial fisherman' },
  { id: 'marine_biologist', label: 'Marine Biologist',  desc: 'Marine scientist or researcher — requires verification', locked: true },
]

const MB_STATUS_LABELS = {
  pending:  { text: 'Verification Pending', color: '#f59e0b' },
  approved: { text: 'Verified',             color: '#22c55e' },
  rejected: { text: 'Verification Rejected', color: '#ef4444' },
}

const APP_STATUS = {
  pending:  { text: 'Application Pending Review', color: '#f59e0b' },
  approved: { text: 'Application Approved',        color: '#22c55e' },
  rejected: { text: 'Application Rejected',        color: '#ef4444' },
}

export default function Settings() {
  const { user, updateUser } = useAuth()
  const navigate = useNavigate()

  // Role section
  const [selectedType, setSelectedType] = useState(user?.user_type || 'enthusiast')
  const [mbCred, setMbCred]             = useState(user?.mb_credential || '')
  const [roleMsg, setRoleMsg]           = useState('')
  const [roleSaving, setRoleSaving]     = useState(false)

  // Password section
  const [currentPw, setCurrentPw]   = useState('')
  const [newPw, setNewPw]           = useState('')
  const [confirmPw, setConfirmPw]   = useState('')
  const [pwMsg, setPwMsg]           = useState('')
  const [pwSaving, setPwSaving]     = useState(false)

  // Admin application section
  const [application, setApplication]     = useState(undefined)  // undefined = loading
  const [appMotivation, setAppMotivation] = useState('')
  const [appExperience, setAppExperience] = useState('')
  const [appMsg, setAppMsg]               = useState('')
  const [appSaving, setAppSaving]         = useState(false)

  // Refresh user data from server on mount so role/status is current
  useEffect(() => {
    if (!user) return
    fetch('/api/auth/me', { headers: authHeaders() })
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data) updateUser(data) })
      .catch(() => {})
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch current admin application status
  useEffect(() => {
    if (!user) return
    fetch('/api/admin-applications/my', { headers: authHeaders() })
      .then(r => r.ok ? r.json() : null)
      .then(data => setApplication(data))
      .catch(() => setApplication(null))
  }, [user?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!user) {
    return (
      <div className="settings-gate">
        <p>You must be signed in to view settings.</p>
        <button className="btn-primary" onClick={() => navigate('/login')}>Sign In</button>
      </div>
    )
  }

  const mbBadge    = user.mb_status ? MB_STATUS_LABELS[user.mb_status] : null
  const roleChanged = selectedType !== user.user_type ||
    (selectedType === 'marine_biologist' && mbCred !== (user.mb_credential || ''))

  async function saveRole(e) {
    e.preventDefault()
    setRoleMsg('')
    setRoleSaving(true)
    const body = { user_type: selectedType }
    if (selectedType === 'marine_biologist') body.mb_credential = mbCred
    const r = await fetch('/api/auth/me', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(body),
    })
    const data = await r.json()
    setRoleSaving(false)
    if (!r.ok) {
      setRoleMsg(Array.isArray(data.detail) ? data.detail.map(e => e.msg).join(', ') : (data.detail || 'Error saving'))
    } else {
      updateUser(data)
      setRoleMsg(selectedType === 'marine_biologist' ? 'Credentials submitted — pending admin review.' : 'Role updated.')
    }
  }

  async function savePassword(e) {
    e.preventDefault()
    setPwMsg('')
    if (newPw !== confirmPw) { setPwMsg('Passwords do not match'); return }
    setPwSaving(true)
    const r = await fetch('/api/auth/me', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ current_password: currentPw, new_password: newPw }),
    })
    const data = await r.json()
    setPwSaving(false)
    if (!r.ok) {
      setPwMsg(Array.isArray(data.detail) ? data.detail.map(e => e.msg).join(', ') : (data.detail || 'Error saving'))
    } else {
      setPwMsg('Password updated.')
      setCurrentPw(''); setNewPw(''); setConfirmPw('')
    }
  }

  async function submitApplication(e) {
    e.preventDefault()
    setAppMsg('')
    setAppSaving(true)
    const r = await fetch('/api/admin-applications', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ motivation: appMotivation, experience: appExperience || undefined }),
    })
    const data = await r.json()
    setAppSaving(false)
    if (!r.ok) {
      setAppMsg(Array.isArray(data.detail) ? data.detail.map(e => e.msg).join(', ') : (data.detail || 'Error submitting'))
    } else {
      setApplication(data)
      setAppMotivation('')
      setAppExperience('')
      setAppMsg('Application submitted! An admin will review it soon.')
    }
  }

  const appStatus = application ? APP_STATUS[application.status] : null
  const canApply  = application === null || application?.status === 'rejected'

  return (
    <div className="settings-page">
      <div className="settings-inner">
        <h2 className="settings-title">Account Settings</h2>

        {/* Profile */}
        <div className="settings-section">
          <p className="settings-section-title">Profile</p>
          <div className="settings-profile-row">
            <div className="settings-field">
              <span className="settings-field-label">Username</span>
              <span className="settings-field-value">{user.username}</span>
            </div>
            <div className="settings-field">
              <span className="settings-field-label">Email</span>
              <span className="settings-field-value">{user.email}</span>
            </div>
            <div className="settings-field">
              <span className="settings-field-label">Account type</span>
              <span className="settings-field-value" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {ROLES.find(r => r.id === user.user_type)?.label || user.user_type}
                {mbBadge && (
                  <span className="mb-badge" style={{ color: mbBadge.color, borderColor: mbBadge.color }}>
                    {mbBadge.text}
                  </span>
                )}
              </span>
            </div>
            <div className="settings-field">
              <span className="settings-field-label">Site role</span>
              <span className="settings-field-value" style={{ textTransform: 'capitalize' }}>{user.role}</span>
            </div>
          </div>
          {user.mb_status === 'rejected' && (
            <p className="settings-note settings-note-warn">
              Your Marine Biologist verification was rejected. Update your credentials below and resubmit.
            </p>
          )}
        </div>

        {/* Role picker */}
        <form className="settings-section" onSubmit={saveRole}>
          <p className="settings-section-title">User Role</p>
          <div className="role-picker">
            {ROLES.map(role => (
              <button
                key={role.id}
                type="button"
                className={`role-card ${selectedType === role.id ? 'selected' : ''}`}
                onClick={() => setSelectedType(role.id)}
              >
                <p className="role-card-title">{role.label}</p>
                <p className="role-card-desc">{role.desc}</p>
                {role.locked && <p className="role-card-lock">Requires verification</p>}
              </button>
            ))}
          </div>

          {selectedType === 'marine_biologist' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <label className="settings-field-label">
                Credentials / Institution
                <span style={{ color: '#64748b', fontWeight: 400, marginLeft: 6 }}>
                  (describe your role, institution, or relevant experience)
                </span>
              </label>
              <textarea
                className="submit-textarea submit-input"
                rows={3}
                value={mbCred}
                onChange={e => setMbCred(e.target.value)}
                placeholder="e.g. PhD candidate at University of Delaware, focusing on mid-Atlantic shark ecology"
                required
              />
            </div>
          )}

          {roleMsg && (
            <p className="settings-msg" style={{ color: roleMsg.includes('Pending') || roleMsg.includes('updated') ? '#22c55e' : '#ef4444' }}>
              {roleMsg}
            </p>
          )}
          <div>
            <button className="btn-primary" type="submit" disabled={roleSaving || !roleChanged}>
              {roleSaving ? 'Saving…' : 'Save Role'}
            </button>
          </div>
        </form>

        {/* Password */}
        <form className="settings-section" onSubmit={savePassword}>
          <p className="settings-section-title">Change Password</p>
          <div className="settings-pw-grid">
            <label className="auth-label">
              Current Password
              <input className="auth-input" type="password" value={currentPw} onChange={e => setCurrentPw(e.target.value)} required />
            </label>
            <label className="auth-label">
              New Password <span style={{ color: '#475569', fontWeight: 400 }}>(min 8 characters)</span>
              <input className="auth-input" type="password" value={newPw} onChange={e => setNewPw(e.target.value)} required minLength={8} maxLength={72} />
            </label>
            <label className="auth-label">
              Confirm New Password
              <input className="auth-input" type="password" value={confirmPw} onChange={e => setConfirmPw(e.target.value)} required />
            </label>
          </div>
          {pwMsg && (
            <p className="settings-msg" style={{ color: pwMsg === 'Password updated.' ? '#22c55e' : '#ef4444' }}>
              {pwMsg}
            </p>
          )}
          <div>
            <button className="btn-primary" type="submit" disabled={pwSaving}>
              {pwSaving ? 'Saving…' : 'Update Password'}
            </button>
          </div>
        </form>

        {/* Admin application — not shown for existing admins */}
        {user.role !== 'admin' && (
          <div className="settings-section">
            <div className="app-section-header">
              <div>
                <p className="settings-section-title">Become a Contributor Admin</p>
                <p className="app-section-desc">
                  Help our team review species submissions and verify Marine Biologist credentials.
                  Admin volunteers must demonstrate commitment to marine conservation.
                </p>
              </div>
            </div>

            {/* Loading state */}
            {application === undefined && (
              <p style={{ color: '#64748b', fontSize: '0.875rem' }}>Loading…</p>
            )}

            {/* Has an application — show status */}
            {application !== undefined && application !== null && (
              <div className="app-status-card" style={{ borderColor: appStatus?.color }}>
                <div className="app-status-row">
                  <span className="app-status-badge" style={{ color: appStatus?.color, borderColor: appStatus?.color }}>
                    {appStatus?.text}
                  </span>
                  <span className="app-status-date">
                    Submitted {new Date(application.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="app-motivation-preview">{application.motivation}</p>
                {application.review_note && (
                  <p className="settings-note settings-note-warn" style={{ marginTop: 8 }}>
                    Admin note: {application.review_note}
                  </p>
                )}
                {application.status === 'approved' && (
                  <p className="settings-note" style={{ background: 'rgba(34,197,94,0.08)', color: '#22c55e', borderLeft: '3px solid #22c55e', marginTop: 8 }}>
                    Your application was approved. Sign out and back in to activate admin access.
                  </p>
                )}
              </div>
            )}

            {/* No application or rejected — show form */}
            {application !== undefined && canApply && (
              <form onSubmit={submitApplication} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {application?.status === 'rejected' && (
                  <p style={{ fontSize: '0.84rem', color: '#94a3b8' }}>
                    Your previous application was rejected. You're welcome to apply again.
                  </p>
                )}
                <label className="auth-label" style={{ gap: 6, display: 'flex', flexDirection: 'column' }}>
                  Why do you want to become a contributor admin?
                  <span style={{ color: '#64748b', fontWeight: 400, fontSize: '0.75rem' }}>Required — tell us about your commitment to marine conservation</span>
                  <textarea
                    className="submit-textarea submit-input"
                    rows={4}
                    value={appMotivation}
                    onChange={e => setAppMotivation(e.target.value)}
                    placeholder="e.g. I've been diving the mid-Atlantic coast for 12 years and care deeply about protecting local species. I want to help ensure submissions are accurate and meaningful."
                    required
                  />
                </label>
                <label className="auth-label" style={{ gap: 6, display: 'flex', flexDirection: 'column' }}>
                  Relevant background or experience
                  <span style={{ color: '#64748b', fontWeight: 400, fontSize: '0.75rem' }}>Optional — biology, conservation, fishing, diving, etc.</span>
                  <textarea
                    className="submit-textarea submit-input"
                    rows={3}
                    value={appExperience}
                    onChange={e => setAppExperience(e.target.value)}
                    placeholder="e.g. PADI divemaster, 10 years recreational fishing on the Jersey Shore, volunteer with a local reef monitoring group."
                  />
                </label>
                {appMsg && (
                  <p className="settings-msg" style={{ color: appMsg.includes('submitted') ? '#22c55e' : '#ef4444' }}>
                    {appMsg}
                  </p>
                )}
                <div>
                  <button className="btn-primary" type="submit" disabled={appSaving || !appMotivation.trim()}>
                    {appSaving ? 'Submitting…' : 'Submit Application'}
                  </button>
                </div>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
