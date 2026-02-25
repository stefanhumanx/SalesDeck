import { useMemo } from 'react'
import ProductCard from './ProductCard'

export default function ProductCatalog({
  groupedProducts,
  selectedProducts,
  onToggle,
  categories,
  searchQuery,
  setSearchQuery,
  activeCategory,
  setActiveCategory,
  selectedCount,
  totalCount
}) {
  return (
    <div className="catalog-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="catalog-header">
        <input
          type="text"
          className="search-box"
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        <div className="category-filters">
          {categories.map(category => (
            <button
              key={category}
              className={`category-pill ${activeCategory === category ? 'active' : ''}`}
              onClick={() => setActiveCategory(category)}
            >
              {category}
            </button>
          ))}
        </div>

        <div className="product-count">
          {selectedCount} of {totalCount} products selected
        </div>
      </div>

      <div className="products-list">
        {Object.keys(groupedProducts).length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '32px',
              color: '#999',
              fontSize: '14px'
            }}
          >
            No products found
          </div>
        ) : (
          Object.entries(groupedProducts).map(([categoryName, categoryProducts]) => (
            <div key={categoryName} className="category-section">
              <div className="category-header">{categoryName}</div>
              {categoryProducts.map(product => (
                <ProductCard
                  key={product.slide_index}
                  product={product}
                  isSelected={!!selectedProducts[product.slide_index]}
                  onToggle={() => onToggle(product.slide_index)}
                />
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
