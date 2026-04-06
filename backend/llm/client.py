import os
import time
from pathlib import Path

from google import genai
from dotenv import load_dotenv

# Load backend/.env regardless of current working directory.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not _api_key:
    raise RuntimeError(
        "Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY in environment or backend/.env"
    )

client = genai.Client(api_key=_api_key)

MODEL_NAME = os.environ.get("GEMINI_MODEL", "models/gemini-2.5-flash-lite")
FALLBACK_MODEL_NAME = os.environ.get(
    "GEMINI_FALLBACK_MODEL", "models/gemini-2.0-flash-lite"
)


def _is_transient_error(err: Exception) -> bool:
    msg = str(err).upper()
    return any(token in msg for token in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "INTERNAL"]) 


def _generate_with_model(model_name: str, combined_prompt: str, temperature: float):
    return client.models.generate_content(
        model=model_name,
        contents=[{
            "role": "user",
            "parts": [{"text": combined_prompt}]
        }],
        config={
            "temperature": temperature,
            "max_output_tokens": 300
        }
    )


def generate_response(system_prompt: str, user_prompt: str, temperature=0.3):
    combined_prompt = f"{system_prompt}\n\n{user_prompt}"

    response = None
    last_error = None

    try:
        # Retry transient errors on primary model.
        for attempt in range(3):
            try:
                response = _generate_with_model(MODEL_NAME, combined_prompt, temperature)
                break
            except Exception as e:
                last_error = e
                if not _is_transient_error(e) or attempt == 2:
                    break
                time.sleep(0.6 * (2 ** attempt))

        # Fall back to a generally available model if primary failed transiently.
        if response is None and last_error and _is_transient_error(last_error):
            for attempt in range(2):
                try:
                    response = _generate_with_model(
                        FALLBACK_MODEL_NAME, combined_prompt, temperature
                    )
                    print(
                        f"Gemini fallback model used: {FALLBACK_MODEL_NAME} (primary: {MODEL_NAME})"
                    )
                    break
                except Exception as e:
                    last_error = e
                    if not _is_transient_error(e) or attempt == 1:
                        break
                    time.sleep(0.8 * (2 ** attempt))

        if response is None:
            raise last_error if last_error else RuntimeError("Unknown Gemini generation failure")

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
        print(
            f"Gemini Error (model={MODEL_NAME}, fallback={FALLBACK_MODEL_NAME}): {str(e)}"
        )
        return "I'm having trouble generating a response right now."
