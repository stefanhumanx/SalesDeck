# HumanX Deck Generator

## Overview

A web application for HumanX sales representatives to quickly generate custom sponsorship proposal PDFs. The application allows salespeople to select products from a catalog, fill in sponsor information, and generate beautiful PDF proposals in seconds.

## How It Works

The HumanX Deck Generator workflow is simple and efficient:

1. **Product Selection**: Sales reps browse the product catalog and select products to include in the proposal
2. **Sponsor Information**: Fill in sponsor/client details (name, contact info, custom fields)
3. **Generate**: Click the "Generate" button to create a custom PDF proposal
4. **Download**: The generated PDF is automatically downloaded to the user's computer

The application combines a React frontend for user interaction with a Python FastAPI backend that handles PDF generation using PowerPoint templates and LibreOffice for conversion.

## Quick Start (3 Steps)

### Step 1: Prepare Your Template
```bash
# Copy your PowerPoint template to the backend directory
cp your-template.pptx backend/template.pptx
```

### Step 2: Configure Product Pricing
Edit the `products_catalog.csv` file in the project root with your product information:
```csv
slide_index,name,category,price
23,Product A,Category 1,1000
24,Product B,Category 1,1500
25,Product C,Category 2,2000
```

### Step 3: Run with Docker
```bash
# Start both frontend and backend services
docker-compose up

# The application will be available at http://localhost:3000
# The API will be available at http://localhost:8000
```

## Product Catalog Setup Options

### Option 1: CSV (Default)
Simple local CSV file for product information:
- Location: `products_catalog.csv`
- Edit directly in any text editor or spreadsheet application
- Changes are picked up immediately on restart

Format required:
```csv
slide_index,name,category,price
23,Premium Sponsorship,Gold,5000
24,Standard Sponsorship,Silver,3000
```

### Option 2: Google Sheets (Recommended for Teams)
For collaborative editing and real-time updates:

1. **Create a Google Sheet** with columns:
   - slide_index (integer)
   - name (string)
   - category (string)
   - price (number)

2. **Set up Google Cloud credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable the "Google Sheets API"
   - Create a Service Account
   - Download the credentials JSON file

3. **Configure environment variables**:
   ```bash
   # In backend/.env or docker environment
   GOOGLE_SHEET_ID=your-sheet-id-here
   GOOGLE_CREDENTIALS_JSON=/path/to/credentials.json
   ```

4. **Edit the sheet directly**: Changes are reflected immediately in the application

## Development Setup (Without Docker)

### Backend Setup
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to set TEMPLATE_PATH to your template location

# Run the FastAPI server with auto-reload
uvicorn main:app --reload

# The API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

### Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Run the development server with hot reload
npm run dev

# The application will be available at http://localhost:5173
```

Both services will run simultaneously for development.

## Updating the Product Catalog

### Using CSV
1. Open `products_catalog.csv` in any text editor or Excel
2. Update product names, categories, or prices
3. Save the file
4. Restart the application (or refresh if using Google Sheets)

### Using Google Sheets
1. Open your Google Sheet
2. Edit product details directly
3. Changes are live immediately
4. No application restart needed

## Adding New Products

Products in the HumanX Deck Generator come from slides in your PowerPoint template:

1. **Add a new slide** to your template (e.g., at position 129)
2. **Design the slide** with product information and layout
3. **Update products_catalog.csv**:
   - Add a new row with the slide index (129 in this example)
   - Include name, category, and price
4. **Restart the application** to load the new product

**Slide Index Convention**: By default, product slides are numbered 23-128 in the template. Slides 0-22 are typically intro/branding slides.

## Deployment

The application is ready for production deployment on:

- **Railway.app**: Easy one-click deployment with automatic HTTPS
- **Render**: Simple Docker deployment with health checks
- **Fly.io**: Global deployment with automatic scaling
- **AWS ECS/Fargate**: For enterprise deployments
- **Google Cloud Run**: Serverless deployment option

All of these support Docker Compose format, making deployment straightforward.

### Key Production Considerations

- Set `TEMPLATE_PATH` to a mounted volume containing your template
- Configure `GOOGLE_SHEET_ID` and credentials if using Google Sheets
- Enable CORS if frontend and backend are on different domains
- Use environment variables for sensitive configuration
- Ensure LibreOffice and system fonts are available in the container

## File Structure

```
humanx-deck-generator/
├── README.md                 # This file
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── docker-compose.yml       # Docker Compose configuration
├── products_catalog.csv     # Product catalog (editable by team)
│
├── backend/
│   ├── Dockerfile           # Backend container definition
│   ├── requirements.txt      # Python dependencies
│   ├── main.py              # FastAPI application entry point
│   ├── deck_generator.py     # Core PDF generation logic
│   ├── sheets_client.py      # Google Sheets integration
│   ├── template.pptx        # PowerPoint template (not in git)
│   ├── products_catalog.csv # Product catalog (mounted from root)
│   ├── .env.example         # Backend environment template
│   └── README.md            # Backend documentation
│
├── frontend/
│   ├── Dockerfile           # Frontend container definition
│   ├── nginx.conf           # Nginx server configuration
│   ├── package.json         # Node.js dependencies
│   ├── index.html           # HTML entry point
│   ├── vite.config.js       # Vite configuration
│   ├── .env.example         # Frontend environment template
│   │
│   └── src/
│       ├── main.jsx         # React app entry point
│       ├── App.jsx          # Main App component
│       ├── App.css          # Styles
│       │
│       └── components/
│           ├── ProductCatalog.jsx   # Product listing
│           ├── ProductCard.jsx      # Individual product card
│           ├── SponsorForm.jsx      # Sponsor info form
│           └── GeneratePanel.jsx    # PDF generation panel
│
└── .github/
    └── workflows/           # CI/CD workflows (optional)
```

## Architecture Overview

**Frontend (React + Vite)**
- Modern SPA built with React
- Real-time product selection
- Form validation and submission
- PDF download handling

**Backend (Python + FastAPI)**
- High-performance async API
- Integrates with Google Sheets for dynamic product data
- Generates PDFs using python-pptx for slide manipulation
- LibreOffice for PPTX to PDF conversion
- Efficient file handling and streaming

**Communication**
- Frontend calls `/api/generate` endpoint with sponsor info and selected products
- Backend generates custom PDF and streams it back
- Download happens automatically in the browser

## Updating and Maintenance

### Regular Updates
- Keep Docker images updated: `docker-compose pull`
- Update Python packages: `pip install --upgrade -r requirements.txt`
- Update Node packages: `npm update` in frontend directory

### Troubleshooting
- Check Docker logs: `docker-compose logs -f [service-name]`
- Backend API docs at http://localhost:8000/docs
- Frontend dev tools: Check browser console for errors
- LibreOffice conversion issues: Ensure template.pptx exists and is readable

## Support and Documentation

- Backend README: See `backend/README.md` for API documentation
- Frontend README: See `frontend/README.md` for component details
- Each service has its own `.env.example` for configuration options
- API interactive documentation: http://localhost:8000/docs (Swagger UI)

