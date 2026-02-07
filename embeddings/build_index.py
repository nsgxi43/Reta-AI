import faiss
import pickle
from data.load_data import load_products
from embeddings.embedder import Embedder

INDEX_PATH = "vectorstore/faiss_index.bin"
META_PATH = "vectorstore/products.pkl"

def build_index():
    df = load_products()

    embedder = Embedder()
    embeddings = embedder.embed(df["embedding_text"].tolist())

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Save FAISS index
    faiss.write_index(index, INDEX_PATH)

    # Save metadata (for lookup)
    with open(META_PATH, "wb") as f:
        pickle.dump(df.to_dict(orient="records"), f)

    print(f"Index built with {len(df)} products")

if __name__ == "__main__":
    build_index()
