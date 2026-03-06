from google import genai


client = genai.Client(api_key= "AIzaSyA9IaBJOUtPASJAOy0wEb571RfgzVIeL04")

models = client.models.list()

print("\nAvailable Models:\n")

for m in models:
    print("Name:", m.name)
    print("Display Name:", getattr(m, "display_name", None))
    print("Input Token Limit:", getattr(m, "input_token_limit", None))
    print("Output Token Limit:", getattr(m, "output_token_limit", None))
    print("-" * 40)
