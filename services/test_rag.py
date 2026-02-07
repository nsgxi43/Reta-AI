from services.rag_service import RAGService

def main():
    rag = RAGService()

    result = rag.query(
        user_query="toothpaste for sensitive teeth",
        category="Toothpaste",
        color="Blue",
        preferred_size="100g"
    )

    print("\n=== AI RESPONSE ===\n")
    print(result["response"])

    print("\n=== RETRIEVED PRODUCTS ===\n")
    for p in result["products"]:
        print(
            f"- {p['product_name']} | "
            f"{p['product_category']} | "
            f"{p['assigned_color']}"
        )

if __name__ == "__main__":
    main()
