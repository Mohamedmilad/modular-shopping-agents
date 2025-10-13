import requests
from google.adk.agents import Agent
from pydantic import BaseModel, Field

def fetch_catalog():
    url = "https://fake-store-api.mock.beeceptor.com/api/products"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching catalog: {e}")
        return []

class CatalogOutput(BaseModel):
    matched_products: list[str] = Field(
        description="List of product names similar or related to the given product name."
    )

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
        Return a JSON response in this exact format:
        {{
            "matched_products": ["Product 1", "Product 2", "Product 3"]
        }}
        """,
        output_schema=CatalogOutput,
    )

