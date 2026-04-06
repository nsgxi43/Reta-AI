# services/recommendation_engine.py
"""
Recommendation engine selects primary and alternates:
- Primary: highest validation-passing product (ranked by FAISS score)
- Alternates: resolved from alternate_product_ids column (pre-computed in dataset)
- Zone: assigned_color is included in response as in-store zone hint
"""
from typing import List, Dict


class RecommendationEngine:

    def __init__(self, products_df=None):
        """
        Initialize with optional products dataframe for alternate resolution.
        If provided, enables looking up alternate_product_ids.
        """
        self.products_df = products_df
        self.products_by_id = {}
        if products_df is not None:
            # Build lookup map for alternate resolution
            for _, row in products_df.iterrows():
                self.products_by_id[row.get("product_id")] = row.to_dict()

    def select(self, products: List[Dict], parsed: Dict, scores: List[float] = None) -> Dict:
        """
        Select primary and alternates.
        
        Args:
            products: candidate dicts (already filtered by constraints)
            parsed: parsed intent
            scores: optional FAISS scores corresponding to products
        
        Returns:
            {
                "primary": primary product dict,
                "alternates": [list of alternate product dicts],
                "zone": assigned_color as zone hint
            }
        """
        
        if not products:
            return {
                "primary": None,
                "alternates": [],
                "zone": None,
                "reason": "no_products_found"
            }

        # 1️⃣ Primary: first product is highest-scoring from constraints
        # (all candidates are already stock_available=True from constraint engine)
        primary = products[0]
        
        # Sanity check: if primary is somehow out of stock, find first available
        if not primary.get("stock_available", False):
            available = [p for p in products if p.get("stock_available", False)]
            if available:
                primary = available[0]
            else:
                return {
                    "primary": None,
                    "alternates": [],
                    "zone": None,
                    "reason": "all_out_of_stock"
                }
        
        # 2️⃣ Alternates: resolve from alternate_product_ids if available
        alternates = []
        alt_ids_str = primary.get("alternate_product_ids", "")
        if alt_ids_str and self.products_by_id:
            # Parse comma-separated IDs or JSON list
            try:
                import json
                alt_ids = json.loads(alt_ids_str)
                if isinstance(alt_ids, str):
                    alt_ids = [x.strip() for x in alt_ids.split(",")]
            except:
                alt_ids = [x.strip() for x in str(alt_ids_str).split(",")]
            
            for alt_id in alt_ids[:3]:  # limit to 3 alternates
                product = self.products_by_id.get(alt_id)
                # Only include if it's available AND different product name
                if (product and 
                    product.get("stock_available", False) and
                    product.get("product_name") != primary.get("product_name")):
                    alternates.append(product)
        
        # 3️⃣ Zone hint from assigned_color
        zone = primary.get("assigned_color", "Unknown")
        
        return {
            "primary": primary,
            "alternates": alternates,
            "zone": zone,
            "reason": "standard_selection"
        }

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
