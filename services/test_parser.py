from services.query_parser import parse_query

tests = [
    "Not Colgate. Something cheaper for sensitive teeth 100g",
    "Thank you bro",
    "Compare Saffola Gold and Fortune oil",
    "Is Amul almond milk available?",
    "fuck off",
]

for t in tests:
    print("\nUSER:", t)
    print(parse_query(t))
