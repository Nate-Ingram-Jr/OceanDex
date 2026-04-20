import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import SpeciesDetailPanel from '../components/SpeciesDetailPanel'

export default function SpeciesDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [creature, setCreature] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    setLoading(true)
    setError(false)
    fetch(`/api/creatures/${id}`)
      .then((r) => {
        if (!r.ok) throw new Error('Not found')
        return r.json()
      })
      .then((data) => {
        setCreature(data)
        setLoading(false)
      })
      .catch(() => {
        setError(true)
        setLoading(false)
      })
  }, [id])

  if (loading) return <div className="detail-empty"><p>Loading...</p></div>
  if (error) return (
    <div className="detail-empty">
      <p>Species not found. <button onClick={() => navigate('/')}>Go back</button></p>
    </div>
  )
  return <SpeciesDetailPanel creature={creature} />
}
