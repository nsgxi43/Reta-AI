#!/usr/bin/env python3
"""Test new RAG pipeline with improved dataset."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

print("🚀 Importing and initializing...", flush=True)
from services.rag_service import RAGService
rag = RAGService()
print("✅ RAG initialized\n", flush=True)

# Test single query
q = "toothpaste for sensitive teeth"
print(f"📝 Query: {q}\n", flush=True)

try:
    print("⏳ Running RAG query...", flush=True)
    result = rag.query(q)
    
    print(f"\n✅ Query completed!\n", flush=True)
    
    print(f"📋 Parsed Intent:")
    for k, v in result.get("parsed", {}).items():
        if v not in [None, False, []]:
            print(f"  {k}: {v}")
    
    primary = result.get("primary")
    if primary:
        print(f"\n🎯 Primary Product:")
        print(f"  Name: {primary.get('product_name')}")
        print(f"  Brand: {primary.get('brand')}")
        print(f"  Price: ₹{primary.get('price_inr')}")
        print(f"  Category: {primary.get('product_category')}")
        print(f"  Zone: {result.get('zone', primary.get('assigned_color'))}")
    else:
        print(f"\n⚠️ No primary product found")
    
    alts = result.get("alternates", [])
    if alts:
        print(f"\n📦 Alternates ({len(alts)}):")
        for i, alt in enumerate(alts[:3], 1):
            print(f"  {i}. {alt['product_name']} ({alt['brand']}) - ₹{alt.get('price_inr')}")
    
    resp = result.get("response", "")
    print(f"\n💬 Response:\n{resp}")
    
except Exception as e:
    print(f"❌ Error: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("\n✅ Test complete!", flush=True)


