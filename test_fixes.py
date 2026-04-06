#!/usr/bin/env python3
import requests
import json
import time

base_url = "http://localhost:8000"

test_cases = [
    {
        "name": "Exact Product Match - Sensodyne",
        "query": "Sensodyne Rapid Relief 25g",
        "expected": "Sensodyne Rapid Relief 25g",
        "test_num": 1
    },
    {
        "name": "Exact Product Match - Dhara Oil",
        "query": "Dhara Refined Sunflower Oil 5L",
        "expected": "Dhara|Refined|5L",
        "test_num": 2
    },
    {
        "name": "Comparison - Refined Oils",
        "query": "Compare Dhara and Saffola oils",
        "expected": "Dhara|Saffola",
        "test_num": 3
    },
    {
        "name": "Navigation - Zone Location",
        "query": "Where is the toothpaste?",
        "expected": "zone|Zone",
        "test_num": 4
    }
]

print("=" * 70)
print("TESTING 4 CRITICAL FIXES")
print("=" * 70)

results = []
for test in test_cases:
    print(f"\n[Test {test['test_num']}] {test['name']}")
    print(f"Query: {test['query']}")
    
    try:
        resp = requests.post(
            f"{base_url}/chat",
            json={"query": test['query'], "voice_mode": False},
            timeout=25
        )
        
        if resp.status_code == 200:
            data = resp.json()
            response = data.get('response', '')
            
            print(f"Response: {response[:300]}")
            
            # Check if expected content is in response
            import re
            expected_pattern = test['expected']
            found = bool(re.search(expected_pattern, response, re.IGNORECASE))
            
            if found:
                print("✅ PASS")
                results.append((test['test_num'], test['name'], "PASS"))
            else:
                print(f"⚠️  CHECK - Expected pattern '{expected_pattern}' not found")
                results.append((test['test_num'], test['name'], "PARTIAL"))
        else:
            print(f"❌ Error: HTTP {resp.status_code}")
            results.append((test['test_num'], test['name'], "FAIL"))
            
    except Exception as e:
        print(f"❌ Exception: {str(e)[:100]}")
        results.append((test['test_num'], test['name'], "ERROR"))

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
for num, name, status in results:
    print(f"Test {num}: {status:8} | {name}")

pass_count = sum(1 for _, _, s in results if s == "PASS")
print(f"\n✅ Passed: {pass_count}/4")
