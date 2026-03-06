import faiss
import pickle
from pathlib import Path
from embeddings.embedder import Embedder

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "faiss_index.bin"
META_PATH = BASE_DIR / "products.pkl"


class VectorSearch:
    def __init__(self):
        self.embedder = Embedder()
        self.index = faiss.read_index(str(INDEX_PATH))
        

        with open(META_PATH, "rb") as f:
            self.products = pickle.load(f)

    def get_all_products(self):
        return self.products


    def search(self, query: str, top_k: int = 5):
        query_vector = self.embedder.embed([query])

        distances, indices = self.index.search(query_vector, top_k * 3)

        seen = set()
        results = []

        for idx in indices[0]:
            product = self.products[idx]
            name = product["product_name"]

            if name not in seen:
                seen.add(name)
                results.append(product)

            if len(results) == top_k:
                break

        return results
