# rules/intent_filters.py

def apply_intent_rules(products, intent, query):
    q = query.lower()

    if intent == "budget":
        products = [
            p for p in products
            if p.get("product_category") not in ["Detergent"]
        ]

    if intent == "nutrition":
        products = [
            p for p in products
            if p.get("product_category") in [
                "Breakfast Cereals",
                "Dairy Alternatives",
                "Health Foods"
            ]
        ]

    if intent == "category_alternative":
        if "milk" in q:
            products = [
                p for p in products
                if p.get("product_category") in ["Dairy Alternatives"]
            ]

    return products
