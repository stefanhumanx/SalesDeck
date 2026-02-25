# HumanX Deck Generator - Quick Reference

## File Locations

All files are in: `/sessions/optimistic-peaceful-noether/humanx-deck-generator/frontend/`

### Source Code Files
- **App.jsx** - Main app component (state management, API calls)
- **App.css** - All component styling (509 lines)
- **components/ProductCatalog.jsx** - Left panel (search, filter, display)
- **components/ProductCard.jsx** - Individual product card
- **components/SponsorForm.jsx** - Sponsor information form
- **components/GeneratePanel.jsx** - Right sidebar (form + list + button)
- **main.jsx** - React entry point

### Configuration
- **package.json** - Dependencies and npm scripts
- **vite.config.js** - Build configuration
- **index.html** - HTML entry point
- **.gitignore** - Git ignore patterns
- **.env.example** - Environment variables

### Documentation
- **README.md** - Full documentation
- **SETUP.md** - Installation guide
- **SUMMARY.md** - Project overview
- **CODE_SNIPPETS.md** - Code examples
- **QUICK_REFERENCE.md** - This file

## Quick Commands

```bash
# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Key Features Checklist

### Product Catalog
- [x] 100+ items grouped by category
- [x] Search functionality (case-insensitive)
- [x] Category filter pills
- [x] Product count display
- [x] Checkbox selection
- [x] Click-to-select any product
- [x] Keyboard support (Enter/Space)

### Selected Items Panel
- [x] Real-time product list
- [x] Price per item
- [x] Total price calculation
- [x] Clear All link
- [x] Item count badge
- [x] Scrollable list

### Sponsor Form
- [x] Company Name (required)
- [x] Sales Rep Name (optional)
- [x] Email Address (optional)
- [x] Form validation
- [x] Clean styling

### PDF Generation
- [x] Validates required fields
- [x] Shows loading spinner
- [x] Automatic PDF download
- [x] Error handling
- [x] Form reset on success

## Color Scheme

```
Navy:         #1a1a2e  (nav, text)
Gold:         #f5a623  (buttons, accents)
Background:   #f8f9fa  (light gray)
White:        #ffffff  (panels)
Border:       #e1e4e8  (dividers)
```

## Component Props

### ProductCatalog
```jsx
<ProductCatalog
  groupedProducts={object}
  selectedProducts={object}
  onToggle={(slideIndex) => {}}
  categories={array}
  searchQuery={string}
  setSearchQuery={(query) => {}}
  activeCategory={string}
  setActiveCategory={(category) => {}}
  selectedCount={number}
  totalCount={number}
/>
```

### ProductCard
```jsx
<ProductCard
  product={{
    slide_index: string,
    name: string,
    category: string,
    price?: number
  }}
  isSelected={boolean}
  onToggle={() => {}}
/>
```

### SponsorForm
```jsx
<SponsorForm
  sponsorInfo={{
    sponsor_name: string,
    rep_name: string,
    sponsor_email: string
  }}
  onChange={(field, value) => {}}
/>
```

### GeneratePanel
```jsx
<GeneratePanel
  selectedProducts={object}
  sponsorInfo={object}
  onFormChange={(field, value) => {}}
  onGenerate={() => {}}
  onClearAll={() => {}}
  isGenerating={boolean}
  error={string|null}
  onDismissError={() => {}}
/>
```

## State Variables (App.jsx)

```javascript
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
```

## API Endpoints

### GET /api/products
Returns array of products
```json
[
  {
    "slide_index": "001",
    "name": "Gold Sponsorship",
    "category": "Sponsorships",
    "price": 50000
  }
]
```

### POST /api/generate
Request:
```json
{
  "sponsor_name": "Acme Corp",
  "rep_name": "John Doe",
  "sponsor_email": "john@acme.com",
  "selected_products": [
    {
      "slide_index": "001",
      "name": "Gold Sponsorship",
      "category": "Sponsorships"
    }
  ]
}
```

Response: PDF blob (automatic download)

## CSS Classes Reference

### Layout
- `.navbar` - Top navigation bar
- `.app-container` - Main flex container
- `.catalog-panel` - Left panel (60%)
- `.sidebar` - Right sidebar (40%)

### Catalog
- `.catalog-header` - Search and filter area
- `.search-box` - Search input
- `.category-filters` - Category pill buttons
- `.category-pill` - Individual category button
- `.products-list` - Scrollable product list
- `.category-section` - Category group
- `.category-header` - Category title

### Products
- `.product-card` - Individual product row
- `.product-card.selected` - When selected
- `.product-card-checkbox` - Checkbox input
- `.product-card-name` - Product name text
- `.product-card-category` - Category badge

### Form
- `.form-group` - Form field container
- `.form-label` - Field label
- `.form-input` - Text input
- `.sponsor-form` - Form wrapper

### Selected Items
- `.selected-products` - Products list container
- `.selected-product-item` - Individual item
- `.selected-product-name` - Item name
- `.selected-product-price` - Item price
- `.selected-products-stats` - Stats bar

### Buttons
- `.btn` - Base button style
- `.btn-primary` - Primary button (gold)
- `.btn-primary.loading` - Loading state
- `.loading-spinner` - Spinner animation

### Other
- `.error-message` - Error display
- `.error-close` - Error dismiss button
- `.clear-all-link` - Clear all link

## Customization Guide

### Change Navy Color
Edit `src/App.css` line 2:
```css
--navy: #1a1a2e;  /* Change this */
```

### Change Gold Color
Edit `src/App.css` line 5:
```css
--gold: #f5a623;  /* Change this */
```

### Change Sidebar Width
Edit `src/App.css` line ~395:
```css
.sidebar {
  width: 400px;  /* Change this */
}
```

### Add Form Field
Edit `src/components/SponsorForm.jsx`:
```jsx
<div className="form-group">
  <label className="form-label">New Field</label>
  <input type="text" className="form-input" />
</div>
```

### Update API URL
Edit `src/App.jsx` line 19 (fetch products):
```jsx
const response = await fetch('/api/products')  // Change endpoint
```

Edit `src/App.jsx` line 101 (generate deck):
```jsx
const response = await fetch('/api/generate', {  // Change endpoint
```

## Testing Checklist

- [ ] Backend running on localhost:8000
- [ ] Frontend starts: `npm run dev`
- [ ] Products load from /api/products
- [ ] Search filters products by name
- [ ] Category filters work correctly
- [ ] Click product card toggles selection
- [ ] Selected items appear in sidebar
- [ ] Prices display correctly
- [ ] Clear All link removes all selections
- [ ] Form validation shows error without sponsor name
- [ ] Form validation shows error without products
- [ ] Generate button shows loading spinner
- [ ] PDF downloads with correct name
- [ ] Form resets after successful generation
- [ ] Responsive on mobile/tablet

## Troubleshooting

### Products Not Loading
- Check if `/api/products` endpoint exists
- Check browser Network tab for failed requests
- Check backend CORS headers

### API Proxy Not Working
- Ensure Vite proxy is configured in `vite.config.js`
- Check that backend is running on :8000
- Restart dev server if you changed vite.config.js

### Styling Issues
- Check if CSS class names match between JSX and CSS
- Check CSS variable values in :root section
- Use browser DevTools to inspect elements

### PDF Not Downloading
- Check that response is actually a blob
- Check Content-Type header is application/pdf
- Check console for JavaScript errors

## Performance Tips

- useMemo prevents unnecessary filtering/grouping
- Products array is stable (not recreated)
- Selected products stored by index (efficient lookup)
- Only left/catalog-panel and sidebar scroll independently

## Accessibility Features

- Keyboard navigation (Enter/Space on product cards)
- Proper form labels with htmlFor attributes
- ARIA roles on interactive elements
- Error messages for required fields
- High contrast color scheme

## Browser Compatibility

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires ES2020+ support (modern browsers)

## Build Output

Production build creates `dist/` directory with:
- Minified JavaScript
- Optimized CSS
- Tree-shaken unused code
- Source maps (if configured)

Typical size: 30-40 KB gzipped

## Notes

- No Redux or complex state management needed
- Single page application (no routing)
- All API calls handled in App.jsx
- Components are presentational (receive data via props)
- Styling is scoped with BEM-like class names
