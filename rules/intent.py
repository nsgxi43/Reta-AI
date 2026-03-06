# rules/intent.py

def classify_intent(query: str) -> str:
    q = query.lower()

    if any(x in q for x in ["cheap", "low cost", "budget"]):
        return "budget"

    if any(x in q for x in ["protein", "healthy", "nutrition", "low sugar"]):
        return "nutrition"

    if any(x in q for x in ["alternative", "substitute", "instead of"]):
        return "category_alternative"

    if any(x in q for x in ["where", "find", "located"]):
        return "navigation"

    return "product_lookup"
