import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth, authHeaders } from '../context/AuthContext'

const TAGS = ['fish', 'shark', 'shellfish', 'ray']

export default function SightingsForum() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [selectedTag, setSelectedTag] = useState('all')
  const [sightings, setSightings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [tag, setTag] = useState('fish')
  const [caption, setCaption] = useState('')
  const [image, setImage] = useState(null)
  const [posting, setPosting] = useState(false)
  const [postError, setPostError] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editTag, setEditTag] = useState('fish')
  const [editCaption, setEditCaption] = useState('')
  const [editError, setEditError] = useState('')
  const [actionLoadingId, setActionLoadingId] = useState(null)

  async function loadSightings(tagFilter = selectedTag) {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams()
      if (tagFilter !== 'all') params.set('tag', tagFilter)
      const query = params.toString()
      const r = await fetch(`/api/sightings${query ? `?${query}` : ''}`)
      const data = await r.json()
      if (!r.ok) {
        setError(data.detail || 'Could not load sightings')
        return
      }
      setSightings(data)
    } catch {
      setError('Could not reach server')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSightings(selectedTag)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTag])

  const heading = useMemo(() => {
    if (selectedTag === 'all') return 'All Sightings'
    return `${selectedTag[0].toUpperCase()}${selectedTag.slice(1)} Sightings`
  }, [selectedTag])

  async function submitSighting(e) {
    e.preventDefault()
    setPostError('')

    if (!image) {
      setPostError('Please choose an image to post.')
      return
    }

    setPosting(true)
    try {
      const formData = new FormData()
      formData.append('tag', tag)
      formData.append('caption', caption)
      formData.append('image', image)

      const r = await fetch('/api/sightings', {
        method: 'POST',
        headers: { ...authHeaders() },
        body: formData,
      })
      const data = await r.json()
      if (!r.ok) {
        setPostError(data.detail || 'Could not post sighting')
        return
      }

      setSightings((prev) => [data, ...prev])
      setCaption('')
      setImage(null)
      const input = document.getElementById('sighting-image-input')
      if (input) input.value = ''
    } catch {
      setPostError('Could not reach server')
    } finally {
      setPosting(false)
    }
  }

  function startEdit(item) {
    setEditingId(item.id)
    setEditTag(item.tag)
    setEditCaption(item.caption || '')
    setEditError('')
  }

  function cancelEdit() {
    setEditingId(null)
    setEditTag('fish')
    setEditCaption('')
    setEditError('')
  }

  async function saveEdit(itemId) {
    setActionLoadingId(itemId)
    setEditError('')
    try {
      const r = await fetch(`/api/sightings/${itemId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({ tag: editTag, caption: editCaption }),
      })
      const data = await r.json()
      if (!r.ok) {
        setEditError(data.detail || 'Could not update post')
        return
      }
      setSightings((prev) => prev.map((s) => (s.id === itemId ? data : s)))
      cancelEdit()
    } catch {
      setEditError('Could not reach server')
    } finally {
      setActionLoadingId(null)
    }
  }

  async function deletePost(itemId) {
    const confirmed = window.confirm('Delete this sighting post? This cannot be undone.')
    if (!confirmed) return

    setActionLoadingId(itemId)
    try {
      const r = await fetch(`/api/sightings/${itemId}`, {
        method: 'DELETE',
        headers: { ...authHeaders() },
      })
      if (!r.ok && r.status !== 204) {
        let detail = 'Could not delete post'
        try {
          const data = await r.json()
          detail = data.detail || detail
        } catch {
          // no-op
        }
        setError(detail)
        return
      }
      setSightings((prev) => prev.filter((s) => s.id !== itemId))
      if (editingId === itemId) cancelEdit()
    } catch {
      setError('Could not reach server')
    } finally {
      setActionLoadingId(null)
    }
  }

  return (
    <div className="sightings-page">
      <div className="sightings-layout">
        <aside className="sightings-post-panel">
          <h2>Creature Sightings</h2>
          <p>Share photos tagged as fish, shark, shellfish, or ray.</p>

          {!user ? (
            <div className="sightings-gate">
              <p>Sign in to post a sighting.</p>
              <button className="btn-primary" onClick={() => navigate('/login')}>Sign In</button>
            </div>
          ) : (
            <form className="sightings-form" onSubmit={submitSighting}>
              <label className="submit-label">Tag
                <select className="submit-input" value={tag} onChange={(e) => setTag(e.target.value)}>
                  {TAGS.map((t) => (
                    <option key={t} value={t}>{t[0].toUpperCase() + t.slice(1)}</option>
                  ))}
                </select>
              </label>

              <label className="submit-label">Photo
                <input
                  id="sighting-image-input"
                  className="submit-input"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setImage(e.target.files?.[0] || null)}
                  required
                />
              </label>

              <label className="submit-label">Caption (optional)
                <textarea
                  className="submit-textarea"
                  rows={3}
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  placeholder="Where and when did you see it?"
                />
              </label>

              {postError && <p className="auth-error">{postError}</p>}

              <button className="btn-primary" type="submit" disabled={posting}>
                {posting ? 'Posting…' : 'Post Sighting'}
              </button>
            </form>
          )}
        </aside>

        <section className="sightings-feed-panel">
          <div className="sightings-feed-header">
            <h3>{heading}</h3>
            <div className="sightings-filter-pills">
              <button
                className={`pill ${selectedTag === 'all' ? 'active' : ''}`}
                onClick={() => setSelectedTag('all')}
              >
                All
              </button>
              {TAGS.map((t) => (
                <button
                  key={t}
                  className={`pill ${selectedTag === t ? 'active' : ''}`}
                  onClick={() => setSelectedTag(t)}
                >
                  {t[0].toUpperCase() + t.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {loading && <p className="state-msg">Loading sightings…</p>}
          {!loading && error && <p className="state-msg">{error}</p>}

          {!loading && !error && (
            <div className="sightings-grid">
              {sightings.length === 0 ? (
                <p className="state-msg">No sightings posted yet for this tag.</p>
              ) : (
                sightings.map((item) => (
                  <article key={item.id} className="sighting-card">
                    <img src={item.image_url} alt={item.caption || `${item.tag} sighting`} className="sighting-image" />
                    <div className="sighting-meta">
                      <span className="sighting-tag">{item.tag}</span>
                      <span className="sighting-author">by {item.username || 'OceanDex user'}</span>
                      <span className="sighting-date">{new Date(item.created_at).toLocaleString()}</span>
                    </div>

                    {user && (item.user_id === user.id || user.role === 'admin') && (
                      <div className="sighting-owner-actions">
                        <button
                          className="btn-secondary sighting-action-btn"
                          onClick={() => startEdit(item)}
                          disabled={actionLoadingId === item.id}
                        >
                          Edit
                        </button>
                        <button
                          className="btn-danger sighting-action-btn"
                          onClick={() => deletePost(item.id)}
                          disabled={actionLoadingId === item.id}
                        >
                          Delete
                        </button>
                      </div>
                    )}

                    {editingId === item.id ? (
                      <div className="sighting-edit-form">
                        <label className="submit-label">Tag
                          <select className="submit-input" value={editTag} onChange={(e) => setEditTag(e.target.value)}>
                            {TAGS.map((t) => (
                              <option key={t} value={t}>{t[0].toUpperCase() + t.slice(1)}</option>
                            ))}
                          </select>
                        </label>

                        <label className="submit-label">Caption (optional)
                          <textarea
                            className="submit-textarea"
                            rows={2}
                            value={editCaption}
                            onChange={(e) => setEditCaption(e.target.value)}
                          />
                        </label>

                        {editError && <p className="auth-error">{editError}</p>}

                        <div className="sighting-edit-actions">
                          <button
                            className="btn-primary sighting-action-btn"
                            onClick={() => saveEdit(item.id)}
                            disabled={actionLoadingId === item.id}
                          >
                            Save
                          </button>
                          <button className="btn-secondary sighting-action-btn" onClick={cancelEdit}>Cancel</button>
                        </div>
                      </div>
                    ) : (
                      item.caption && <p className="sighting-caption">{item.caption}</p>
                    )}
                  </article>
                ))
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
