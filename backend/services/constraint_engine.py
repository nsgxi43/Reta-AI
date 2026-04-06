# services/constraint_engine.py
"""
Constraint engine applies retail filters in priority order:
1. stock_available == True (hard gate)
2. category (exact match if parsed)
3. brand (exact match; relax if no results)
4. price_inr <= budget_max
5. price_tier (if no numeric budget)
6. size_variant (if parsed)
7. seasonal (only if True in intent)
8. source (if parsed)
9. free_text (match keywords in product descriptions/lines)
10. exclude_brands (drop from candidates)
"""
from typing import List, Dict


class StructuredConstraintEngine:

    def apply(self, products: List[Dict], parsed: Dict) -> List[Dict]:
        """Apply filters in priority order."""
        
        # 1️⃣ Hard gate: stock_available must be True
        products = [p for p in products if p.get("stock_available", False) is True]
        
        if not products:
            return []
        
        # 2️⃣ Category: exact match if parsed
        if parsed.get("category"):
            filtered = [
                p for p in products
                if p.get("product_category", "").lower() == parsed["category"].lower()
            ]
            if filtered:
                products = filtered
        
        # 3️⃣ Brand: For comparison mode, keep all comparison brands; otherwise single brand match
        if parsed.get("comparison") and parsed.get("comparison_brands"):
            # In comparison mode, include ALL brands mentioned
            comparison_brands_lower = {b.lower() for b in parsed["comparison_brands"]}
            filtered = [
                p for p in products
                if p.get("brand", "").lower() in comparison_brands_lower
            ]
            if filtered:
                products = filtered
        elif parsed.get("brand"):
            # Non-comparison: exact match for single brand; relax if no results
            filtered = [
                p for p in products
                if p.get("brand", "").lower() == parsed["brand"].lower()
            ]
            if filtered:
                products = filtered
            # If brand filter removes all, keep products and apply other constraints
        
        # 4️⃣ Price: numeric budget constraint
        if parsed.get("budget_max"):
            products = [
                p for p in products
                if p.get("price_inr") and p["price_inr"] <= parsed["budget_max"]
            ]
        
        # 5️⃣ Price tier: match if no numeric budget
        if not parsed.get("budget_max") and parsed.get("price_tier"):
            products = [
                p for p in products
                if p.get("price_tier", "").lower() == parsed["price_tier"].lower()
            ]
        
        # 6️⃣ Size variant: if parsed
        if parsed.get("size_variant"):
            products = [
                p for p in products
                if p.get("size_variant", "").lower() == parsed["size_variant"].lower()
            ]
        
        # 7️⃣ Seasonal: only filter if True in intent
        if parsed.get("seasonal") is True:
            products = [
                p for p in products
                if p.get("seasonal", False) is True
            ]
        
        # 8️⃣ Source: if parsed (Online/Store/Any)
        if parsed.get("source"):
            products = [
                p for p in products
                if p.get("source", "").lower() == parsed["source"].lower()
            ]
        
        # 9️⃣ Free text: match keywords in product descriptions, product_line, short_description
        if parsed.get("free_text"):
            free_text_lower = parsed["free_text"].lower()
            # Extract keywords (words longer than 3 chars, excluding common words)
            keywords = [w for w in free_text_lower.split() if len(w) > 3 and w not in ["for", "with", "from", "that", "this", "toothpaste", "shampoo", "soap"]]
            
            if keywords:
                matched = []
                for p in products:
                    product_line = (p.get("product_line", "") or "").lower()
                    short_desc = (p.get("short_description", "") or "").lower()
                    long_desc = (p.get("long_description", "") or "").lower()
                    product_name = (p.get("product_name", "") or "").lower()
                    
                    combined_text = f"{product_line} {short_desc} {long_desc} {product_name}"
                    
                    # Check if any keyword matches
                    if any(keyword in combined_text for keyword in keywords):
                        matched.append(p)
                
                # Only filter if we found matches, otherwise keep original products
                if matched:
                    products = matched
        
        # 🔟 Exclude brands: drop from candidates
        if parsed.get("exclude_brands"):
            exclude_set = {b.lower() for b in parsed["exclude_brands"]}
            products = [
                p for p in products
                if p.get("brand", "").lower() not in exclude_set
            ]
        
        # 1️⃣1️⃣ Price ordering: sort by price if requested
        if parsed.get("price_ordering"):
            if parsed["price_ordering"] == "min":
                products.sort(key=lambda p: p.get("price_inr", 999999))
            elif parsed["price_ordering"] == "max":
                products.sort(key=lambda p: p.get("price_inr", 0), reverse=True)
        
        return products

    # ----------------------------------

    def _filter_category(self, products, category):
        if not category:
            return products

        return [
            p for p in products
            if category.lower() in p.get("product_category", "").lower()
        ]

    # ----------------------------------

    def _apply_budget_preference(self, products, budget):
        if not budget:
            return products

        # If you have price column in dataset
        if "price" not in products[0]:
            return products

        if budget == "low":
            return sorted(products, key=lambda x: x.get("price", 9999))

        if budget == "high":
            return sorted(products, key=lambda x: -x.get("price", 0))

        return products

    # ----------------------------------

    def _apply_size_preference(self, products, preferred_size):
        if not preferred_size:
            return products

        preferred = []
        others = []

        for p in products:
            size = p.get("size_variant", "")
            if preferred_size.lower() in size.lower():
                preferred.append(p)
            else:
                others.append(p)

        return preferred + others
