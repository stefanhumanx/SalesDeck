# HumanX Deck Generator Backend

REST API for generating custom sponsorship decks from a PowerPoint template.

## Features

- Load product catalog from Google Sheets or CSV fallback
- Generate custom sponsorship decks by selecting products from template
- Convert presentations to PDF using LibreOffice
- Health checks and request logging
- CORS enabled for frontend development

## Project Structure

```
backend/
├── main.py                 # FastAPI application with REST endpoints
├── deck_generator.py       # Core logic for deck generation
├── sheets_client.py        # Google Sheets integration
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment configuration
├── .gitignore             # Git ignore patterns
└── README.md              # This file
```

## Setup

### 1. Create Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required
TEMPLATE_PATH=./template.pptx

# Optional - Product catalog
PRODUCTS_CSV=./products_catalog.csv

# Optional - Google Sheets configuration
GOOGLE_SHEET_ID=your-spreadsheet-id
GOOGLE_CREDENTIALS_JSON=/path/to/service-account-key.json
```

### 4. Prepare Template and Products

- Place your PowerPoint template at the path specified in `TEMPLATE_PATH`
- Place your products CSV at the path specified in `PRODUCTS_CSV` (if using CSV fallback)

#### Products CSV Format

```csv
slide_index,name,category,price
23,Product A,Category 1,50000
24,Product B,Category 1,75000
25,Product C,Category 2,100000
```

#### Google Sheets Format

Set up a sheet with columns:
- Column A: slide_index (integer, 23-128)
- Column B: name (product name)
- Column C: category (product category)
- Column D: price (numeric or empty)

## Running the Server

### Development Mode

```bash
python3 main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```
GET /health
```

Returns service health status.

### Get Products

```
GET /api/products
```

Returns list of available products from catalog (Google Sheets or CSV).

**Response:**
```json
[
  {
    "slide_index": 23,
    "name": "Product A",
    "category": "Category 1",
    "price": 50000.0
  }
]
```

### Generate Deck

```
POST /api/generate
Content-Type: application/json
```

Generates a custom sponsorship deck PDF.

**Request Body:**
```json
{
  "sponsor_name": "Acme Corp",
  "rep_name": "John Doe",
  "sponsor_email": "john@acme.com",
  "selected_products": [
    {
      "slide_index": 23,
      "name": "Product A",
      "price": 50000.0
    },
    {
      "slide_index": 24,
      "name": "Product B",
      "price": 75000.0
    }
  ]
}
```

**Response:**
- Returns PDF file download with filename: `HumanX_2026_Proposal_{sponsor_name}.pdf`

## Template Structure

The PowerPoint template is expected to have:

- **Slides 0-22**: Static intro/front matter slides
- **Slides 23-128**: Product slides (106 total)
- **Slides 129-131**: Static closing slides

When generating a deck:
1. Keep intro slides (0-22)
2. Insert proposal slide at position 23
3. Keep only selected product slides
4. Keep closing slides
5. Convert to PDF

## Deck Generation Logic

The `deck_generator.py` module:

1. **Copies** the template to a temporary directory
2. **Removes** unselected product slides
3. **Inserts** a custom proposal/quote slide with:
   - Dark background (#1a1a2e)
   - Gold accents (#f5a623)
   - Sponsor and rep information
   - Product listing with prices
   - Total investment
   - Generation date
4. **Converts** to PDF using LibreOffice

## Google Sheets Setup

1. Create a Google Cloud project
2. Enable the Google Sheets API
3. Create a service account with Sheets access
4. Download the service account JSON key
5. Create a Google Sheet with the products catalog
6. Set environment variables:
   - `GOOGLE_SHEET_ID`: Your spreadsheet ID
   - `GOOGLE_CREDENTIALS_JSON`: Path to the service account JSON file

## Logging

All requests are logged with timing information. Check console output for:
- Request method, path, status code, and duration
- Product loading (from Sheets or CSV)
- Deck generation steps
- Any errors or warnings

## Troubleshooting

### Template Not Found

Ensure `TEMPLATE_PATH` in `.env` points to a valid PPTX file. Default is `./template.pptx` in the same directory as `main.py`.

### Products Not Loading

1. Check `PRODUCTS_CSV` path exists
2. Verify CSV format (see Products CSV Format above)
3. Check logs for specific parsing errors

### PDF Conversion Fails

Ensure LibreOffice is installed:

```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# macOS
brew install libreoffice

# Or use the provided soffice.py wrapper
```

### Google Sheets Connection Issues

1. Verify `GOOGLE_CREDENTIALS_JSON` path
2. Ensure service account has Sheets API access
3. Check sheet structure matches expected format
4. Review logs for authentication errors

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **python-pptx**: PowerPoint manipulation
- **google-auth/google-api-python-client**: Google Sheets integration
- **python-dotenv**: Environment configuration
- **Pillow**: Image handling
- **lxml**: XML processing

See `requirements.txt` for versions.

## Development

### Code Structure

- `main.py`: FastAPI app, routes, middleware
- `deck_generator.py`: PPTX manipulation, PDF conversion
- `sheets_client.py`: Google Sheets API client

### Adding New Endpoints

1. Define request/response Pydantic models
2. Add route function with `@app.get()` or `@app.post()` decorator
3. Add appropriate logging
4. Add docstrings

### Modifying Proposal Slide

Edit the `add_quote_slide()` function in `deck_generator.py` to customize:
- Colors and styling
- Layout and spacing
- Text content and formatting
- Table structure

## License

Internal HumanX project.
