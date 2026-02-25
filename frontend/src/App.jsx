import { useState, useEffect, useMemo } from 'react'
import ProductCatalog from './components/ProductCatalog'
import GeneratePanel from './components/GeneratePanel'

export default function App() {
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
  const [loading, setLoading] = useState(true)

  // Fetch products on mount
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch('/api/products')
        if (!response.ok) throw new Error('Failed to fetch products')
        const data = await response.json()
        setProducts(data)
        setLoading(false)
      } catch (err) {
        console.error('Error fetching products:', err)
        setError('Failed to load products. Please refresh the page.')
        setLoading(false)
      }
    }

    fetchProducts()
  }, [])

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(products.map(p => p.category || 'Uncategorized'))
    return ['All', ...Array.from(cats).sort()]
  }, [products])

  // Filtered products
  const filteredProducts = useMemo(() => {
    return products.filter(product => {
      const matchesSearch =
        product.name.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesCategory =
        activeCategory === 'All' || product.category === activeCategory
      return matchesSearch && matchesCategory
    })
  }, [products, searchQuery, activeCategory])

  // Group filtered products by category
  const groupedProducts = useMemo(() => {
    const groups = {}
    filteredProducts.forEach(product => {
      const cat = product.category || 'Uncategorized'
      if (!groups[cat]) groups[cat] = []
      groups[cat].push(product)
    })
    return groups
  }, [filteredProducts])

  // Handle product selection toggle
  const handleToggleProduct = (slideIndex) => {
    setSelectedProducts(prev => {
      const updated = { ...prev }
      if (updated[slideIndex]) {
        delete updated[slideIndex]
      } else {
        const product = products.find(p => p.slide_index === slideIndex)
        if (product) {
          updated[slideIndex] = product
        }
      }
      return updated
    })
  }

  // Handle form input changes
  const handleFormChange = (field, value) => {
    setSponsorInfo(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Clear all selections
  const handleClearAll = () => {
    setSelectedProducts({})
  }

  // Generate deck
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
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error('Failed to generate deck')
      }

      // Get filename from Content-Disposition header if available
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = 'sponsorship-deck.pdf'
      if (contentDisposition) {
        const match = contentDisposition.match(/filename[^;=\n]*=(["\']?)([^"\';]*)\1/i)
        if (match && match[2]) {
          filename = match[2]
        }
      }

      // Convert response to blob and download
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(link)

      // Reset form after successful generation
      setSponsorInfo({
        sponsor_name: '',
        rep_name: '',
        sponsor_email: ''
      })
      setSelectedProducts({})
    } catch (err) {
      console.error('Error generating deck:', err)
      setError('Failed to generate deck. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  if (loading) {
    return (
      <div>
        <div className="navbar">
          <span className="navbar-logo">HumanX</span>
          <span className="navbar-separator">|</span>
          <span className="navbar-title">Sponsorship Deck Generator</span>
        </div>
        <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
          Loading products...
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="navbar">
        <span className="navbar-logo">HumanX</span>
        <span className="navbar-separator">|</span>
        <span className="navbar-title">Sponsorship Deck Generator</span>
      </div>

      <div className="app-container">
        <div className="catalog-panel">
          <ProductCatalog
            products={filteredProducts}
            groupedProducts={groupedProducts}
            selectedProducts={selectedProducts}
            onToggle={handleToggleProduct}
            categories={categories}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            activeCategory={activeCategory}
            setActiveCategory={setActiveCategory}
            selectedCount={Object.keys(selectedProducts).length}
            totalCount={products.length}
          />
        </div>

        <div className="sidebar">
          <GeneratePanel
            selectedProducts={selectedProducts}
            sponsorInfo={sponsorInfo}
            onFormChange={handleFormChange}
            onGenerate={handleGenerate}
            onClearAll={handleClearAll}
            isGenerating={isGenerating}
            error={error}
            onDismissError={() => setError(null)}
          />
        </div>
      </div>
    </div>
  )
}
