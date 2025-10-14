from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.genai import types
from pydantic import BaseModel,Field
import json
import uuid
import asyncio
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Allow import of sibling folders
from catalogAgent.CatalogAgent import create_catalog_agent

async def main():
    load_dotenv() #load env file (api key, etc..)
    session_memory=InMemorySessionService()
    AppName="ShoppingAssistant"
    UserId="A123"
    SessionId=str(uuid.uuid4())

    # user_history={
    #     "user_id": UserId,
    #     "history": [
    #         {"product": "Bluetooth headphones", "category": "electronics", "price": 120},
    #         {"product": "Running shoes", "category": "sportswear", "price": 80}
    #     ]
    # }
    initial_state = {
        "user_id": UserId,
        "history": [
            {"product": "Bluetooth headphones", "category": "electronics", "price": 120},
            {"product": "Running shoes", "category": "sportswear", "price": 80},
        ],
        "recommended_product": None,
        "catalog_products": [],
        "selected_product": None,
        "purchases": []
    }

    await session_memory.create_session(
        app_name=AppName,
        user_id=UserId,
        session_id=SessionId,
        state=initial_state,
    )
    class CapitalOutput(BaseModel):
        product: str=Field(description="only the name of the recommended product")
        justification: str=Field(description="Here write the justification of this recommendation")
    root_agent=Agent(
        name="ShoppingAgent",
        model="gemini-2.0-flash",
        description="An agent that recommends products based on user purchase history.",
        instruction="""
        You are a helpful shopping assistant. 
        Analyze the user's purchase history which has as id = {user_id} and history={history} , infer preferences, 
        recommend new products logically, and justify your recommendation.
        Then display the top products from the catalog that match the recommendation and is good with user price range {history.price}.
        I want the output to be in form of this json
        {
        "product": only the name of the recommended product don't write full justification in this output variable,
        "justification": "Here write the justification of this recommendation",
        }
        """,
        output_schema=CapitalOutput,
    )
    runner=Runner(
        agent=root_agent,
        app_name=AppName,
        session_service=session_memory
    )
    message=types.Content(
        role="user",parts=[types.Part(text="what do you Recommend as a product based on user history")]
    )
    recommended_product = None
    catalog_items = None
    for event in runner.run(
        user_id=UserId,
        session_id=SessionId,
        new_message=message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                raw_output=event.content.parts[0].text
                try:
                    data = json.loads(raw_output)
                    product = data.get("product", "Unknown")
                    recommended_product = product

                    session = await session_memory.get_session(app_name=AppName, user_id=UserId, session_id=SessionId)
                    state = session.state
                    state["recommended_product"] = recommended_product
                    await session_memory.create_session(app_name=AppName, user_id=UserId, session_id=SessionId, state=state)
                    print("the recommendation agent processing")
                    print(f"The recommended product is: {product}")
                    justification=data.get("justification", "Unknown")
                    print(f"The justification is: {justification}")
                except json.JSONDecodeError:
                    print("Model did not return valid JSON.")
    # print("Session Event")
    # session=await session_memory.get_session(
    #     app_name=AppName,
    #     user_id=UserId,
    #     session_id=SessionId,
    # )
    # print("Final session state")
    # for key, value in session.state.items():
    #     print(f"{key}:{value}")
    if recommended_product:
        print("\n Catalog Agent is now searching for similar items...")

        catalog_agent = await create_catalog_agent(
            session_service=session_memory,AppName=AppName,UserId=UserId,SessionId=SessionId,recommended_product=recommended_product
        )

        catalog_runner = Runner(agent=catalog_agent, app_name=AppName, session_service=session_memory)

        catalog_message = types.Content(
            role="user",
            parts=[types.Part(text="Find similar products to the one recommended earlier.")]
        )

        for event in catalog_runner.run(user_id=UserId, session_id=SessionId, new_message=catalog_message):
            if event.is_final_response() and event.content and event.content.parts:
                print("\n Matching Catalog Items:")
                data = json.loads(event.content.parts[0].text)
                catalog_items = data.get("matched_products", [])
                justify=data.get("justification")
                session = await session_memory.get_session(app_name=AppName, user_id=UserId, session_id=SessionId)
                state = session.state
                state["catalog_products"] = catalog_items
                await session_memory.create_session(app_name=AppName, user_id=UserId, session_id=SessionId, state=state)

    if catalog_items:
        for i, product in enumerate(catalog_items, 1):
            print(f"{i}. {product['product']} - {product['category']} (${product['price']})")
        print(justify)
        
        choice = input("\nEnter the number of the product you want to purchase (1-3): ")
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(catalog_items):
                selected_product = catalog_items[choice_idx]
                print(f"\nYou selected: {selected_product}")

                session = await session_memory.get_session(app_name=AppName, user_id=UserId, session_id=SessionId)
                state = session.state
                state["selected_product"] = selected_product
                state["purchases"].append({"product": selected_product, "status": "success"})
                await session_memory.create_session(app_name=AppName, user_id=UserId, session_id=SessionId, state=state)

            else:
                print("Invalid choice. Defaulting to first product.")
                selected_product = catalog_items[0]
        except ValueError:
            print("Invalid input. Defaulting to first product.")
            selected_product = catalog_items[0]
    from purchaseAgent.PurchaseAgent import create_purchase_agent

    print("\n Processing simulated purchase...")

    purchase_agent = await create_purchase_agent(
        session_service=session_memory,
        AppName=AppName,
        UserId=UserId,
        SessionId=SessionId,
        selected_product=selected_product
    )

    purchase_runner = Runner(agent=purchase_agent, app_name=AppName, session_service=session_memory)

    purchase_message = types.Content(
        role="user",
        parts=[types.Part(text=f"Purchase {selected_product}")]
    )

    for event in purchase_runner.run(user_id=UserId, session_id=SessionId, new_message=purchase_message):
        if event.is_final_response() and event.content and event.content.parts:
            print("\n Purchase agent processing:")
            print(event.content.parts[0].text)
            session = await session_memory.get_session(app_name=AppName, user_id=UserId, session_id=SessionId)
            state = session.state
            state['history'].append(state["selected_product"])
            await session_memory.create_session(app_name=AppName, user_id=UserId, session_id=SessionId, state=state)
    print("User History is \n")
    for i in session.state['history']:
        print(i)


asyncio.run(main())