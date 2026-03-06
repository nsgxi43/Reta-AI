# services/recommendation_engine.py

from typing import List, Dict


class RecommendationEngine:

    def select(self, products: List[Dict], parsed: Dict) -> Dict:

        if not products:
            return {
                "primary": None,
                "alternates": [],
                "reason": "no_products_found"
            }

        # 1️⃣ Primary Selection Logic
        primary = self._select_primary(products)

        # 2️⃣ Alternate Selection Logic
        alternates = self._select_alternates(products, primary)

        return {
            "primary": primary,
            "alternates": alternates,
            "reason": "standard_selection"
        }

    # -----------------------------------------

    def _select_primary(self, products):

        # Products are already filtered + size ranked
        # So first item is strongest candidate
        return products[0]

    # -----------------------------------------

    def _select_alternates(self, products, primary):

        alternates = []

        primary_brand = primary.get("brand", "").lower()

        for p in products[1:]:

            # Avoid duplicate same size only variation
            if p.get("product_name") == primary.get("product_name"):
                continue

            # Prefer different brand alternatives
            if p.get("brand", "").lower() != primary_brand:
                alternates.append(p)

        # If no cross-brand alternates found,
        # fallback to different size variants
        if not alternates:
            alternates = products[1:4]

        return alternates[:3]
