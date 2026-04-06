from llm.client import generate_response
import json

PARSER_SYSTEM_PROMPT = """
You are a structured retail query parser.

Return ONLY valid JSON (no markdown, no explanations, no backticks).

Extract user intent into this schema:
{
  "category": "Product category (e.g. Shampoo, Toothpaste) or null",
  "brand": "Brand name (e.g. Dove, Colgate) or null",
  "comparison_brands": ["List of brands mentioned for comparison"],
  "product_line": "Product line/variant name or null",
  "size_variant": "Size (e.g. 180ml, 25g, 500ml) or null",
  "unit_type": "Unit type (ml, g, pieces, etc) or null",
  "budget_max": "Max price in INR (numeric) or null",
  "price_tier": "Budget/Standard/Premium/Luxury or null",
  "price_ordering": "min/max or null (cheapest/most expensive)",
  "listing": "true/false (user wants to see list of products)",
  "seasonal": "true/false or null",
  "source": "Online/Store/Any or null",
  "comparison": "true/false (is user asking for product comparison)",
  "exclude_brands": ["list of brands to exclude"],
  "free_text": "Any unstructured requirement (e.g. for dry hair, for sensitive teeth)"
}

Rules:
- Set listing=true if user asks "What X do you have", "Show me all X", "List X", "Available X"
- When user asks "cheapest" or "lowest price": set price_ordering="min"
- When user asks "most expensive" or "highest price": set price_ordering="max"  
- When user asks to COMPARE: set comparison=true and extract both brands
- Extract brand names into exclude_brands if user says "not X"
- Extract budget as numeric max price if mentioned
- Extract descriptive requirements into free_text (e.g. "for sensitivity", "whitening")
- Preserve null for any field not mentioned
"""


def parse_query(user_query: str) -> dict:
    """Parse user query into structured intent schema."""
    prompt = f"""
User message:
{user_query}

Extract structured JSON (no markdown, no backticks, just raw JSON):
"""

    response = generate_response(
        system_prompt=PARSER_SYSTEM_PROMPT,
        user_prompt=prompt,
        temperature=0.1
    )

    response = response.strip()
    
    # Remove markdown if present
    if response.startswith("```"):
        response = response.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(response)
        return parsed
    except Exception as e:
        print(f"Parser error: {e}. Raw response: {response}")
        # Safe fallback
        return {
            "category": None,
            "brand": None,
            "comparison_brands": [],
            "product_line": None,
            "size_variant": None,
            "unit_type": None,
            "budget_max": None,
            "price_tier": None,
            "price_ordering": None,
            "listing": False,
            "seasonal": None,
            "source": None,
            "comparison": False,
            "exclude_brands": [],
            "free_text": user_query
        }


