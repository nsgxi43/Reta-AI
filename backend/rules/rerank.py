def rerank_products(products, intent, preferred_size=None):
    ranked = []

    for p in products:
        score = 0.0

        # Size preference (soft)
        if preferred_size and preferred_size.lower() in p.get("size_variant", "").lower():
            score += 0.3

        # Intent-based boosts
        if intent == "nutrition":
            if p.get("product_category") in ["Health Foods", "Breakfast Cereals"]:
                score += 0.4

        if intent == "budget":
            # Smaller packs often cheaper
            if any(x in p.get("size_variant", "").lower() for x in ["25g", "50g", "100g"]):
                score += 0.2

        # Brand trust (example)
        if p.get("brand") in ["Sensodyne", "Saffola", "HUL", "Nestle"]:
            score += 0.1

        ranked.append((score, p))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in ranked]
