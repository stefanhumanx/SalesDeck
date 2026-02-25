export default function ProductCard({ product, isSelected, onToggle }) {
  return (
    <div
      className={`product-card ${isSelected ? 'selected' : ''}`}
      onClick={onToggle}
      role="button"
      tabIndex="0"
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          onToggle()
        }
      }}
    >
      <input
        type="checkbox"
        className="product-card-checkbox"
        checked={isSelected}
        onChange={onToggle}
        onClick={(e) => e.stopPropagation()}
      />
      <div className="product-card-content">
        <div className="product-card-name">{product.name}</div>
        <span className="product-card-category">{product.category || 'Uncategorized'}</span>
      </div>
    </div>
  )
}
