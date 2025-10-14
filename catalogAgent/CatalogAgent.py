import requests
from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import List

def fetch_catalog():
    url = "https://fake-store-api.mock.beeceptor.com/api/products"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching catalog: {e}")
        return []

class Product(BaseModel):
    product: str = Field(description="Name of the product")
    category: str = Field(description="Category of the product")
    price: float = Field(description="Price of the product in USD")

class CatalogOutput(BaseModel):
    matched_products: List[Product] = Field(
        description="List of matching products with name, category, and price."
    )
    justification: str =Field(description='justification and convincing the user to buy on of the 3 products')

async def create_catalog_agent(session_service,AppName,UserId,SessionId,recommended_product):
    catalog = fetch_catalog()
    user_history=None
    session = await session_service.get_session(
    app_name=AppName,
    user_id=UserId,
    session_id=SessionId
    )
    user_history = session.state.get("history")
    if user_history and isinstance(user_history, list):
        avg_price = sum(item["price"] for item in user_history if "price" in item) / len(user_history)
    else:
        avg_price = 0
    return Agent(
        name="CatalogAgent",
        model="gemini-2.0-flash",
        description="Agent that searches for related or similar products in the catalog.",
        instruction=f"""
        You are a product catalog search assistant.
        You will receive a product name and a price range , and you must search for similar or complementary products
        in the catalog below:

        CATALOG = {catalog}
        you must get 3 products and search by catalog name and the price of the product is recommended to be in the same price range of the users which you can access from {avg_price} 
        And please give a good justification for your answer I want you to convince the user to buy one of the three recommended products
        Return 2 JSON responses one  in this exact format:
        {{
        "matched_products": [
            {{"product": "Product 1", "category": "Category 1", "price": price1}},
            {{"product": "Product 2", "category": "Category 2", "price": price2}},
            {{"product": "Product 3", "category": "Category 3", "price": price3}},
        ]
        }}
        and the other contains only the justification 
        """,
        output_schema=CatalogOutput,
    )