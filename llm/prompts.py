SYSTEM_PROMPT = """
You are Reta AI, a retail assistant.
You must only use the provided product information.
Do not invent products.
Do not mention anything outside the given data.
Always mention the colour zone.
Be concise and helpful.
"""

def build_prompt(user_query, products):
    product_lines = []

    for i, p in enumerate(products, 1):
        product_lines.append(
            f"{i}. {p['product_name']} "
            f"({p['product_category']}, {p['assigned_color']} zone)"
        )

    product_block = "\n".join(product_lines)

    prompt = f"""
User query:
{user_query}

Available products:
{product_block}

Task:
- Recommend the best matching product
- Suggest alternates if relevant
- Mention the colour zone
- Keep the response clear and user-friendly
"""

    return prompt
