import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "product.xlsx"

def load_products():
    df = pd.read_excel(DATA_PATH)
    df = df.fillna("")

    df["embedding_text"] = (
        df["product_name"] + " " +
        df["short_description"] + " " +
        df["product_category"] + " " +
        df["assigned_color"] + " zone"
    )

    return df
