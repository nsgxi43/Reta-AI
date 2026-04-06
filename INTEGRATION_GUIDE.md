# 🚀 Reta-AI Integration Complete — Quick Start Guide

## ✅ Status
- **Backend:** Running on http://localhost:8000 ✅
- **Frontend:** Running on http://localhost:3000 ✅
- **Integration:** Tested and working ✅
- **Dataset:** 2000 products with 18 columns ✅
- **LLM:** Gemini with retry + fallback model ✅

---

## 🧪 Quick Test

All tests **PASSED**:
```
✅ Health check
✅ Intent parsing (category extraction)
✅ Vector retrieval (FAISS)
✅ Constraint filtering (budget, category, brand, size)
✅ Product recommendations + alternates
✅ Natural language response generation
✅ Frontend suggestions from products list
```

---

## 🌐 Access the Application

### Option 1: Local Browser
1. Open **http://localhost:3000** in your browser
2. Enter your name and select **Text** mode
3. Start chatting!

**Example queries to test:**
- "shampoo for dry hair"
- "toothpaste under 200 rupees"
- "compare different shampoos"
- "moisturizer for sensitive skin"
- "budget-friendly face wash"

### Option 2: Direct API Testing
```bash
# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "toothpaste for sensitive teeth", "user_name": "Alice"}'

# Health check
curl http://localhost:8000/health
```

---

## 🔧 How to Restart Services

### Backend
```bash
# Terminal 1: Stop current backend (Ctrl+C in backend terminal)
# Then restart:
cd /Users/nishanthsgowda/Reta-AI/backend
/Users/nishanthsgowda/Reta-AI/reta-ai-env/bin/python main.py
```

### Frontend
```bash
# Terminal 2: (Already running, or restart with)
cd /Users/nishanthsgowda/Reta-AI/frontend
npm run dev
```

---

## 📊 What Each Component Does

### 1. **Data Layer** (`data/load_data.py`)
- Loads `product_improved_2000.xlsx`
- Exposes all 18 columns (product_id, brand, size_variant, price_inr, etc.)
- Pre-constructed embedding_text column

### 2. **Embedding + Search** (`embeddings/build_index.py` + `vectorstore/search.py`)
- 2000 products indexed with FAISS (384-dim normalized embeddings)
- Deduplicates by product_name for duplicate size variants
- Returns all columns for rich product context

### 3. **Intent Parser** (`services/query_parser.py`)
- Extracts: category, brand, budget_max, price_tier, size_variant, comparison, exclude_brands, seasonal, source, etc.
- Powered by Gemini with structured JSON output
- 11-field schema directly mapped to dataset columns

### 4. **Constraint Engine** (`services/constraint_engine.py`)
- 9-step priority filtering:
  1. Stock available (hard gate)
  2. Category match
  3. Brand match (with relaxation)
  4. Price budget
  5. Price tier
  6. Size variant
  7. Seasonal
  8. Source
  9. Exclude brands

### 5. **Recommendation Engine** (`services/recommendation_engine.py`)
- Primary: highest-scoring product passing all constraints
- Alternates: resolved from `alternate_product_ids` in dataset
- Zone: assigned_color for in-store location hints

### 6. **Response Renderer** (`services/renderer.py`)
- Generates natural language response with LLM
- Includes product details (brand, price, description, zone)
- Lists alternates and location hints

### 7. **Frontend** (`frontend/src/lib/conversation.tsx`)
- Calls POST `/chat` with {query, user_name}
- Receives {response, intent, primary, products}
- Displays response + product suggestions as buttons
- Auto-login and rating system

---

## 🎯 Test Scenarios

### Scenario 1: Basic Product Search
**Input:** "I need a shampoo"
**Expected:** 
- ✅ Category extraction: "Shampoo"
- ✅ Top product from FAISS search
- ✅ Alternates from recommendation engine
- ✅ Natural response with zone info

### Scenario 2: Budget Constraint
**Input:** "moisturizer under 300 rupees"
**Expected:**
- ✅ budget_max: 300
- ✅ Filtered products <= ₹300
- ✅ Recommendations sorted by relevance

### Scenario 3: Brand Exclusion
**Input:** "toothpaste but not Colgate"
**Expected:**
- ✅ exclude_brands: ["Colgate"]
- ✅ Results without Colgate products

### Scenario 4: Size Preference
**Input:** "small size shampoo 100ml"
**Expected:**
- ✅ size_variant: "100ml"
- ✅ Only 100ml products returned

### Scenario 5: Comparison
**Input:** "compare Dove and Ponds soaps"
**Expected:**
- ✅ comparison: True
- ✅ 2-5 products side-by-side response

---

## 🔍 Debugging Tips

### Check Backend Logs
```bash
# Look for startup messages in backend terminal:
# - "RAG warmup starting..."
# - "RAG warmup complete."
# - "Uvicorn running on http://0.0.0.0:8000"
```

### Check Frontend Console
```bash
# Open browser DevTools (F12) → Console tab
# Look for API errors or response logging
```

### Test Backend Directly
```bash
# Quick test without frontend
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"any query","user_name":"test"}' \
  | python3 -m json.tool
```

---

## 📱 Frontend Features

### Chat Interface
- Login with any username
- Text input with auto-resize
- Conversation history with timestamps
- Agent typing indicator
- Product suggestions as clickable buttons
- Rating system (auto-trigger on conclusive phrases like "thanks", "bye", "done")

### Voice Interface (optional)
- Microphone input with auto-stop on silence
- Whisper transcription
- Brand/product name fuzzy correction
- TTS response (optional)

---

## 🚀 Next Steps (Production)

1. **Deploy Backend** (e.g., Cloud Run, AWS Lambda)
   - Update `NEXT_PUBLIC_API_URL` in frontend `.env.local`
   - Set `GEMINI_API_KEY` env var in production

2. **Deploy Frontend** (e.g., Vercel, Netlify)
   - `npm run build && npm start`

3. **Monitor**
   - Log API response times
   - Track intent distribution
   - Monitor Gemini API quota usage

4. **Optimize**
   - Cache popular queries
   - Fine-tune embedding model
   - A/B test ranking algorithms

---

## 📞 Support

**Common Issues:**

- **"Port already in use"** → Kill existing process:
  ```bash
  lsof -ti:8000 | xargs kill -9  # Backend
  lsof -ti:3000 | xargs kill -9  # Frontend
  ```

- **"GEMINI_API_KEY not set"** → Add to `backend/.env`:
  ```
  GEMINI_API_KEY=your_key_here
  GOOGLE_API_KEY=your_key_here
  ```

- **"Index not found"** → Rebuild:
  ```bash
  cd backend && python embeddings/build_index.py
  ```

---

**Enjoy testing! 🎉**
