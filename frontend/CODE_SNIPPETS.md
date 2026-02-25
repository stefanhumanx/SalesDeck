# Code Snippets - HumanX Deck Generator Frontend

## Main App Component Flow

### 1. Data Fetching on Mount

```jsx
// src/App.jsx - Lines 16-26
useEffect(() => {
  const fetchProducts = async () => {
    try {
      const response = await fetch('/api/products')
      if (!response.ok) throw new Error('Failed to fetch products')
      const data = await response.json()
      setProducts(data)
      setLoading(false)
    } catch (err) {
      setError('Failed to load products. Please refresh the page.')
    }
  }
  fetchProducts()
}, [])
```

### 2. Dynamic Category Generation

```jsx
// src/App.jsx - Lines 29-34
const categories = useMemo(() => {
  const cats = new Set(products.map(p => p.category || 'Uncategorized'))
  return ['All', ...Array.from(cats).sort()]
}, [products])
```

### 3. Product Filtering

```jsx
// src/App.jsx - Lines 36-46
const filteredProducts = useMemo(() => {
  return products.filter(product => {
    const matchesSearch =
      product.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory =
      activeCategory === 'All' || product.category === activeCategory
    return matchesSearch && matchesCategory
  })
}, [products, searchQuery, activeCategory])
```

### 4. PDF Generation with Download

```jsx
// src/App.jsx - Lines 88-135
const handleGenerate = async () => {
  // Validation
  if (!sponsorInfo.sponsor_name.trim()) {
    setError('Please enter sponsor/company name')
    return
  }
  if (Object.keys(selectedProducts).length === 0) {
    setError('Please select at least one product')
    return
  }

  setError(null)
  setIsGenerating(true)

  try {
    const payload = {
      sponsor_name: sponsorInfo.sponsor_name,
      rep_name: sponsorInfo.rep_name,
      sponsor_email: sponsorInfo.sponsor_email,
      selected_products: Object.values(selectedProducts).map(p => ({
        slide_index: p.slide_index,
        name: p.name,
        category: p.category
      }))
    }

    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error('Failed to generate deck')

    // Extract filename from Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = 'sponsorship-deck.pdf'
    if (contentDisposition) {
      const match = contentDisposition.match(/filename[^;=\n]*=(["\']?)([^"\';]*)\1/i)
      if (match && match[2]) filename = match[2]
    }

    // Convert blob and trigger download
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)

    // Reset form after success
    setSponsorInfo({
      sponsor_name: '',
      rep_name: '',
      sponsor_email: ''
    })
    setSelectedProducts({})
  } catch (err) {
    setError('Failed to generate deck. Please try again.')
  } finally {
    setIsGenerating(false)
  }
}
```

## Component Composition

### Product Catalog - Search & Filter

```jsx
// src/components/ProductCatalog.jsx - Rendering Logic
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
```

### Product Selection - Click & Keyboard Support

```jsx
// src/components/ProductCard.jsx
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
    <span className="product-card-category">
      {product.category || 'Uncategorized'}
    </span>
  </div>
</div>
```

### Dynamic Pricing Calculation

```jsx
// src/components/GeneratePanel.jsx - Lines 14-21
const selectedCount = Object.keys(selectedProducts).length
const totalPrice = useMemo(() => {
  return Object.values(selectedProducts).reduce((sum, product) => {
    return sum + (product.price || 0)
  }, 0)
}, [selectedProducts])

const hasAllPrices = Object.values(selectedProducts).every(p => p.price)
```

### Error Handling with Dismissal

```jsx
// src/components/GeneratePanel.jsx - Error Display
{error && (
  <div className="error-message">
    <span className="error-close" onClick={onDismissError}>×</span>
    {error}
  </div>
)}
```

### Loading State Management

```jsx
// Generate button with loading spinner
<button
  className={`btn btn-primary ${isGenerating ? 'loading' : ''}`}
  onClick={onGenerate}
  disabled={isGenerating || selectedCount === 0}
>
  {isGenerating && <span className="loading-spinner"></span>}
  {isGenerating ? 'Generating...' : 'Generate Deck'}
</button>
```

## CSS Key Features

### Color System with CSS Variables

```css
/* src/App.css - Lines 1-12 */
:root {
  --navy: #1a1a2e;
  --white: #ffffff;
  --bg: #f8f9fa;
  --gold: #f5a623;
  --border: #e1e4e8;
  --text-primary: #1a1a2e;
  --text-secondary: #666666;
  --success: #28a745;
  --error: #dc3545;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
```

### Two-Column Layout

```css
.app-container {
  display: flex;
  height: calc(100vh - 65px);
  overflow: hidden;
}

.catalog-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border);
}

.sidebar {
  width: 400px;
  display: flex;
  flex-direction: column;
}
```

### Interactive Product Card Styling

```css
.product-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--border);
}

.product-card:hover {
  background-color: var(--bg);
  border-color: var(--gold);
  box-shadow: var(--shadow);
}

.product-card.selected {
  background-color: #fff8e6;
  border-color: var(--gold);
}
```

### Button States

```css
.btn-primary {
  background-color: var(--gold);
  color: var(--white);
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background-color: #e5951a;
  box-shadow: 0 4px 12px rgba(245, 166, 35, 0.2);
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}
```

### Loading Animation

```css
.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--white);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

## API Integration Examples

### Fetch Products

```javascript
const response = await fetch('/api/products')
const data = await response.json()
// Expected format:
// [
//   {
//     "slide_index": "001",
//     "name": "Gold Sponsorship",
//     "category": "Sponsorships",
//     "price": 50000
//   },
//   ...
// ]
```

### Generate PDF

```javascript
const payload = {
  sponsor_name: "Acme Corp",
  rep_name: "John Doe",
  sponsor_email: "john@acme.com",
  selected_products: [
    {
      slide_index: "001",
      name: "Gold Sponsorship",
      category: "Sponsorships"
    }
  ]
}

const response = await fetch('/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})

// Response is a PDF blob
const blob = await response.blob()
// Browser downloads file automatically
```

## State Management Pattern

```jsx
// App-level state
const [products, setProducts] = useState([])
const [selectedProducts, setSelectedProducts] = useState({})
const [sponsorInfo, setSponsorInfo] = useState({
  sponsor_name: '',
  rep_name: '',
  sponsor_email: ''
})
const [isGenerating, setIsGenerating] = useState(false)
const [searchQuery, setSearchQuery] = useState('')
const [activeCategory, setActiveCategory] = useState('All')
const [error, setError] = useState(null)

// Derived state with useMemo
const categories = useMemo(() => { ... }, [products])
const filteredProducts = useMemo(() => { ... }, [products, searchQuery, activeCategory])
const groupedProducts = useMemo(() => { ... }, [filteredProducts])

// Data flow: App -> ProductCatalog -> ProductCard
// App -> GeneratePanel -> (SponsorForm + Selected List)
```

## Component Hierarchy

```
App (state, API calls, filtering)
├── ProductCatalog (display filtered products)
│   └── ProductCard (each item)
│
└── GeneratePanel (sidebar)
    ├── Error message (if any)
    ├── SponsorForm (3 fields)
    ├── Selected Products List
    └── Generate Button
```

Each component is self-contained and follows React best practices with hooks and functional components.
