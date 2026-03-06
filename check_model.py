from google import genai
import os


client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


models = client.models.list()

print("\nAvailable Models:\n")

for m in models:
    print("Name:", m.name)
    print("Display Name:", getattr(m, "display_name", None))
    print("Input Token Limit:", getattr(m, "input_token_limit", None))
    print("Output Token Limit:", getattr(m, "output_token_limit", None))
    print("-" * 40)
