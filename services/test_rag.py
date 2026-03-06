from services.rag_service import RAGService


def run_test(query: str):
    rag = RAGService()

    print("\n====================================================")
    print("USER QUERY:", query)
    print("====================================================\n")

    result = rag.query(query)

    # Structured Debug Info
    print("PARSED OUTPUT:")
    print(result.get("parsed"))

    print("\nPRIMARY PRODUCT:")
    print(result.get("primary"))

    print("\nALTERNATES:")
    alternates = result.get("alternates") or []
    for alt in alternates:
        print(f"- {alt.get('product_name')} | {alt.get('brand')} | {alt.get('size_variant')}")

    print("\n<<< FULL RESPONSE START >>>\n")
    print(result.get("response"))
    print("\n<<< FULL RESPONSE END >>>\n")


def main():

    test_queries = [

        # ---------------------------
        # 1️⃣ Normal Recommendation
        # ---------------------------
        "toothpaste for sensitive teeth 100g",

        # ---------------------------
        # 2️⃣ Brand Exclusion
        # ---------------------------
        "Not Colgate. Sensitive toothpaste 100g",

        # ---------------------------
        # 3️⃣ Budget Intent
        # ---------------------------
        "best shampoo for daddruff",

        # ---------------------------
        # 4️⃣ Exact Product Match
        # ---------------------------
        "Sensodyne Rapid Relief 100g",

        # ---------------------------
        # 5️⃣ Product Not Found (Fallback)
        # ---------------------------
        "Sensodyne Ultra Pro Max 999g",

        # ---------------------------
        # 6️⃣ Comparison
        # ---------------------------
        "Compare Saffola Gold and Fortune oil",

        # ---------------------------
        # 7️⃣ Small Talk
        # ---------------------------
        "Thank you bro",

        # ---------------------------
        # 8️⃣ Toxic / Random Input
        # ---------------------------
        "fuck off",

        # ---------------------------
        # 9️⃣ Random Natural Language
        # ---------------------------
        "I need something for daily cooking oil",

        # ---------------------------
        # 🔟 Size Constraint Only
        # ---------------------------
        "Sunflower oil 2L",

    ]

    for q in test_queries:
        run_test(q)


if __name__ == "__main__":
    main()
