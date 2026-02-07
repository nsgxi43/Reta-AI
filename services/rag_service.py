from vectorstore.search import VectorSearch
from rules.filters import (
    filter_by_category,
    filter_by_color,
    prefer_size
)
from llm.prompts import build_prompt
from llm.client import generate_response


class RAGService:
    def __init__(self):
        self.searcher = VectorSearch()

    def query(
        self,
        user_query: str,
        category: str = None,
        color: str = None,
        preferred_size: str = None
    ):
        products = self.searcher.search(user_query, top_k=10)

        products = filter_by_category(products, category)
        products = filter_by_color(products, color)
        products = prefer_size(products, preferred_size)

        prompt = build_prompt(user_query, products)
        response = generate_response(prompt)

        return {
            "query": user_query,
            "products": products,
            "response": response
        }
