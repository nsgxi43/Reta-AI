from vectorstore.search import VectorSearch

TEST_QUERIES = [
    "toothpaste for sensitive teeth",
    "shampoo for dandruff",
    "biscuits for kids",
    "healthy cooking oil",
    "milk alternatives",
    "cheap soap",
    "protein rich breakfast"
]

def run_eval():
    searcher = VectorSearch()

    for q in TEST_QUERIES:
        print("\n" + "=" * 60)
        print(f"QUERY: {q}")
        print("-" * 60)

        results = searcher.search(q, top_k=5)

        for i, r in enumerate(results, 1):
            print(
                f"{i}. {r.get('product_name')} | "
                f"{r.get('product_category')} | "
                f"{r.get('color_zone')}"
            )

if __name__ == "__main__":
    run_eval()
