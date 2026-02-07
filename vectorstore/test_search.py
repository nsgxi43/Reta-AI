from vectorstore.search import VectorSearch
from rules.filters import (
    filter_by_category,
    filter_by_color,
    prefer_size
)

vs = VectorSearch()

query = "toothpaste for sensitive teeth"

results = vs.search(query, top_k=10)

# Apply retail rules
results = filter_by_category(results, "Toothpaste")
results = filter_by_color(results, "Blue")
results = prefer_size(results, "100g")

for r in results:
    print(
        r["product_name"],
        "|",
        r["product_category"],
        "|",
        r["assigned_color"]
    )
