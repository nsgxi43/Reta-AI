# services/constraint_engine.py

from typing import List, Dict


class StructuredConstraintEngine:

    def apply(self, products: List[Dict], parsed: Dict) -> List[Dict]:

        products = self._exclude_brands(products, parsed.get("exclude_brands"))
        products = self._filter_category(products, parsed.get("category"))
        products = self._apply_budget_preference(products, parsed.get("budget_preference"))
        products = self._apply_size_preference(products, parsed.get("preferred_size"))

        return products

    # ----------------------------------

    def _exclude_brands(self, products, exclude_brands):
        if not exclude_brands:
            return products

        return [
            p for p in products
            if not any(
                brand.lower() in p.get("product_name", "").lower()
                for brand in exclude_brands
            )
        ]

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
