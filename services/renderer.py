from llm.client import generate_response


def render_response(user_query, primary, alternates):

    if not primary:
        return "Sorry, no suitable product found."

    alt_names = ", ".join([p["product_name"] for p in alternates]) if alternates else "None"

    system_prompt = "You are a professional retail assistant. Keep response concise. No markdown tables. Use bullet points only. Maximum 200 words."

    user_prompt = f"""
Customer Query:
{user_query}

Primary Product:
Name: {primary["product_name"]}
Category: {primary["product_category"]}
Size: {primary.get("size_variant")}
Colour Zone: {primary["assigned_color"]}
Description: {primary.get("short_description")}

Alternate Products:
{alt_names}

Respond in a natural, human-friendly way.
Mention colour zone.
Be clear and concise.
"""

    return generate_response(system_prompt, user_prompt)


def render_unavailable_response(user_query, alternates):

    alt_list = "\n".join(
        [f"- {p['product_name']} ({p['assigned_color']} zone)" for p in alternates]
    )

    return f"""
The requested product is not available.

However, you may consider the following alternatives:

{alt_list}
"""


def render_comparison_response(user_query, products):

    product_blocks = []

    for p in products:
        product_blocks.append(
            f"""
Product Name: {p['name']}
Brand: {p['brand']}
Size: {p['size']}
Description: {p['description']}
Colour Zone: {p['zone']}
"""
        )

    product_text = "\n".join(product_blocks)

    prompt = f"""
User Query:
{user_query}

Compare the following products clearly and professionally.

{product_text}

Provide:
1. Key Differences
2. Similarities
3. Recommendation based on typical usage

Keep response concise. No markdown tables. Use bullet points only. Maximum 200 words.
"""

    return generate_response(
        system_prompt="You are a retail comparison assistant.",
        user_prompt=prompt
    )

