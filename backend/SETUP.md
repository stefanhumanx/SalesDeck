# Quick Start Guide - HumanX Deck Generator Backend

## Prerequisites

- Python 3.8+
- LibreOffice (for PDF conversion)
- (Optional) Google Sheets account with service account credentials

## Installation & Setup (5 minutes)

### 1. Install Dependencies

```bash
cd /sessions/optimistic-peaceful-noether/humanx-deck-generator/backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example config
cp .env.example .env

# Edit .env with your settings
nano .env  # or your preferred editor
```

Minimum configuration:
```env
TEMPLATE_PATH=./template.pptx
PRODUCTS_CSV=./products_catalog.csv
```

### 3. Prepare Files

1. **Place your PowerPoint template** at the path specified in `TEMPLATE_PATH`
   - Template should have:
     - Slides 0-22: Intro slides (static)
     - Slides 23-128: Product slides
     - Slides 129-131: Closing slides (static)

2. **Place or create** `products_catalog.csv` with columns:
   ```
   slide_index,name,category,price
   23,Product A,Category,50000
   24,Product B,Category,75000
   ```

### 4. Start the Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

The API is now available at: **http://localhost:8000**

## API Usage Examples

### Check Server Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2026-02-25T22:20:00.123456",
  "service": "HumanX Deck Generator"
}
```

### Get Available Products

```bash
curl http://localhost:8000/api/products
```

Response:
```json
[
  {
    "slide_index": 23,
    "name": "Product A",
    "category": "Category 1",
    "price": 50000.0
  },
  {
    "slide_index": 24,
    "name": "Product B",
    "category": "Category 1",
    "price": 75000.0
  }
]
```

### Generate a Deck

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "sponsor_name": "Acme Corporation",
    "rep_name": "Jane Smith",
    "sponsor_email": "jane@acme.com",
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
  }' \
  --output "HumanX_Proposal_Acme.pdf"
```

The PDF will be saved as `HumanX_Proposal_Acme.pdf`

## Using the Interactive API Docs

FastAPI provides interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these to test endpoints directly in your browser!

## Docker Deployment

### Build and Run with Docker

```bash
# Build image
docker build -t humanx-deck-generator .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/template.pptx:/app/template.pptx:ro \
  -v $(pwd)/products_catalog.csv:/app/products_catalog.csv:ro \
  humanx-deck-generator
```

### Using Docker Compose

```bash
# Start services
docker-compose up

# Stop services
docker-compose down
```

## Google Sheets Integration (Optional)

### Setup Steps

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com
   - Create new project

2. **Enable Google Sheets API**
   - In APIs & Services, enable "Google Sheets API"

3. **Create Service Account**
   - In APIs & Services → Credentials
   - Create new service account
   - Create JSON key
   - Download and save as `google-credentials.json`

4. **Share Google Sheet**
   - Create a sheet with products (columns: slide_index, name, category, price)
   - Get the spreadsheet ID from the URL: `docs.google.com/spreadsheets/d/{ID}/`
   - Share the sheet with the service account email

5. **Configure Environment**
   ```env
   GOOGLE_SHEET_ID=your-spreadsheet-id
   GOOGLE_CREDENTIALS_JSON=./google-credentials.json
   ```

6. **Restart Server**
   ```bash
   python main.py
   ```

Products will now load from Google Sheets automatically!

## Troubleshooting

### "Template not found" Error

**Problem**: `FileNotFoundError: Template not found: ./template.pptx`

**Solution**:
1. Check that `TEMPLATE_PATH` in `.env` is correct
2. Ensure the file exists: `ls -l ./template.pptx`
3. Use absolute path if relative path doesn't work: `TEMPLATE_PATH=/full/path/to/template.pptx`

### "PDF conversion failed" Error

**Problem**: `RuntimeError: Failed to convert PPTX to PDF`

**Solution**:
1. Install LibreOffice:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libreoffice

   # macOS
   brew install libreoffice

   # CentOS/RHEL
   sudo yum install libreoffice
   ```
2. Check that soffice is available: `which soffice`
3. Check logs for more details

### Products not loading from CSV

**Problem**: `/api/products` returns empty list

**Solution**:
1. Check CSV exists: `ls -l ./products_catalog.csv`
2. Verify CSV format:
   - Header row: `slide_index,name,category,price`
   - Data rows with valid values
3. Check for parsing errors in logs
4. Use absolute path if relative doesn't work

### ModuleNotFoundError for google modules

**Problem**: Import error even though Google libraries are in requirements.txt

**Solution**:
1. This is expected if Google Sheets not configured
2. Ensure you installed requirements: `pip install -r requirements.txt`
3. Check that Google Sheets env vars are NOT set (falls back gracefully)
4. If you need Google Sheets, properly set up service account

## Monitoring & Logs

All requests are logged with timing information:

```
2026-02-25 22:20:15,123 - main - INFO - GET /api/products - Status: 200 - Duration: 0.045s
2026-02-25 22:20:20,456 - main - INFO - POST /api/generate - Status: 200 - Duration: 15.234s
```

View logs in real-time:
```bash
python main.py 2>&1 | tee server.log
```

## Performance Tips

1. **For large decks**: PDF conversion can take 10-30 seconds
2. **Multiple workers**: Use `-w 4` flag for production:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```
3. **Monitor disk**: Check `/tmp` for orphaned temp files periodically

## Next Steps

1. **Test the API**: Use curl examples above or open http://localhost:8000/docs
2. **Integrate with frontend**: Frontend should POST to `/api/generate`
3. **Configure Google Sheets** (optional): Follow Google Sheets Integration section
4. **Deploy**: Use Docker for easy production deployment

## File Reference

- **main.py**: FastAPI application with routes
- **deck_generator.py**: Core PPTX manipulation logic
- **sheets_client.py**: Google Sheets integration
- **products_catalog.csv**: Example products (CSV fallback)
- **requirements.txt**: Python dependencies
- **.env.example**: Example environment configuration
- **README.md**: Full documentation
- **ARCHITECTURE.md**: Technical architecture details
- **Dockerfile**: Docker container definition
- **docker-compose.yml**: Docker Compose configuration

## Getting Help

1. Check logs for error messages
2. Review ARCHITECTURE.md for technical details
3. Check README.md for comprehensive documentation
4. Test endpoints with FastAPI docs at http://localhost:8000/docs
5. Ensure template PPTX has correct structure (intro/products/closing)

---

**Ready to generate some decks!** 🎉
