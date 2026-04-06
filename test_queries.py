#!/usr/bin/env python3
import requests
import json
import sys

BASE_URL = "http://localhost:8000/chat"

queries = [
    "What products do you have?",
    "What toothpaste do you have?",
    "Show me all toothpaste",
    "What refined oils do you have?",
    "Sensodyne Rapid Relief 25g",
    "Dhara Refined Sunflower Oil 5L",
    "Toothpaste for sensitivity",
    "Whitening toothpaste",
    "Compare Dhara and Saffola oils",
    "Where is the toothpaste?",
    "Toothpaste under 50",
    "Cheapest oil",
    "Most expensive ghee",
    "Oil in 1L size",
    "What would you recommend for toothpaste?",
    "Do you have Colgate?",
    "Best oil for cooking",
]

results = []

for i, query in enumerate(queries, 1):
    try:
        resp = requests.post(BASE_URL, json={"query": query}, timeout=10)
        data = resp.json()
        response = data.get('response', 'NO RESPONSE')
        
        results.append({
            "query_num": i,
            "query": query,
            "response": response[:200] + "..." if len(response) > 200 else response
        })
        
    except Exception as e:
        results.append({
            "query_num": i,
            "query": query,
            "response": f"ERROR: {str(e)}"
        })

# Print results
for r in results:
    print(f"\n{'='*60}")
    print(f"TEST {r['query_num']}: {r['query']}")
    print(f"{'='*60}")
    print(f"Response: {r['response']}")

# Save to file
with open("/Users/nishanthsgowda/Reta-AI/test_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n\n✓ Results saved to test_results.json")
