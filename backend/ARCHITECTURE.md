# HumanX Deck Generator - Architecture Documentation

## Overview

The HumanX Deck Generator is a REST API backend that generates custom sponsorship decks from a PowerPoint template. It accepts sponsor information and a list of selected products, then produces a professional PDF proposal deck.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Web Server                       │
│                    (main.py)                                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ GET /health  │  │GET /products │  │POST /generate      │
│  │              │  │              │  │               │      │
│  │Health Check  │  │Load Catalog  │  │Generate PDF   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────┬──────────────────────────────┬──────────────────┘
           │                              │
           │                    ┌─────────▼─────────┐
           │                    │ deck_generator.py │
           │                    │                   │
           │                    │ • Remove slides   │
           │                    │ • Add proposal    │
           │                    │ • Convert to PDF  │
           │                    └─────────┬─────────┘
           │                              │
           │          ┌───────────────────┼───────────────────┐
           │          │                   │                   │
    ┌──────▼────┐   ┌─▼──────┐     ┌──────▼────┐      ┌──────▼────┐
    │ Sheets    │   │Template│     │Temp Files │      │LibreOffice│
    │Client     │   │PPTX    │     │(Working)  │      │(soffice)  │
    │           │   │        │     │           │      │           │
    │Google     │   │Master  │     │temp/      │      │PDF        │
    │Sheets API │   │Deck    │     │working.*  │      │Conversion │
    └───────────┘   └────────┘     └───────────┘      └───────────┘
```

## Module Structure

### 1. main.py - FastAPI Application

**Purpose**: REST API server and request/response handling

**Key Components**:
- **CORS Middleware**: Allows requests from all origins (development)
- **Request Logging**: Middleware logs all requests with timing
- **Environment Setup**: Loads configuration from .env file
- **Health Endpoint**: `/health` returns service status
- **Products Endpoint**: `/api/products` returns product catalog
- **Generation Endpoint**: `/api/generate` generates custom decks

**Request Flow**:
```
HTTP Request
    ↓
CORS Check
    ↓
Log Request + Start Timer
    ↓
Route Handler (health/products/generate)
    ↓
Process Request
    ↓
Return Response
    ↓
Log Response + Duration
    ↓
HTTP Response
```

**Pydantic Models**:
- `Product`: Product from catalog (slide_index, name, category, price)
- `SelectedProduct`: Product selected for generation (subset of Product)
- `GenerationRequest`: Request body for /api/generate

### 2. deck_generator.py - Core Logic

**Purpose**: PowerPoint manipulation and PDF generation

**Key Functions**:

#### remove_slide(prs, index)
- Removes a slide from the presentation
- Uses XML manipulation (python-pptx lacks native removal)
- Called in reverse order to avoid index shifting issues

#### add_quote_slide(prs, sponsor_name, rep_name, products, insert_position)
- Creates a professional proposal/sponsorship slide
- Styling:
  - Dark background: #1a1a2e (RGB 26, 26, 46)
  - Gold accents: #f5a623 (RGB 245, 166, 35)
  - White/light gray text: RGB 255, 255, 255
- Content:
  - Large title: "SPONSORSHIP PROPOSAL"
  - Sponsor info: name and rep name
  - Product table: Name | Investment
  - Total row (sum of prices)
  - Generation date footer
- Positioning: Inserted at position after front matter (typically slide 23)

#### convert_to_pdf(pptx_path, output_dir)
- Converts PPTX to PDF using LibreOffice headless mode
- Tries multiple command variations:
  1. Custom soffice.py wrapper script
  2. soffice command
  3. libreoffice command
- Returns path to generated PDF
- Raises RuntimeError if all methods fail

#### generate_deck(template_path, selected_products, sponsor_info)
- Main orchestrator function
- Process:
  1. Create temporary directory
  2. Copy template to temp location
  3. Load with python-pptx
  4. Calculate which slides to remove
  5. Remove unselected product slides (in reverse order)
  6. Insert proposal slide
  7. Save modified presentation
  8. Convert to PDF
  9. Return paths (cleanup left to caller)

**Slide Indices**:
- 0-22: Front matter (static, always kept)
- 23-128: Products (selected ones kept, others removed)
- 129-131: Closing (static, always kept)
- After processing: Intro (0-22) + Proposal (23) + Selected Products + Closing

### 3. sheets_client.py - Google Sheets Integration

**Purpose**: Load product catalog from Google Sheets

**Function**: get_products_from_sheet()
- Reads from Google Sheet specified by GOOGLE_SHEET_ID env var
- Uses service account credentials from GOOGLE_CREDENTIALS_JSON
- Parses columns: slide_index, name, category, price
- Returns empty list if Sheets not configured (graceful fallback)
- Handles errors with logging, doesn't crash the app

**Sheet Format**:
```
| slide_index | name        | category | price   |
|-------------|-------------|----------|---------|
| 23          | Product A   | Cat 1    | 50000   |
| 24          | Product B   | Cat 1    | 75000   |
```

## Data Flow

### Getting Products

```
GET /api/products
    ↓
Try Google Sheets (if configured)
    ↓ (success)
Return products
    ↓ (fail/not configured)
Fall back to CSV file
    ↓
Parse products_catalog.csv
    ↓
Return products
```

### Generating Deck

```
POST /api/generate
{sponsor_name, rep_name, selected_products}
    ↓
Validate request
    ↓
Create temp directory
    ↓
Copy template PPTX
    ↓
Load with python-pptx
    ↓
Calculate removal list
(all products not in selected_products)
    ↓
Remove slides (reverse order)
    ↓
Insert proposal slide
    ↓
Save PPTX
    ↓
Convert to PDF (LibreOffice)
    ↓
Return PDF file
    ↓
Clean up temp directory
```

## Environment Configuration

```ini
# Required
TEMPLATE_PATH=./template.pptx

# Optional - CSV fallback
PRODUCTS_CSV=./products_catalog.csv

# Optional - Google Sheets
GOOGLE_SHEET_ID=spreadsheet-id
GOOGLE_CREDENTIALS_JSON=/path/to/service-account.json

# Server (optional)
HOST=0.0.0.0
PORT=8000
```

## Error Handling

### Template Not Found
- Application starts but logs warning
- Returns 500 error when deck generation requested
- Error message specifies missing template path

### Products Loading
- Tries Google Sheets first
- Silently falls back to CSV
- Returns empty list if both unavailable
- Logs all errors without crashing

### Deck Generation Failures
- PDF conversion failures caught and reported
- Slide removal errors logged and raised
- Temp directory cleaned up on error
- Returns 500 error with descriptive message

### Request Validation
- FastAPI validates request body against Pydantic models
- Returns 422 error for invalid requests
- Returns 400 error for business logic failures (e.g., no products)

## File Management

### Temporary Files
- Created in system temp directory with prefix "humanx_deck_"
- Contains:
  - working.pptx (modified template)
  - *.pdf (generated PDF)
- Cleaned up after response sent
- Robust error handling ensures cleanup even if errors occur

### Output Files
- PDF filename format: `HumanX_2026_Proposal_{sponsor_name}.pdf`
- Special characters in sponsor name sanitized
- Sent as FileResponse with appropriate MIME type

## Performance Considerations

### Timeouts
- PDF conversion has 120 second timeout
- Subprocess calls fail gracefully if timeout exceeded

### Resource Usage
- Temp files cleaned up immediately after use
- No persistent state between requests
- Thread-safe for multi-worker deployment

### Logging
- All requests logged with duration
- Debug logging for internal operations
- Error logging for failures
- Structured format for parsing

## Security Considerations

### CORS
- Currently allows all origins (development setting)
- Should be restricted in production to frontend domain(s)

### File Handling
- All paths properly quoted
- No path traversal vulnerabilities
- Temp files in dedicated directory
- File cleanup on errors

### Input Validation
- Request body validated by Pydantic
- Sponsor name sanitized for filename
- Product indices validated against template

### Google Sheets
- Uses service account (not user credentials)
- Credentials stored in env var (not hardcoded)
- API scope restricted to read-only access

## Scalability

### Stateless Design
- Each request is independent
- No persistent connections
- Can run multiple workers

### Load Balancing
- Horizontal scaling with multiple uvicorn workers
- Use reverse proxy (nginx) in production
- Load balance across worker processes

### Resource Limits
- Each deck generation creates temp directory
- Should monitor disk space usage
- Consider cleanup job for orphaned temp files
- PDF conversion CPU-intensive (may limit concurrent requests)

## Testing Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Get Products
```bash
curl http://localhost:8000/api/products
```

### Generate Deck
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "sponsor_name": "Acme Corp",
    "rep_name": "John Doe",
    "selected_products": [
      {"slide_index": 23, "name": "Product A", "price": 50000}
    ]
  }' \
  --output deck.pdf
```

## Dependencies and Versions

- **fastapi 0.111.0**: Web framework
- **uvicorn 0.29.0**: ASGI server
- **python-pptx 0.6.23**: PowerPoint manipulation
- **google-auth 2.29.0**: Google authentication
- **google-api-python-client 2.128.0**: Google Sheets API
- **python-dotenv 1.0.1**: Environment configuration
- **Pillow 10.3.0**: Image processing
- **lxml 5.2.2**: XML handling

See requirements.txt for complete list.
