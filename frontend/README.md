# HumanX Sponsorship Deck Generator - Frontend

A clean, modern React-based sales tool for HumanX reps to quickly generate customized sponsorship decks.

## Features

- **Product Catalog**: Browse 100+ items grouped by category
- **Smart Search & Filter**: Find products by name or category
- **Quick Selection**: Checkbox-based product selection with visual feedback
- **Sponsor Information Form**: Capture client details (company, rep name, email)
- **Selected Items Panel**: View and manage selected products with pricing
- **PDF Generation**: Generate and download customized sponsorship decks

## Getting Started

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will run on `http://localhost:3000` with automatic proxy to the backend API at `http://localhost:8000`.

### Building for Production

```bash
npm run build
```

Preview the build:

```bash
npm run preview
```

## Architecture

### Components

- **App.jsx** - Main application container with state management
  - Fetches products from API
  - Manages form state and product selections
  - Handles PDF generation

- **ProductCatalog.jsx** - Left panel with product browsing
  - Search functionality
  - Category filtering
  - Product grid display

- **ProductCard.jsx** - Individual product card/row
  - Checkbox selection
  - Category badge
  - Hover states

- **SponsorForm.jsx** - Sponsor information input
  - Company name (required)
  - Sales rep name
  - Email address

- **GeneratePanel.jsx** - Right sidebar
  - Embeds sponsor form
  - Shows selected products list
  - Displays pricing and totals
  - Generate button with loading state

### State Management

Uses React hooks (useState, useEffect, useMemo):
- `products` - Loaded from GET /api/products
- `selectedProducts` - Map of slide_index to product objects
- `sponsorInfo` - Form data (sponsor_name, rep_name, sponsor_email)
- `searchQuery` - Current search filter
- `activeCategory` - Selected category filter
- `isGenerating` - Loading state during PDF generation
- `error` - Error messages

## API Integration

### GET /api/products

Returns array of products:
```json
[
  {
    "slide_index": "001",
    "name": "Product Name",
    "category": "Category Name",
    "price": 10000
  }
]
```

### POST /api/generate

Request body:
```json
{
  "sponsor_name": "Company Name",
  "rep_name": "Rep Name",
  "sponsor_email": "email@example.com",
  "selected_products": [
    {
      "slide_index": "001",
      "name": "Product Name",
      "category": "Category"
    }
  ]
}
```

Response: PDF file as blob (downloaded to browser)

## Design

### Color Scheme

- **Navy**: #1a1a2e (nav bar, primary text)
- **Gold/Orange**: #f5a623 (accents, buttons)
- **Background**: #f8f9fa (light gray)
- **White**: #ffffff (panels)
- **Border**: #e1e4e8 (dividers)

### Layout

- **Top Navigation**: Dark navy header with HumanX branding
- **Two-Column Layout**: 
  - Left (60%): Product catalog with search
  - Right (40%): Sponsor form + selected items + generate button

### Responsive

Stacks vertically on tablets and mobile devices.

## Development Notes

- Uses Vite for fast development and optimized builds
- React 18 with functional components and hooks
- No external UI framework (pure CSS)
- Fully typed with prop validation
- Error handling for API failures
- Loading states and user feedback

## Browser Support

Modern browsers (Chrome, Firefox, Safari, Edge) with ES2020+ support.
