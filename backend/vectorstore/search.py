import faiss
from pathlib import Path
from embeddings.embedder import Embedder

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "products.index"
META_PATH = BASE_DIR / "products_meta.pkl"


class VectorSearch:
    def __init__(self):
        self.embedder = Embedder()
        self.index = faiss.read_index(str(INDEX_PATH))
        
        # Load full dataframe metadata for all 18 columns
        import pandas as pd
        self.df = pd.read_pickle(str(META_PATH))
        self.products_by_idx = self.df.to_dict(orient="index")

    def get_all_products(self):
        """Return all products as list of dicts with all 18 columns."""
        return self.df.to_dict(orient="records")

    def search(self, query: str, top_k: int = 5):
        """Search with FAISS and return full product dicts, deduplicated by product_name."""
        query_vector = self.embedder.embed([query])

        distances, indices = self.index.search(query_vector, top_k * 3)

        seen = set()
        results = []

        for idx in indices[0]:
            product = self.products_by_idx[idx]
            name = product["product_name"]

            # Deduplicate by product_name (not product_id) 
            # to collapse size variants when user hasn't specified size
            if name not in seen:
                seen.add(name)
                results.append(product)

            if len(results) == top_k:
                break

        return results
