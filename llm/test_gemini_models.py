import os
from google import genai

def list_models():
    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    print("\nAvailable Gemini Models:\n")

    for model in client.models.list():
        if "generateContent" in model.supported_actions:
            print(f"Model name: {model.name}")
            print(f"  Description: {model.description}")
            print(f"  Input tokens: {model.input_token_limit}")
            print(f"  Output tokens: {model.output_token_limit}")
            print("-" * 50)

if __name__ == "__main__":
    list_models()
