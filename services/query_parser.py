from llm.client import generate_response
import json

PARSER_SYSTEM_PROMPT = """
You are a structured retail query parser.

Return ONLY valid JSON.
Do not add explanations.
Do not add markdown.

Schema:
{
  "intent": "recommendation | info | comparison | conversational",
  "category": string or null,
  "exclude_brands": [],
  "preferred_size": string or null,
  "budget_preference": "low | high | null",
  "comparison": true or false,
  "conversation_type": "product_query | small_talk",
  "compare_entities": []
}

Rules:
- Extract brand names into exclude_brands if user says "not X".
- If user wants comparison, set comparison=true and extract product/brand names into compare_entities.
- If greeting/thank you/abusive language, set intent="conversational".
- If asking product availability or details → intent="info".
- If asking recommendation → intent="recommendation".
"""



def parse_query(user_query: str) -> dict:
    prompt = f"""
User message:
{user_query}

Extract structured JSON:
"""

    response = generate_response(
        system_prompt=PARSER_SYSTEM_PROMPT,
        user_prompt=prompt,
        temperature=0.1
    )

    response = response.strip()

    if response.startswith("```"):
        response = response.replace("```json", "").replace("```", "").strip()


    try:
        parsed = json.loads(response)
        return parsed
    except Exception:
        # fallback safe default
        return {
            "intent": "recommendation",
            "category": None,
            "exclude_brands": [],
            "preferred_size": None,
            "budget_preference": None,
            "comparison": False,
            "conversation_type": "product_query"
        }

