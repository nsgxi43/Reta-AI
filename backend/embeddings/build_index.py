import sys
from pathlib import Path

# Add backend root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import faiss
from data.load_data import load_products
from embeddings.embedder import Embedder

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR.parent / "vectorstore" / "products.index"
META_PATH = BASE_DIR.parent / "vectorstore" / "products_meta.pkl"

def build_index():
    """Build FAISS index from embedding_text column.
    
    - Encodes texts with normalize_embeddings=True
    - Saves normalized embeddings to IndexFlatIP
    - Saves full dataframe as pickle for metadata lookups
    """
    df = load_products()
    
    print(f"Loading {len(df)} products...")
    
    # Extract embedding texts (already pre-constructed in dataset)
    texts = df["embedding_text"].tolist()
    
    embedder = Embedder()
    print("Encoding embeddings with normalize_embeddings=True...")
    embeddings = embedder.embed(texts)
    
    # Create and populate FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    # Save FAISS index
    faiss.write_index(index, str(INDEX_PATH))
    print(f"✅ FAISS index saved to {INDEX_PATH}")
    
    # Save full dataframe metadata for join-on-index lookups
    df.to_pickle(str(META_PATH))
    print(f"✅ Metadata pickle saved to {META_PATH}")
    
    print(f"✅ Index built with {len(df)} products, dimension={dimension}")

if __name__ == "__main__":
    build_index()
