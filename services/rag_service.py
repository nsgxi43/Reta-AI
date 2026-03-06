from services.query_parser import parse_query
from services.constraint_engine import StructuredConstraintEngine
from services.recommendation_engine import RecommendationEngine
from services.renderer import (
    render_response,
    render_unavailable_response,
    render_comparison_response,
)
from vectorstore.search import VectorSearch


class RAGService:

    def __init__(self):
        self.searcher = VectorSearch()
        self.constraints = StructuredConstraintEngine()
        self.recommender = RecommendationEngine()

    @staticmethod
    def _entity_matches(entity: str, product: dict) -> bool:
        """Check if ALL words of an entity appear in the product name or brand."""
        words = entity.lower().split()
        searchable = (product["product_name"] + " " + product["brand"]).lower()
        return all(word in searchable for word in words)

    def query(self, user_query: str):

        parsed = parse_query(user_query)

        # ---------------------------
        # 1️⃣ Small Talk
        # ---------------------------
        if parsed["intent"] == "conversational":
            return {
                "parsed": parsed,
                "primary": None,
                "alternates": [],
                "response": "I'm here to help! Let me know what product you're looking for.",
            }

        all_products = self.searcher.get_all_products()

        # ---------------------------
        # 2️⃣ Exact Product Match
        # ---------------------------
        exact_match = next(
            (
                p
                for p in all_products
                if user_query.lower() in p["product_name"].lower()
            ),
            None,
        )

        if exact_match:
            response = render_response(
                user_query=user_query,
                primary=exact_match,
                alternates=[],
            )
            return {
                "parsed": parsed,
                "primary": exact_match,
                "alternates": [],
                "response": response,
            }

        # ---------------------------
        # 3️⃣ Comparison Logic
        # ---------------------------
        if parsed["intent"] == "comparison":

            entities = parsed.get("compare_entities", [])

            # Detect common category
            category_candidates = [
                p["product_category"]
                for p in all_products
                if any(
                    self._entity_matches(entity, p)
                    for entity in entities
                )
            ]

            target_category = category_candidates[0] if category_candidates else None

            raw_matches = [
                p
                for p in all_products
                if any(
                    self._entity_matches(entity, p)
                    for entity in entities
                )
                and (
                    target_category is None
                    or p["product_category"] == target_category
                )
            ]

            # Deduplicate by product family (remove size)
            unique = {}
            for p in raw_matches:
                base_name = (
                    p["product_name"]
                    .replace(p.get("size_variant", ""), "")
                    .strip()
                )
                if base_name not in unique:
                    unique[base_name] = p

            comparison_products = list(unique.values())[:5]

            structured_products = [
                {
                    "name": p["product_name"],
                    "brand": p["brand"],
                    "size": p.get("size_variant"),
                    "description": p.get("short_description"),
                    "zone": p.get("assigned_color"),
                }
                for p in comparison_products
            ]

            response = render_comparison_response(
                user_query=user_query,
                products=structured_products,
            )

            return {
                "parsed": parsed,
                "primary": None,
                "alternates": comparison_products,
                "response": response,
            }

        # ---------------------------
        # 4️⃣ Retrieval
        # ---------------------------
        products = self.searcher.search(user_query, top_k=25)
        products = self.constraints.apply(products, parsed)

        # ---------------------------
        # 5️⃣ Not Found Fallback
        # ---------------------------
        if not products:

            if parsed.get("category"):
                alternates = [
                    p
                    for p in all_products
                    if parsed["category"].lower()
                    in p["product_category"].lower()
                ][:5]
            else:
                alternates = self.searcher.search(user_query, top_k=5)

            response = render_unavailable_response(
                user_query=user_query,
                alternates=alternates,
            )

            return {
                "parsed": parsed,
                "primary": None,
                "alternates": alternates,
                "response": response,
            }

        # ---------------------------
        # 6️⃣ Recommendation Selection
        # ---------------------------
        selection = self.recommender.select(products, parsed)

        response = render_response(
            user_query=user_query,
            primary=selection["primary"],
            alternates=selection["alternates"],
        )

        return {
            "parsed": parsed,
            "primary": selection["primary"],
            "alternates": selection["alternates"],
            "response": response,
        }
