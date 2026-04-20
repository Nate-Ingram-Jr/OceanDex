import { STATUS_COLORS } from '../utils/constants'

export default function SpeciesListItem({ creature, selected, onClick }) {
  const iucn = creature.conservation?.iucn_level
  const dotColor = STATUS_COLORS[iucn] || '#9ca3af'

  return (
    <div className={`list-item ${selected ? 'selected' : ''}`} onClick={onClick}>
      <div className="list-item-img">
        {creature.image_url ? (
          <img src={creature.image_url} alt={creature.common_name} />
        ) : (
          <div className="list-item-placeholder">■</div>
        )}
      </div>
      <div className="list-item-info">
        <p className="list-item-name">{creature.common_name}</p>
        <p className="list-item-sci">{creature.scientific_name}</p>
      </div>
      <span className="list-item-dot" style={{ color: dotColor }}>●</span>
    </div>
  )
}
