"""
Google Sheets Client

Reads the product catalog from a Google Sheet.
Sheet structure: slide_index | name | category | price

Requires env vars:
- GOOGLE_SHEET_ID: the spreadsheet ID
- GOOGLE_CREDENTIALS_JSON: path to service account JSON file
"""

import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_products_from_sheet() -> List[Dict[str, Any]]:
    """
    Fetch products from Google Sheet.
    
    Returns:
        List of product dicts with keys: slide_index, name, category, price
    """
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_JSON")
    
    if not sheet_id or not credentials_path:
        logger.debug(
            "Google Sheets not configured. Missing GOOGLE_SHEET_ID or GOOGLE_CREDENTIALS_JSON"
        )
        return []
    
    if not os.path.exists(credentials_path):
        logger.warning(f"Google credentials file not found: {credentials_path}")
        return []
    
    try:
        # Import Google libs only when needed to avoid dependency issues
        from google.oauth2.service_account import Credentials as ServiceAccountCredentials
        from googleapiclient.discovery import build
        
        creds = ServiceAccountCredentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=creds)
        
        # Fetch data from the first sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1!A:D"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            logger.warning("No data found in Google Sheet")
            return []
        
        products = []
        # Skip header row (row 0)
        for row in values[1:]:
            if len(row) < 4:
                continue
            
            try:
                slide_index = int(row[0])
                name = str(row[1])
                category = str(row[2])
                price = float(row[3]) if row[3] else None
                
                products.append({
                    "slide_index": slide_index,
                    "name": name,
                    "category": category,
                    "price": price
                })
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parsing row: {row}, error: {e}")
                continue
        
        logger.info(f"Loaded {len(products)} products from Google Sheet")
        return products
    
    except ImportError as e:
        logger.warning(f"Google Sheets libraries not available: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching products from Google Sheet: {e}")
        return []
