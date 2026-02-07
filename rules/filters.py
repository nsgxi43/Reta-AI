def filter_by_category(products, category):
    if not category:
        return products
    return [
        p for p in products
        if p.get("product_category", "").lower() == category.lower()
    ]


def filter_by_color(products, color):
    if not color:
        return products
    return [
        p for p in products
        if p.get("assigned_color", "").lower() == color.lower()
    ]


def prefer_size(products, preferred_size):
    """
    Reorders products so preferred size appears first if present.
    Does not remove other products.
    """
    if not preferred_size:
        return products

    exact = []
    others = []

    for p in products:
        size = p.get("size_variant", "")
        if preferred_size.lower() in size.lower():
            exact.append(p)
        else:
            others.append(p)

    return exact + others
