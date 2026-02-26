"""
FastAPI Backend for HumanX Deck Generator
"""

import logging
import os
import shutil
import urllib.request
from typing import List, Optional
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from sheets_client import get_products_from_sheet
from deck_generator import generate_deck

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    logger.info("Downloading template from TEMPLATE_URL...")
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
        logger.warning("Template not found. Use /upload-template to upload it.")
    else:
        size_mb = os.path.getsize(TEMPLATE_PATH) / (1024 * 1024)
        logger.info(f"Template found: {TEMPLATE_PATH} ({size_mb:.1f} MB)")
    logger.info(f"Products CSV: {PRODUCTS_CSV}")
    yield
    logger.info("=== Shutting Down ===")


app = FastAPI(title="HumanX Deck Generator API", version="1.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {time.time()-start:.3f}s")
    return response


@app.get("/health")
async def health_check():
    template_ok = os.path.exists(TEMPLATE_PATH)
    template_size = round(os.path.getsize(TEMPLATE_PATH) / (1024*1024), 1) if template_ok else 0
    return {"status": "ok", "timestamp": datetime.now().isoformat(), "template_ready": template_ok, "template_size_mb": template_size}


@app.post("/upload-template")
async def upload_template(key: str, file: UploadFile = File(...)):
    """Upload the PPTX template directly. Pass ?key=YOUR_UPLOAD_KEY"""
    upload_key = os.getenv("UPLOAD_KEY", "")
    if not upload_key or key != upload_key:
        raise HTTPException(status_code=403, detail="Invalid or missing upload key")
    contents = await file.read()
    with open(TEMPLATE_PATH, "wb") as f:
        f.write(contents)
    size_mb = os.path.getsize(TEMPLATE_PATH) / (1024 * 1024)
    logger.info(f"Template uploaded: {TEMPLATE_PATH} ({size_mb:.1f} MB)")
    return {"status": "ok", "size_mb": round(size_mb, 1)}


@app.get("/api/products", response_model=List[Product])
async def get_products():
    logger.info("Fetching products")
    products = get_products_from_sheet()
    if products:
        return products
    if not os.path.exists(PRODUCTS_CSV):
        return []
    try:
        import csv
        products = []
        with open(PRODUCTS_CSV, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    products.append(Product(
                        slide_index=int(row.get('slide_index', 0)),
                        name=row.get('name', ''),
                        category=row.get('category', ''),
                        price=float(row.get('price')) if row.get('price') else None
                    ))
                except (ValueError, KeyError):
                    continue
        logger.info(f"Loaded {len(products)} products from CSV")
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def generate_deck_endpoint(request: GenerationRequest):
    logger.info(f"Generating deck for: {request.sponsor_name}, {len(request.selected_products)} products")
    if not os.path.exists(TEMPLATE_PATH):
        raise HTTPException(status_code=500, detail="Template not found. Please upload it via /upload-template")
    if not request.selected_products:
        raise HTTPException(status_code=400, detail="At least one product must be selected")
    tmpdir = None
    try:
        selected = [{"slide_index": p.slide_index, "name": p.name, "price": p.price} for p in request.selected_products]
        sponsor = {"sponsor_name": request.sponsor_name, "rep_name": request.rep_name, "sponsor_email": request.sponsor_email}
        pdf_path, tmpdir = generate_deck(TEMPLATE_PATH, selected, sponsor)
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in request.sponsor_name).strip()
        return FileResponse(path=pdf_path, filename=f"HumanX_2026_Proposal_{safe_name}.pdf", media_type="application/pdf")
    except Exception as e:
        logger.error(f"Error: {e}")
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
