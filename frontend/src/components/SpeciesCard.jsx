import { STATUS_COLORS } from '../utils/constants'

export default function SpeciesCard({ creature }) {
  const iucn = creature.conservation?.iucn_level
  const statusColor = STATUS_COLORS[iucn] || '#9ca3af'

  return (
    <div className="related-card">
      <div className="related-img">
        {creature.image_url ? (
          <img src={creature.image_url} alt={creature.common_name} />
        ) : (
          <div className="related-img-placeholder">■</div>
        )}
      </div>
      <div className="related-info">
        <p className="related-name">{creature.common_name}</p>
        <p className="related-meta">{creature.category} · <span style={{ color: statusColor }}>{iucn}</span></p>
      </div>
    </div>
  )
}
