"""
FastAPI Backend for HumanX Deck Generator

Provides REST endpoints for:
- Loading product catalog from Google Sheets or CSV
- Generating custom sponsorship decks from template
- Health checks
"""

import logging
import os
import shutil
import urllib.request
from typing import List, Optional
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from sheets_client import get_products_from_sheet
from deck_generator import generate_deck

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "./template.pptx")
TEMPLATE_URL = os.getenv("TEMPLATE_URL", "")  # Optional: URL to download template on startup
PRODUCTS_CSV = os.getenv("PRODUCTS_CSV", "./products_catalog.csv")


def download_template_if_needed():
    """
    If TEMPLATE_URL is set and the template file doesn't exist locally, download it.
    Supports direct URLs (S3, GCS signed URLs, Dropbox, etc.)
    """
    if not TEMPLATE_URL:
        return

    if os.path.exists(TEMPLATE_PATH):
        logger.info(f"Template already exists at {TEMPLATE_PATH}, skipping download")
        return

    logger.info(f"Template not found locally. Downloading from TEMPLATE_URL...")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(TEMPLATE_PATH)), exist_ok=True)
        urllib.request.urlretrieve(TEMPLATE_URL, TEMPLATE_PATH)
        size_mb = os.path.getsize(TEMPLATE_PATH) / (1024 * 1024)
        logger.info(f"Template downloaded successfully: {TEMPLATE_PATH} ({size_mb:.1f} MB)")
    except Exception as e:
        logger.error(f"Failed to download template from {TEMPLATE_URL}: {e}")
        raise RuntimeError(f"Could not download template: {e}")

# Pydantic models
class Product(BaseModel):
    """Product model from catalog"""
    slide_index: int
    name: str
    category: str
    price: Optional[float] = None


class SelectedProduct(BaseModel):
    """Selected product for generation request"""
    slide_index: int
    name: str
    price: Optional[float] = None


class GenerationRequest(BaseModel):
    """Request model for deck generation"""
    sponsor_name: str
    rep_name: str
    sponsor_email: Optional[str] = None
    selected_products: List[SelectedProduct]


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle handler"""
    # Startup
    logger.info("=== HumanX Deck Generator Starting ===")

    # Download template from URL if configured and not already present
    download_template_if_needed()

    if not os.path.exists(TEMPLATE_PATH):
        logger.error(f"Template PPTX not found at: {TEMPLATE_PATH}")
        logger.warning("Set TEMPLATE_URL env var to auto-download on startup, or mount the file directly")
    else:
        logger.info(f"Template PPTX found at: {TEMPLATE_PATH}")
    
    logger.info(f"Products CSV path: {PRODUCTS_CSV}")
    
    yield
    
    # Shutdown
    logger.info("=== HumanX Deck Generator Shutting Down ===")


# Create FastAPI app
app = FastAPI(
    title="HumanX Deck Generator API",
    description="REST API for generating custom sponsorship decks",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request/response logging with timing
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests with timing"""
    import time
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.3f}s"
    )
    
    return response


# Routes
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "HumanX Deck Generator"
    }


@app.get("/api/products", response_model=List[Product], tags=["Products"])
async def get_products():
    """
    Get available products from catalog.
    
    Tries to load from Google Sheets first, falls back to CSV if not configured.
    
    Returns:
        List of products with slide_index, name, category, price
    """
    logger.info("Fetching products from catalog")
    
    # Try Google Sheets first
    products = get_products_from_sheet()
    
    if products:
        logger.info(f"Loaded {len(products)} products from Google Sheets")
        return products
    
    # Fall back to CSV
    logger.info("Google Sheets not configured or empty, attempting CSV fallback")
    
    if not os.path.exists(PRODUCTS_CSV):
        logger.warning(f"Products CSV not found at: {PRODUCTS_CSV}")
        return []
    
    try:
        import csv
        products = []
        
        with open(PRODUCTS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    product = Product(
                        slide_index=int(row.get('slide_index', 0)),
                        name=row.get('name', ''),
                        category=row.get('category', ''),
                        price=float(row.get('price')) if row.get('price') else None
                    )
                    products.append(product)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing product row: {row}, error: {e}")
                    continue
        
        logger.info(f"Loaded {len(products)} products from CSV")
        return products
    
    except Exception as e:
        logger.error(f"Error reading products CSV: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading products catalog: {str(e)}"
        )


@app.post("/api/generate", tags=["Generation"])
async def generate_deck_endpoint(request: GenerationRequest):
    """
    Generate a custom sponsorship deck PDF.
    
    Accepts sponsor information and selected products, returns a PDF file.
    
    Args:
        request: GenerationRequest with sponsor_name, rep_name, selected_products
    
    Returns:
        PDF file as FileResponse
    """
    logger.info(
        f"Received deck generation request for sponsor: {request.sponsor_name}, "
        f"rep: {request.rep_name}, products: {len(request.selected_products)}"
    )
    
    if not os.path.exists(TEMPLATE_PATH):
        logger.error(f"Template not found: {TEMPLATE_PATH}")
        raise HTTPException(
            status_code=500,
            detail=f"Template PPTX not found at {TEMPLATE_PATH}"
        )
    
    if not request.selected_products:
        logger.warning("No products selected for deck generation")
        raise HTTPException(
            status_code=400,
            detail="At least one product must be selected"
        )
    
    tmpdir = None
    pdf_path = None
    
    try:
        # Convert selected products to dict format for deck_generator
        selected_products = [
            {
                "slide_index": p.slide_index,
                "name": p.name,
                "price": p.price
            }
            for p in request.selected_products
        ]
        
        sponsor_info = {
            "sponsor_name": request.sponsor_name,
            "rep_name": request.rep_name,
            "sponsor_email": request.sponsor_email
        }
        
        logger.info(f"Generating deck with template: {TEMPLATE_PATH}")
        
        # Generate deck
        pdf_path, tmpdir = generate_deck(
            TEMPLATE_PATH,
            selected_products,
            sponsor_info
        )
        
        logger.info(f"Deck generated successfully: {pdf_path}")
        
        # Create filename for download
        safe_sponsor_name = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '_'
            for c in request.sponsor_name
        ).strip()
        download_filename = f"HumanX_2026_Proposal_{safe_sponsor_name}.pdf"
        
        logger.info(f"Returning PDF as download: {download_filename}")
        
        # Return PDF
        return FileResponse(
            path=pdf_path,
            filename=download_filename,
            media_type="application/pdf"
        )
    
    except FileNotFoundError as e:
        logger.error(f"File not found error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
    except RuntimeError as e:
        logger.error(f"Deck generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate deck: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during deck generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    
    finally:
        # Clean up temp directory after sending file
        if tmpdir and os.path.exists(tmpdir):
            try:
                logger.info(f"Cleaning up temp directory: {tmpdir}")
                shutil.rmtree(tmpdir)
            except Exception as e:
                logger.warning(f"Error cleaning up temp directory {tmpdir}: {e}")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API documentation"""
    return {
        "service": "HumanX Deck Generator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "products": "/api/products",
            "generate": "/api/generate",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    logger.info("Starting HumanX Deck Generator server")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
