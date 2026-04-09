# RetaAI: Intelligent Retail Assistant

An AI-powered retail recommendation system with voice input, natural language processing, and intelligent product retrieval using Retrieval-Augmented Generation (RAG). The system helps customers find the right products through a conversational interface.

---

## Overview

Reta-AI is a conversational retail assistant that enables product discovery using:

- Vector embeddings for semantic search over 2,000 products  
- Structured intent parsing (11-field schema)  
- Priority-based constraint filtering with intelligent relaxation  
- Gemini-powered natural language response generation  
- Voice input with transcription and fuzzy correction  
- Store navigation using color-based location mapping  
- Web interface built with Next.js  

### Latest Improvements

- Full dataset integration using all 18 columns  
- Enhanced 11-field intent schema  
- Priority-based 9-step constraint engine  
- Precomputed alternate product recommendations  
- Store location mapping using color zones  
- Rich contextual responses using full dataset  

---

## Deployment

The application is deployed and accessible at:

Web Link: https://retaai.vercel.app/

Note: The first response may take a few seconds due to cold start. Subsequent responses are faster.

---

## Features

- Semantic search using FAISS with normalized 384-dimensional embeddings  
- Structured intent extraction (category, brand, size, budget, seasonal, etc.)  
- Intelligent filtering using ordered constraint pipeline  
- Context-aware recommendations with alternates  
- Voice input with improved transcription accuracy  
- Natural language responses with product and location details  
- Real-time web-based chat interface  
- Coverage of 2,000+ products  

---

## Architecture

Frontend (Next.js)  
- Chat interface with voice and text input  

Backend (FastAPI)  
- Query parsing  
- FAISS vector retrieval  
- Constraint filtering  
- Recommendation engine  
- Response generation using Gemini  

Data Layer  
- 18-column product dataset  
- FAISS index for similarity search  
- Metadata stored as DataFrame  

---

## Key Components

### 1. Intent Parser
Converts user queries into structured 11-field schema including category, brand, size, budget, and preferences.

### 2. Constraint Engine
Applies filters in priority order:
1. Stock availability  
2. Category  
3. Brand (with relaxation if needed)  
4. Price  
5. Size  
6. Seasonal  
7. Source  
8. Exclusions  

### 3. Retrieval System
- FAISS-based vector search  
- Normalized embeddings (384-dim)  
- Deduplication of products  

### 4. Recommendation Engine
- Selects best product  
- Uses precomputed alternate product IDs  
- Adds store location hints  

### 5. Response Generator
- Uses Gemini for natural language output  
- Includes product details, alternatives, and location guidance  

---

## Tech Stack

- Backend: Python (FastAPI)  
- Retrieval: FAISS  
- LLM: Gemini  
- Frontend: Next.js  
- Hosting: AWS EC2 (backend), Vercel (frontend)  

---

## Performance Notes

- Retrieval accuracy improved using structured embeddings  
- Faster filtering using priority-based constraints  
- Reduced latency through simplified pipeline  
- First request may experience cold start delay  

---


## Documentation

Refer to the following for more details:

- PIPELINE_UPGRADE_SUMMARY.md  
- INTEGRATION_GUIDE.md  
- CUSTOMER_TEST_CASES.md  
