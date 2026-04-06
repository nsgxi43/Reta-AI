import re
from services.query_parser import parse_query
from services.constraint_engine import StructuredConstraintEngine
from services.recommendation_engine import RecommendationEngine
from services.renderer import (
    render_response,
    render_unavailable_response,
    render_comparison_response,
    render_listing_response,
)
from vectorstore.search import VectorSearch
from data.load_data import load_products

# ═════════════════════════════════════════════════════════════════════╗
# HELPERS FOR CATEGORY & INTENT HANDLING
# ═════════════════════════════════════════════════════════════════════╝

def _fuzzy_match_category(user_category: str, all_products) -> str:
    """Map user category (e.g. 'oil') to actual database category (e.g. 'Oil')."""
    if not user_category:
        return None
    
    user_cat_lower = user_category.lower().strip()
    
    # Get unique categories from database
    unique_categories = set(
        p.get("product_category", "")
        for p in all_products if p.get("product_category")
    )
    
    # Exact match (case-insensitive)
    for cat in unique_categories:
        if cat.lower() == user_cat_lower:
            return cat
    
    # Substring match
    for cat in unique_categories:
        if user_cat_lower in cat.lower() or cat.lower() in user_cat_lower:
            return cat
    
    return None

# Chitchat patterns (bypasses RAG entirely)
CHITCHAT_PATTERNS = [
    (r"^(hey|hi|hello|heyy+|yo)\b", "greeting"),
    (r"^thank(s| you)", "thanks"),
    (r"^(bye|goodbye|see you|cya)\b", "bye"),
    (r"^(ok|okay|sure|alright|cool|nice|great|awesome)$", "ok"),
    (r"^(how are you|what's up|who are you|what can you do)", "whatsup"),
    (r"^(help|what do you do|yes|no)$", "help"),
    # Follow-up confirmations that are clearly chitchat
    (r"can you hear me", "greeting"),
    (r"are you there", "greeting"),
    (r"can you understand", "greeting"),
    (r"do you understand", "greeting"),
]

CHITCHAT_RESPONSES = {
    "greeting": "Hey! How can I help you find something today?",
    "thanks": "Happy to help! Need anything else?",
    "bye": "Thanks for shopping! See you soon.",
    "ok": "Great! Just ask me about any product.",
    "whatsup": "I'm your in-store assistant. Ask me about any product, and I'll find it for you!",
    "help": "Just ask me about any product — I'll find it, tell you the price, and show you where it is.",
}

def _classify_chitchat(query: str) -> str | None:
    """Detect simple social messages that skip vector search.
    
    Only match if:
    1. Pattern matches
    2. No product keywords present
    3. Message is short (≤6 words) OR matches specific confirmation patterns
    """
    q = query.strip().lower()
    
    # Product keywords that indicate intent (not pure chitchat)
    PRODUCT_KEYWORDS = {
        'toothpaste', 'shampoo', 'soap', 'moisturizer', 'cream', 'oil',
        'product', 'brand', 'price', 'cost', 'find', 'search', 'get',
        'buy', 'shop', 'need', 'want', 'look', 'recommend', 'suggest',
        'best', 'good', 'cheap', 'expensive', 'under', 'rupees', 'rs',
    }
    
    # If message contains product keywords, skip chitchat (product intent)
    words = q.split()
    if any(word in PRODUCT_KEYWORDS for word in words):
        return None
    
    # Check patterns - some are allowed to be longer (>4 words)
    for pattern, response_type in CHITCHAT_PATTERNS:
        if re.search(pattern, q):  # Use search() instead of match() to find anywhere
            # "can you hear me" type patterns are allowed to be longer
            if any(p in q for p in ["can you hear", "are you there", "can you understand", "do you understand"]):
                return response_type
            # Standard greetings limited to short messages
            if len(words) <= 6:
                return response_type
    
    return None


class RAGService:

    def __init__(self):
        self.searcher = VectorSearch()
        self.constraints = StructuredConstraintEngine()
        
        # Load products dataframe for recommendation engine (alternate resolution)
        df = load_products()
        self.recommender = RecommendationEngine(products_df=df)

    def query(self, user_query: str, voice_mode: bool = False):
        """
        End-to-end RAG pipeline:
        1. Check for chitchat (bypass vector search for simple messages)
        2. Check for listing queries (what products do you have in X)
        3. Check for EXACT PRODUCT MATCH (user asking for specific product)
        4. Check for navigation (where is X)
        5. Parse intent/constraints from user query
        6. Retrieve candidate products via FAISS
        7. Apply constraint filters
        8. Select primary + alternates
        9. Render natural language response
        """
        
        # --- 1️⃣ CHITCHAT GATE: Skip vector search for social messages ---
        chitchat_type = _classify_chitchat(user_query)
        if chitchat_type:
            return {
                "parsed": {},
                "primary": None,
                "alternates": [],
                "response": CHITCHAT_RESPONSES[chitchat_type],
                "chitchat": True,
                "request_feedback": chitchat_type in ["bye", "thanks"],
            }
        
        # --- 2️⃣ LISTING DETECTION ---
        query_lower = user_query.lower()
        is_listing = (
            any(phrase in query_lower for phrase in ["what products", "show me all", "list", "what brands"]) or
            ("what" in query_lower and "do you have" in query_lower) or
            ("what" in query_lower and "available" in query_lower)
        )
        if is_listing:
            listing_response = self._handle_listing_query(user_query)
            if listing_response:
                return listing_response
        
        # --- 3️⃣ EXACT PRODUCT MATCH CHECK ---
        # Direct lookup for specific products by name
        all_products = self.searcher.get_all_products()
        exact_match = self._find_exact_product_match(user_query, all_products)
        if exact_match:
            response = render_response(
                user_query=user_query,
                primary=exact_match,
                alternates=[],
                zone=exact_match.get("assigned_color"),
                voice_mode=voice_mode
            )
            return {
                "parsed": {},
                "primary": exact_match,
                "alternates": [],
                "response": response,
                "chitchat": False,
                "request_feedback": False,
            }
        
        # --- 4️⃣ NAVIGATION DETECTION ---
        if "where" in query_lower and any(x in query_lower for x in ["toothpaste", "oil", "soap", "shampoo", "product", "find", "zone"]):
            nav_response = self._handle_navigation_query(user_query, all_products)
            if nav_response:
                return nav_response
        
        parsed = parse_query(user_query)

        # Retrieve candidates from vector search
        candidate_products = self.searcher.search(user_query, top_k=25)

        # Apply constraint filters (stock, category, brand, price, size, etc.)
        filtered_products = self.constraints.apply(candidate_products, parsed)

        # Handle no results
        if not filtered_products:
            all_products = self.searcher.get_all_products()
            
            # Try fallback: search without constraints, but prioritize category + free_text match
            alternates = []
            
            # Smart fallback: search for category + free_text keywords
            if parsed.get("category"):
                category_products = [
                    p for p in all_products
                    if p.get("product_category", "").lower() == parsed["category"].lower() 
                    and p.get("stock_available", False) is True
                ]
                
                # If user provided free_text, try to match those keywords
                if parsed.get("free_text") and category_products:
                    free_text_lower = parsed["free_text"].lower()
                    keywords = [w for w in free_text_lower.split() if len(w) > 3 and w not in ["for", "with", "from", "that", "this", "toothpaste", "shampoo", "soap"]]
                    
                    if keywords:
                        matched_by_desc = []
                        for p in category_products:
                            product_line = (p.get("product_line", "") or "").lower()
                            short_desc = (p.get("short_description", "") or "").lower()
                            product_name = (p.get("product_name", "") or "").lower()
                            combined_text = f"{product_line} {short_desc} {product_name}"
                            
                            if any(keyword in combined_text for keyword in keywords):
                                matched_by_desc.append(p)
                        
                        alternates = matched_by_desc[:5]
                
                # If no matches found by description, just show category products
                if not alternates:
                    alternates = category_products[:5]
            
            # Last resort: use vector search candidates
            if not alternates:
                alternates = candidate_products[:5]

            # ✅ EXACT MATCH PROMOTION: Check if exact product exists in alternatives
            # This handles cases where user searches for "Sensodyne Rapid Relief 25g" 
            # and that exact product exists but was filtered out by constraints
            exact_match = None
            if user_query and alternates:
                user_query_lower = user_query.lower().strip()
                for i, alt in enumerate(alternates):
                    prod_name_lower = (alt.get("product_name", "") or "").lower().strip()
                    # Check if product name matches query or query contains all key words of product
                    if prod_name_lower == user_query_lower or all(
                        word in user_query_lower for word in prod_name_lower.split()
                        if len(word) > 2
                    ):
                        exact_match = alt
                        # Remove from alternatives and use as primary
                        alternates.pop(i)
                        break
            
            # If exact match found, return it as primary
            if exact_match:
                response = render_response(
                    user_query=user_query,
                    primary=exact_match,
                    alternates=alternates,
                    zone=exact_match.get("assigned_color"),
                    voice_mode=voice_mode
                )
                return {
                    "parsed": parsed,
                    "primary": exact_match,
                    "alternates": alternates,
                    "zone": exact_match.get("assigned_color"),
                    "response": response,
                    "chitchat": False,
                    "request_feedback": False,
                }

            response = render_unavailable_response(
                user_query=user_query,
                alternates=alternates,
                zone=None
            )

            return {
                "parsed": parsed,
                "primary": None,
                "alternates": alternates,
                "response": response,
            }

        # Select primary + alternates via recommendation engine
        selection = self.recommender.select(filtered_products, parsed)

        # Render response based on comparison flag
        if parsed.get("comparison"):
            # For comparison, show products from all comparison_brands if available
            comparison_products = filtered_products
            
            # If we have limited results but multiple comparison brands, expand search
            if len(comparison_products) < 4 and parsed.get("comparison_brands"):
                all_products = self.searcher.get_all_products()
                
                # Helper: apply free_text filter
                def apply_free_text_filter(prods, free_text):
                    if not free_text:
                        return prods
                    free_text_lower = free_text.lower()
                    keywords = [w for w in free_text_lower.split() if len(w) > 3 and w not in ["for", "with", "from", "that", "this", "oil", "and"]]
                    if not keywords:
                        return prods
                    matched = []
                    for p in prods:
                        product_line = (p.get("product_line", "") or "").lower()
                        short_desc = (p.get("short_description", "") or "").lower()
                        product_name = (p.get("product_name", "") or "").lower()
                        combined_text = f"{product_line} {short_desc} {product_name}"
                        if any(keyword in combined_text for keyword in keywords):
                            matched.append(p)
                    return matched if matched else prods
                
                for brand in parsed.get("comparison_brands", []):
                    brand_products = [
                        p for p in all_products
                        if p.get("brand", "").lower() == brand.lower()
                        and p.get("stock_available", False)
                        and p not in comparison_products
                    ]
                    
                    # Apply free_text filter to brand results
                    brand_products = apply_free_text_filter(brand_products, parsed.get("free_text", ""))
                    
                    # Additional filter: if query mentions "refined" or "ghee" explicitly, filter for those
                    query_lower = user_query.lower()
                    if "refined" in query_lower:
                        brand_products = [
                            p for p in brand_products
                            if "refined" in (p.get("product_line", "") or "").lower() or
                               "refined" in (p.get("product_name", "") or "").lower()
                        ]
                    elif "ghee" in query_lower:
                        brand_products = [
                            p for p in brand_products
                            if "ghee" in (p.get("product_line", "") or "").lower() or
                               "ghee" in (p.get("product_name", "") or "").lower()
                        ]
                    
                    comparison_products.extend(brand_products[:3])
            
            if len(comparison_products) > 1:
                response = render_comparison_response(
                    user_query=user_query,
                    products=comparison_products[:6],
                )
                return {
                    "parsed": parsed,
                    "primary": None,
                    "alternates": comparison_products[:6],
                    "response": response,
                }
        else:
        # Validate that selected product matches user intent
            # (sanity check for voice mishearings)
            primary = selection["primary"]
            if primary and parsed.get("category"):
                primary_category = primary.get("product_category", "").lower()
                parsed_category = parsed.get("category", "").lower()
                # If categories don't match well, it might be a mishearing
                if primary_category != parsed_category:
                    # Ask for clarification instead of returning wrong product
                    response = (
                        f"I found a {primary_category.lower()}, but you asked for a {parsed_category.lower()}. "
                        f"Did you mean the {primary['product_name']}, or would you like me to search again?"
                    )
                    return {
                        "parsed": parsed,
                        "primary": None,  # Don't show product if mismatch
                        "alternates": [],
                        "response": response,
                        "chitchat": False,
                        "request_feedback": False,
                    }
            
            # Standard response for single product recommendation
            response = render_response(
                user_query=user_query,
                primary=selection["primary"],
                alternates=selection["alternates"],
                zone=selection.get("zone"),
                voice_mode=voice_mode
            )

            return {
                "parsed": parsed,
                "primary": selection["primary"],
                "alternates": selection["alternates"],
                "zone": selection.get("zone"),
                "response": response,
                "chitchat": False,
                "request_feedback": False,
            }
    
    def _handle_listing_query(self, user_query: str):
        """Handle 'what products do you have in X' type queries."""
        all_products = self.searcher.get_all_products()
        
        # Parse the category from query
        parsed = parse_query(user_query)
        
        # Try to extract category
        products_to_show = []
        category_name = "products"
        
        # 1. If we have a parsed category, use fuzzy matching
        if parsed.get("category"):
            fuzzy_cat = _fuzzy_match_category(parsed["category"], all_products)
            if fuzzy_cat:
                category_name = fuzzy_cat.lower()
                products_to_show = [
                    p for p in all_products
                    if p.get("product_category", "").lower() == fuzzy_cat.lower()
                    and p.get("stock_available", False)
                ]
        
        # 2. If no category matched, try free_text keywords
        if not products_to_show and parsed.get("free_text"):
            free_text_lower = parsed["free_text"].lower()
            keywords = [w for w in free_text_lower.split() if len(w) > 3]
            
            matched = []
            for p in all_products:
                if not p.get("stock_available", False):
                    continue
                product_line = (p.get("product_line", "") or "").lower()
                short_desc = (p.get("short_description", "") or "").lower()
                product_name = (p.get("product_name", "") or "").lower()
                combined_text = f"{product_line} {short_desc} {product_name}"
                
                if any(keyword in combined_text for keyword in keywords):
                    matched.append(p)
            products_to_show = matched
        
        # 3. If still nothing, try broader category search
        if not products_to_show:
            # Extract category terms from query
            category_keywords = ["oil", "shampoo", "toothpaste", "soap", "cream", "ghee", "butter", "detergent"]
            query_lower = user_query.lower()
            
            for keyword in category_keywords:
                if keyword in query_lower:
                    fuzzy_cat = _fuzzy_match_category(keyword, all_products)
                    if fuzzy_cat:
                        category_name = fuzzy_cat.lower()
                        products_to_show = [
                            p for p in all_products
                            if fuzzy_cat.lower() in p.get("product_category", "").lower()
                            and p.get("stock_available", False)
                        ]
                        break
        
        # 4. Handle price ordering if requested
        if products_to_show and parsed.get("price_ordering"):
            if parsed["price_ordering"] == "min":
                products_to_show.sort(key=lambda p: p.get("price_inr", 999999))[:10]
            elif parsed["price_ordering"] == "max":
                products_to_show.sort(key=lambda p: p.get("price_inr", 0), reverse=True)[:10]
        
        # Format response as a nice list
        if products_to_show:
            response = render_listing_response(products_to_show[:15], category_name)
            
            return {
                "parsed": parsed,
                "primary": None,
                "alternates": products_to_show[:15],
                "response": response,
                "chitchat": False,
                "request_feedback": False,
            }
        
        return None
    
    def _find_exact_product_match(self, user_query: str, all_products) -> dict:
        """Find exact product match by name in database."""
        query_lower = user_query.lower().strip()
        
        # Exact match on product_name
        for p in all_products:
            if p.get("stock_available", False):
                product_name = (p.get("product_name", "") or "").lower().strip()
                if product_name == query_lower:
                    return p
        
        # Fuzzy match: check if all significant words in query are in product name
        query_words = [w for w in query_lower.split() if len(w) > 2]
        for p in all_products:
            if p.get("stock_available", False):
                product_name = (p.get("product_name", "") or "").lower()
                # Check if all query words are in product name
                if all(word in product_name for word in query_words) and len(query_words) >= 2:
                    return p
        
        return None
    
    def _handle_navigation_query(self, user_query: str, all_products):
        """Handle 'Where is X?' location/navigation queries."""
        # Try to extract product category from query
        query_lower = user_query.lower()
        category_keywords = {
            "toothpaste": "Toothpaste",
            "oil": "Oil",
            "soap": "Soap",
            "shampoo": "Shampoo",
            "cream": "Cream",
            "ghee": "Ghee"
        }
        
        found_category = None
        for keyword, category in category_keywords.items():
            if keyword in query_lower:
                found_category = category
                break
        
        if found_category:
            # Get first available product of that category
            for p in all_products:
                if (p.get("product_category") == found_category and 
                    p.get("stock_available", False)):
                    zone = p.get("assigned_color", "Unknown")
                    response = f"You can find {found_category.lower()} in the {zone} zone. For example, we have {p.get('product_name')} for ₹{p.get('price_inr')}."
                    
                    return {
                        "parsed": {},
                        "primary": p,
                        "alternates": [],
                        "response": response,
                        "chitchat": False,
                        "request_feedback": False,
                    }
        
        return None
