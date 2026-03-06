SYSTEM_PROMPT = """
You are Reta AI, an in-store retail assistant.

Rules:
- Do not greet the user.
- Use only the provided product information.
- Do not invent or assume details.
- Always mention the colour zone.
- Keep the response concise and easy to read.

Response style:
- Write in a natural, flowing paragraph.
- Guide the customer as if helping them inside a store.
- Mention alternates naturally at the end.




"""


def build_prompt(user_query, products):
    if not products:
        return f"""
Customer query:
{user_query}

No matching products were found in the database.
"""

    # Authoritative product
    best = products[0]

    product_lines = []
    for p in products:
        product_lines.append(
            f"- {p['product_name']} | "
            f"Category: {p['product_category']} | "
            f"Size: {p.get('size_variant', 'N/A')} | "
            f"Colour Zone: {p['assigned_color']}"
        )

    product_block = "\n".join(product_lines)

    prompt = f"""
Customer query:
{user_query}

Recommended product (authoritative):
Name: {best['product_name']}
Category: {best['product_category']}
Size: {best.get('size_variant', 'N/A')}
Colour Zone: {best['assigned_color']}

Other available products:
{product_block}

Instructions:
Write a short, clear response in paragraph form.

You must:
- Recommend the best product.
- Explain briefly why it matches the need.
- Clearly state the colour zone.
- Mention 1–2 alternate options if available.

Do not use headings or bullet points.
Do not greet the user.

"""

    return prompt

