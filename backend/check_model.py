import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load backend/.env regardless of current working directory.
load_dotenv(Path(__file__).resolve().parent / ".env")

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError(
        "Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY in environment or backend/.env"
    )

client = genai.Client(api_key=api_key)


models = client.models.list()

print("\nAvailable Models:\n")

for m in models:
    print("Name:", m.name)
    print("Display Name:", getattr(m, "display_name", None))
    print("Input Token Limit:", getattr(m, "input_token_limit", None))
    print("Output Token Limit:", getattr(m, "output_token_limit", None))
    print("-" * 40)
