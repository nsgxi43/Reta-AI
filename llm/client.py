import os
from google import genai

_api_key = os.environ.get("GEMINI_API_KEY")
if not _api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set")

client = genai.Client(api_key=_api_key)

MODEL_NAME = "models/gemini-2.5-flash-lite"


def generate_response(system_prompt: str, user_prompt: str, temperature=0.3):
    combined_prompt = f"{system_prompt}\n\n{user_prompt}"

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[{
                "role": "user",
                "parts": [{"text": combined_prompt}]
            }],
            config={
                "temperature": temperature,
                "max_output_tokens": 300
            }
        )

        # ---------------------------
        # 1️⃣ Print token usage
        # ---------------------------
        if hasattr(response, "usage_metadata"):
            usage = response.usage_metadata
            print("=== GEMINI TOKEN USAGE ===")
            print("Prompt tokens:", usage.prompt_token_count)
            print("Candidates tokens:", usage.candidates_token_count)
            print("Total tokens:", usage.total_token_count)
            print("==========================")

        # ---------------------------
        # 2️⃣ Extract clean text
        # ---------------------------
        if response.text:
            return response.text.strip()

        # fallback extraction
        output = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "text"):
                    output.append(part.text)

        return "\n".join(output).strip()

    except Exception as e:
        print("Gemini Error:", str(e))
        return "I'm having trouble generating a response right now."
