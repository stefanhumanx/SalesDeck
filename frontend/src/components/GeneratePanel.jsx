import { useMemo } from 'react'
import SponsorForm from './SponsorForm'

export default function GeneratePanel({
  selectedProducts,
  sponsorInfo,
  onFormChange,
  onGenerate,
  onClearAll,
  isGenerating,
  error,
  onDismissError
}) {
  const selectedCount = Object.keys(selectedProducts).length
  const totalPrice = useMemo(() => {
    return Object.values(selectedProducts).reduce((sum, product) => {
      return sum + (product.price || 0)
    }, 0)
  }, [selectedProducts])

  const hasAllPrices = Object.values(selectedProducts).every(p => p.price)

  return (
    <div className="sidebar" style={{ display: 'flex', flexDirection: 'column' }}>
      <div className="sidebar-content">
        {error && (
          <div className="error-message">
            <span className="error-close" onClick={onDismissError}>×</span>
            {error}
          </div>
        )}

        <div className="sidebar-section">
          <div className="sidebar-section-title">Sponsor Info</div>
          <SponsorForm sponsorInfo={sponsorInfo} onChange={onFormChange} />
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-title">
            Selected Products
            {selectedCount > 0 && (
              <span
                style={{
                  float: 'right',
                  fontSize: '12px',
                  fontWeight: 'normal',
                  color: '#666'
                }}
              >
                {selectedCount} items
              </span>
            )}
          </div>

          <div className="selected-products">
            {selectedCount === 0 ? (
              <div className="selected-products-empty">
                No products selected
              </div>
            ) : (
              Object.values(selectedProducts).map(product => (
                <div key={product.slide_index} className="selected-product-item">
                  <span className="selected-product-name">{product.name}</span>
                  {product.price && (
                    <span className="selected-product-price">
                      ${product.price.toFixed(2)}
                    </span>
                  )}
                </div>
              ))
            )}
          </div>

          {selectedCount > 0 && (
            <div className="selected-products-stats">
              <span className="selected-count">
                {hasAllPrices ? `Total: $${totalPrice.toFixed(2)}` : 'Total: N/A'}
              </span>
              <span
                className="clear-all-link"
                onClick={onClearAll}
              >
                Clear All
              </span>
            </div>
          )}
        </div>
      </div>

      <div style={{ padding: '20px', borderTop: '1px solid var(--border)' }}>
        <button
          className={`btn btn-primary ${isGenerating ? 'loading' : ''}`}
          onClick={onGenerate}
          disabled={isGenerating || selectedCount === 0}
        >
          {isGenerating && <span className="loading-spinner"></span>}
          {isGenerating ? 'Generating...' : 'Generate Deck'}
        </button>
      </div>
    </div>
  )
}
