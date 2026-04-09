# RetaAI Pipeline

## Overview

This project implements an upgraded recommendation pipeline designed to improve retrieval accuracy, contextual understanding, filtering intelligence, and response quality. The system integrates structured intent parsing, vector-based retrieval, and intelligent response generation to deliver relevant and user-centric results.

## Deployment

The application is deployed and accessible at:

Web Link: [https://retaai.vercel.app/](https://retaai.vercel.app/)

Note: Initial response may take a few seconds due to cold start. Subsequent responses are faster.

## Key Improvements

### 1. Data Layer Expansion

* Utilizes all 18 columns from the dataset
* Uses precomputed `embedding_text` for improved semantic quality
* Eliminates the need for runtime embedding reconstruction

### 2. Intent Parser Enhancement

* Upgraded from 8-field to 11-field schema
* Added fields: `product_line`, `unit_type`, `source`, `comparison`
* Improved structured extraction for category, brand, size, and seasonal attributes

### 3. Constraint Engine

* Implements priority-based filtering (9-step pipeline)
* Hard constraints applied first (stock, category, brand)
* Soft filters applied later (seasonal, source)
* Includes smart relaxation (e.g., relax brand filter if no results)

### 4. Retrieval System

* Integrated FAISS index with normalized embeddings
* Supports ~2000 products with 384-dimensional vectors
* Stores full dataset as a DataFrame (pickle format)
* Deduplicates results based on product name

### 5. Recommendation Engine

* Uses `alternate_product_ids` for meaningful alternatives
* Incorporates store navigation hints using `assigned_color`

### 6. Response Generation

* Passes full dataset context to the language model
* Generates natural language responses with:

  * Product suggestions
  * Location guidance
  * Alternatives and comparisons

### 7. Voice Pipeline

* Enhanced vocabulary including product and brand names
* Improved fuzzy matching for transcription correction

### 8. Pipeline Simplification

* Streamlined RAG architecture
* Reduced complexity in response handling
* Improved performance and maintainability

## Architecture Summary

1. User Query Input (Text/Voice)
2. Intent Parsing (11-field schema)
3. Constraint Filtering (priority-based)
4. Vector Retrieval (FAISS)
5. Recommendation Resolution
6. Response Generation (LLM)
7. Output Delivery

## Performance Characteristics

* Improved retrieval accuracy due to structured embeddings
* Reduced latency through optimized pipeline flow
* Better result relevance via constraint prioritization
* Scalable architecture with potential for horizontal scaling

## Tech Stack

* Backend: Python
* Retrieval: FAISS
* LLM: Gemini
* Hosting: AWS EC2
* Frontend: Vercel

## Notes

* Performance depends on instance size and external API latency
* First request may experience cold start delay
* System can be scaled using load balancing and multiple instances
