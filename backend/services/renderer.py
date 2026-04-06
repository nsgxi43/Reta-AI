import re
from llm.client import generate_response

def _clean_markdown(text: str) -> str:
    """Strip all markdown formatting to return plain text."""
    # Remove **bold**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove *italic*
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove ###headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove bullet points and dashes
    text = re.sub(r'^\s*[-•*]\s+', '', text, flags=re.MULTILINE)
    # Clean extra whitespace
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.strip()
    return text


# Voice mode: one-sentence crisp response for TTS
VOICE_SYSTEM_PROMPT = (
    "You are a retail assistant. Reply in ONE sentence only. "
    "Format: Product name, price in rupees, color zone. "
    "Example: Sensodyne Rapid Relief 150g, 145 rupees, Blue zone. "
    "No filler words. No markdown. Maximum 20 words."
)

# Text mode: friendly 2-3 sentence response
TEXT_SYSTEM_PROMPT = (
    "You are a friendly in-store retail assistant. "
    "Write 2-3 plain sentences. Never use markdown (**bold**, *italic*, bullets, dashes). "
    "Mention: product name, price, zone location, one helpful tip."
)

def render_response(user_query, primary, alternates, zone=None, voice_mode=False):
    """
    Render natural language response with product details.
    
    Fields passed to Gemini:
    product_name, brand, product_line, size_variant, price_inr,
    short_description, assigned_color (→ "Blue zone"), 
    alternate_product_ids (resolved names)
    """
    
    if not primary:
        return "Sorry, I couldn't find that product. Try asking differently?"

    alt_names = ", ".join([p["product_name"] for p in alternates]) if alternates else "None"
    zone_hint = zone or primary.get("assigned_color", "Unknown")

    system_prompt = VOICE_SYSTEM_PROMPT if voice_mode else TEXT_SYSTEM_PROMPT

    user_prompt = f"""
Customer Query:
{user_query}

Primary Product:
Name: {primary["product_name"]}
Brand: {primary["brand"]}
Product Line: {primary.get("product_line", "N/A")}
Size: {primary.get("size_variant", "N/A")}
Price: ₹{primary.get("price_inr", "N/A")}
Category: {primary["product_category"]}
Description: {primary.get("short_description", "N/A")}
Colour Zone: {zone_hint}

Alternate Products:
{alt_names}

Respond in a natural, human-friendly way.
Clearly mention the colour zone and location hint.
Be concise and actionable.
"""

    response_raw = generate_response(system_prompt, user_prompt)
    # Strip any markdown that slipped through
    response_clean = _clean_markdown(response_raw)
    return response_clean


def render_unavailable_response(user_query, alternates, zone=None):
    """Render response when primary product not found."""
    
    if not alternates:
        return "Sorry, I couldn't find that product. Try asking differently?"
    
    alt_list = "\n".join(
        [f"- {p['product_name']} (₹{p.get('price_inr', 'N/A')}, {p.get('assigned_color', 'Unknown')} zone)" 
         for p in alternates]
    )

    response = f"""The exact product isn't available right now, but here are some great alternatives:

{alt_list}
"""
    return _clean_markdown(response)


def render_comparison_response(user_query, products):
    """Render comparison response - one representative product per brand/type."""
    
    if not products:
        return "No products found to compare."
    
    # Deduplicate by product_line (group same product variants, keep cheapest/best)
    by_product_line = {}
    for p in products:
        product_line = p.get('product_line', p.get('product_name', 'Unknown'))
        if product_line not in by_product_line:
            by_product_line[product_line] = p
        else:
            # Keep the bigger size variant (better value)
            try:
                existing_size = float(by_product_line[product_line].get('size_variant', '0').replace('L', '').replace('ml', ''))
                new_size = float(p.get('size_variant', '0').replace('L', '').replace('ml', ''))
                if new_size > existing_size:
                    by_product_line[product_line] = p
            except:
                pass
    
    # Group by brand
    by_brand = {}
    for product_line, p in by_product_line.items():
        brand = p.get('brand', 'Unknown')
        if brand not in by_brand:
            by_brand[brand] = []
        by_brand[brand].append(p)
    
    # Build clean comparison (no markdown)
    lines = []
    lines.append("PRODUCT COMPARISON")
    lines.append("=" * 50)
    
    for brand, brand_products in by_brand.items():
        lines.append(f"\n{brand}:")
        for p in brand_products[:1]:  # Only one per brand  
            price = p.get('price_inr', 'N/A')
            size = p.get('size_variant', 'N/A')
            desc = p.get('short_description', '')
            zone = p.get('assigned_color', 'Unknown')
            name = p.get('product_name', 'N/A')
            
            # Calculate price per liter
            price_per_unit = ""
            if price != 'N/A' and isinstance(price, (int, float)) and size and 'L' in str(size):
                try:
                    liters = float(str(size).replace('L', ''))
                    price_per_unit = f" - Rs {price/liters:.0f}/L"
                except:
                    pass
            
            lines.append(f"  {name}")
            lines.append(f"  Price: Rs {price}{price_per_unit}")
            if size != 'N/A':
                lines.append(f"  Size: {size}")
            lines.append(f"  Location: {zone} zone")
            if desc:
                lines.append(f"  Details: {desc}")
    
    lines.append("\n" + "=" * 50)
    lines.append("RECOMMENDATION")
    
    # Generate insight
    product_summary = "\n".join([f"- {p.get('product_name')}: Rs{p.get('price_inr')} ({p.get('size_variant')})"
                                  for p in list(by_product_line.values())[:4]])
    
    prompt = f"""User asked: {user_query}

Compare these products:
{product_summary}

Provide ONE short sentence (under 15 words) on which is better value. No bullet points or markdown."""
    
    insight = generate_response(
        system_prompt="You are a helpful retail assistant. Be direct and concise.",
        user_prompt=prompt,
        temperature=0.2
    ).strip()
    
    lines.append(insight)
    
    return "\n".join(lines)


def render_listing_response(products, category_name: str = "products"):
    """Render list of products for listing queries."""
    if not products:
        return f"Sorry, no {category_name} found in stock right now."
    
    lines = []
    lines.append(f"Available {category_name} ({len(products)} varieties):\n")
    
    # Group by brand for better readability
    by_brand = {}
    for p in products:
        brand = p.get("brand", "Unknown")
        if brand not in by_brand:
            by_brand[brand] = []
        by_brand[brand].append(p)
    
    # Format listings
    for brand, brand_prods in sorted(by_brand.items()):
        lines.append(f"{brand}:")
        for p in brand_prods[:3]:  # Max 3 per brand to avoid clutter
            name = p.get("product_name", "N/A")
            price = p.get("price_inr", "N/A")
            zone = p.get("assigned_color", "Unknown")
            lines.append(f"  • {name} - Rs {price} ({zone} zone)")
        if len(brand_prods) > 3:
            lines.append(f"  ... and {len(brand_prods) - 3} more variants")
        lines.append("")  # Space between brands
    
    return "\n".join(lines)

