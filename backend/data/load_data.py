import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "product_improved_2000.xlsx"

def load_products():
    """Load product_improved_2000.xlsx with all 18 columns.
    
    Exposes: product_id, product_name, brand, product_line, product_category,
    short_description, long_description, size_variant, unit_type, price_inr,
    price_tier, stock_available, seasonal, assigned_color, source,
    alternate_product_ids, embedding_text (pre-constructed, use as-is)
    """
    df = pd.read_excel(DATA_PATH)
    df = df.fillna("")
    
    # Type conversions for critical fields
    df["stock_available"] = df["stock_available"].astype(bool)
    df["seasonal"] = df["seasonal"].astype(bool)
    df["price_inr"] = pd.to_numeric(df["price_inr"], errors="coerce")
    
    # embedding_text column is already present — use directly, no reconstruction
    return df
