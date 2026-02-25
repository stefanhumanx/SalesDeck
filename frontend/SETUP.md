# Frontend Setup Guide

## Prerequisites

- Node.js 16+ (includes npm)
- The backend API running on `http://localhost:8000`

## Installation Steps

1. **Navigate to the frontend directory**
   ```bash
   cd /sessions/optimistic-peaceful-noether/humanx-deck-generator/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   - Development: http://localhost:3000
   - The app will automatically proxy API calls to http://localhost:8000

## Project Structure

```
frontend/
├── index.html              # HTML entry point
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration with React plugin
├── src/
│   ├── main.jsx           # React app initialization
│   ├── App.jsx            # Main app component with state & logic
│   ├── App.css            # All component styles (CSS variables, dark theme)
│   └── components/
│       ├── ProductCatalog.jsx    # Product listing & filtering
│       ├── ProductCard.jsx       # Individual product card
│       ├── SponsorForm.jsx       # Sponsor information form
│       └── GeneratePanel.jsx     # Sidebar with form, list, & button
└── README.md              # Full documentation
```

## Key Features

### Product Management
- Fetches 100+ products from `/api/products` on app load
- Groups products by category
- Search by product name (case-insensitive)
- Filter by category with pill buttons
- Display selected count vs total

### Sponsor Information
- Company/Sponsor Name (required)
- Sales Rep Name
- Email address

### Selected Products Panel
- Shows checked items with prices
- Clear All button to reset selections
- Total price calculation (if all products have prices)
- Item count badge

### PDF Generation
- Validates required fields before generation
- POST to `/api/generate` with sponsor info and selected products
- Downloads PDF file with automatic naming
- Shows loading spinner during generation
- Clears form after successful generation

## Development Tips

### Hot Module Replacement
Changes to React components are instantly reflected in the browser without page reload.

### API Proxy
All requests to `/api/*` are automatically forwarded to `http://localhost:8000`:

```javascript
// These requests are proxied:
fetch('/api/products')
fetch('/api/generate', { method: 'POST', ... })
```

### Component Structure
- **App.jsx**: State management, API calls, data flows
- **ProductCatalog**: Left panel - browsing and filtering
- **GeneratePanel**: Right sidebar - form and actions
- All styling in **App.css** using CSS variables for theming

### Styling
All CSS is in one file (`App.css`) using:
- CSS variables for consistent colors
- BEM-like class naming
- Flexbox for layouts
- Mobile-responsive design

## Testing the API Integration

### Sample Product Data Expected
```json
[
  {
    "slide_index": "001",
    "name": "Gold Sponsorship",
    "category": "Sponsorships",
    "price": 50000
  },
  ...
]
```

### Sample API Response for Generate
- Content-Type: application/pdf
- Content-Disposition: attachment; filename="sponsorship_deck_*.pdf"
- Body: PDF binary blob

## Troubleshooting

### Port Already in Use
If port 3000 is in use, Vite will prompt to use another port or you can specify:
```bash
npm run dev -- --port 3001
```

### API Not Responding
- Ensure backend is running on http://localhost:8000
- Check Vite proxy configuration in `vite.config.js`
- Check browser Network tab for failed requests

### Products Not Loading
- Verify `/api/products` endpoint exists and returns valid JSON
- Check browser console for errors
- Ensure backend CORS headers allow localhost:3000

## Building for Production

```bash
npm run build
```

Creates optimized build in `dist/` directory. Deploy the contents of `dist/` to your web server.

## Next Steps

1. Ensure backend API is running
2. Run `npm install` to install dependencies
3. Run `npm run dev` to start development
4. Test product loading and form submission
5. Verify PDF download works with `/api/generate`
