import os
from google import genai

_api_key = os.getenv("GOOGLE_API_KEY")
if not _api_key:
    raise RuntimeError("GOOGLE_API_KEY is not set")

client = genai.Client(api_key=_api_key)

MODEL_NAME = "models/gemini-2.5-flash"


def generate_response(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        config={
            "temperature": 0.2,
            "top_p": 0.9,
            "max_output_tokens": 400,
        }
    )

    # ✅ Properly extract ALL text parts
    output = []
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, "text"):
                output.append(part.text)

    return "".join(output).strip()
