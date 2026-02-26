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

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "./template.pptx")
TEMPLATE_URL = os.getenv("TEMPLATE_URL", "")
PRODUCTS_CSV = os.getenv("PRODUCTS_CSV", "./products_catalog.csv")


def download_template_if_needed():
    if not TEMPLATE_URL:
        return
    if os.path.exists(TEMPLATE_PATH):
        logger.info(f"Template already exists at {TEMPLATE_PATH}, skipping download")
        return
    logger.info("Template not found locally. Downloading from TEMPLATE_URL...")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(TEMPLATE_PATH)), exist_ok=True)
        urllib.request.urlretrieve(TEMPLATE_URL, TEMPLATE_PATH)
        size_mb = os.path.getsize(TEMPLATE_PATH) / (1024 * 1024)
        logger.info(f"Template downloaded: {TEMPLATE_PATH} ({size_mb:.1f} MB)")
    except Exception as e:
        logger.error(f"Failed to download template: {e}")
        raise RuntimeError(f"Could not download template: {e}")


class Product(BaseModel):
    slide_index: int
    name: str
    category: str
    price: Optional[float] = None


class SelectedProduct(BaseModel):
    slide_index: int
    name: str
    price: Optional[float] = None


class GenerationRequest(BaseModel):
    sponsor_name: str
    rep_name: str
    sponsor_email: Optional[str] = None
    selected_products: List[SelectedProduct]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== HumanX Deck Generator Starting ===")
    download_template_if_needed()
    if not os.path.exists(TEMPLATE_PATH):
        logger.error(f"Template PPTX not found at: {TEMPLATE_PATH}")
        logger.warning("Set TEMPLATE_URL env var to auto-download on startup")
    else:
        logger.info(f"Template PPTX found at: {TEMPLATE_PATH}")
    logger.info(f"Products CSV path: {PRODUCTS_CSV}")
    yield
    logger.info("=== HumanX Deck Generator Shutting Down ===")


app = FastAPI(
    title="HumanX Deck Generator API",
    description="REST API for generating custom sponsorship decks",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.3f}s")
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat(), "service": "HumanX Deck Generator"}


@app.get("/api/products", response_model=List[Product])
async def get_products():
    logger.info("Fetching products from catalog")
    products = get_products_from_sheet()
    if products:
        logger.info(f"Loaded {len(products)} products from Google Sheets")
        return products
    logger.info("Falling back to CSV")
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
                    products.append(Product(
                        slide_index=int(row.get('slide_index', 0)),
                        name=row.get('name', ''),
                        category=row.get('category', ''),
                        price=float(row.get('price')) if row.get('price') else None
                    ))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing row: {row}, error: {e}")
        logger.info(f"Loaded {len(products)} products from CSV")
        return products
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading products catalog: {str(e)}")


@app.post("/api/generate")
async def generate_deck_endpoint(request: GenerationRequest):
    logger.info(f"Generating deck for: {request.sponsor_name}, products: {len(request.selected_products)}")
    if not os.path.exists(TEMPLATE_PATH):
        raise HTTPException(status_code=500, detail=f"Template PPTX not found at {TEMPLATE_PATH}")
    if not request.selected_products:
        raise HTTPException(status_code=400, detail="At least one product must be selected")
    tmpdir = None
    try:
        selected_products = [{"slide_index": p.slide_index, "name": p.name, "price": p.price} for p in request.selected_products]
        sponsor_info = {"sponsor_name": request.sponsor_name, "rep_name": request.rep_name, "sponsor_email": request.sponsor_email}
        pdf_path, tmpdir = generate_deck(TEMPLATE_PATH, selected_products, sponsor_info)
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in request.sponsor_name).strip()
        return FileResponse(path=pdf_path, filename=f"HumanX_2026_Proposal_{safe_name}.pdf", media_type="application/pdf")
    except Exception as e:
        logger.error(f"Error generating deck: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmpdir and os.path.exists(tmpdir):
            shutil.rmtree(tmpdir, ignore_errors=True)


@app.get("/")
async def root():
    return {"service": "HumanX Deck Generator API", "version": "1.0.0"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, log_level="info")
