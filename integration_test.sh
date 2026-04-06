#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "🧪 Frontend-Backend Integration Test"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Test health check
echo "1️⃣  Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8000/health)
if [[ $HEALTH == *"ok"* ]]; then
  echo "   ✅ Backend health: OK"
else
  echo "   ❌ Backend health check failed"
  exit 1
fi
echo ""

# Test chat with query 1
echo "2️⃣  Testing chat endpoint - Query 1: 'toothpaste for sensitive teeth'"
RESPONSE1=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"toothpaste for sensitive teeth","user_name":"Alice"}')

if [[ $RESPONSE1 == *"response"* ]]; then
  echo "   ✅ Response received"
  RESP_TEXT=$(echo $RESPONSE1 | grep -o '"response":"[^"]*' | head -c 100)
  echo "   Response preview: ${RESP_TEXT:12}..."
  
  # Check for products array
  if [[ $RESPONSE1 == *"products"* ]]; then
    echo "   ✅ Products suggestions included"
  fi
else
  echo "   ❌ Chat endpoint failed"
  exit 1
fi
echo ""

# Test chat with query 2
echo "3️⃣  Testing chat endpoint - Query 2: 'compare shampoos'"
RESPONSE2=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"compare different shampoos","user_name":"Bob"}')

if [[ $RESPONSE2 == *"response"* ]]; then
  echo "   ✅ Response received"
  if [[ $RESPONSE2 == *"intent"* ]]; then
    echo "   ✅ Intent parsed"
  fi
else
  echo "   ❌ Chat endpoint failed for query 2"
  exit 1
fi
echo ""

# Test chat with query 3 - budget constraint
echo "4️⃣  Testing chat endpoint - Query 3: 'moisturizer under 500 rupees'"
RESPONSE3=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"moisturizer under 500 rupees","user_name":"Charlie"}')

if [[ $RESPONSE3 == *"response"* ]]; then
  echo "   ✅ Response received for budget query"
  if [[ $RESPONSE3 == *"primary"* ]]; then
    echo "   ✅ Primary product selected"
  fi
else
  echo "   ❌ Chat endpoint failed for query 3"
  exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "✅ All integration tests passed!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🌐 Frontend accessible at: http://localhost:3000"
echo "🔌 Backend accessible at: http://localhost:8000"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Login with any name"
echo "  3. Chat with the assistant!"
