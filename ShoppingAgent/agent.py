import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.genai import types
from pydantic import BaseModel,Field
from purchaseAgent.PurchaseAgent import create_purchase_agent
from UI.UserAgentScreen import init_ui, show_text, get_input, start_ui_loop, close_ui
import json
import uuid
import asyncio
from catalogAgent.CatalogAgent import create_catalog_agent
def save_history_to_json(history, filename="user_history.json"):
    """Save the session history dictionary to a JSON file."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(root_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print(f"User history saved to {file_path}")
    except Exception as e:
        print(f"Error saving history: {e}")
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
    init_ui()
    for event in runner.run(
        user_id=UserId,
        session_id=SessionId,
        new_message=message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                raw_output=event.content.parts[0].text
                # print(f"Final Response: {raw_output}")
                try:
                    data = json.loads(raw_output)
                    product = data.get("product", "Unknown")
                    recommended_product = product

                    session = await session_memory.get_session(app_name=AppName, user_id=UserId, session_id=SessionId)
                    state = session.state
                    state["recommended_product"] = recommended_product
                    await session_memory.create_session(app_name=AppName, user_id=UserId, session_id=SessionId, state=state)
                    show_text("the recommendation agent processing", sender="ai")
                    show_text(f"\n The recommended product is: {json.dumps(product, indent=2)}", sender="ai")
                    # show_text(f"The recommended product is: {product}", sender="ai")
                    print("the recommendation agent processing")
                    print(f"The recommended product is: {product}")
                    justification=data.get("justification", "Unknown")
                    show_text(f"\n The justification is: {json.dumps(justification, indent=2)}", sender="ai")
                    # show_text(f"The justification is: {justification}", sender="ai")
                    print(f"The justification is: {justification}")
                except json.JSONDecodeError:
                    show_text("Model didn't inderstand request", sender="ai")
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
        show_text("\n Catalog Agent is now searching for similar items...", sender="ai")
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
                show_text("\n Matching Catalog Items:", sender="ai")
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
            show_text(f"{i}. {product['product']} - {product['category']} (${product['price']})", sender="ai")
            print(f"{i}. {product['product']} - {product['category']} (${product['price']})")
        show_text(justify, sender="ai")
        print(justify)
        choice = get_input("\nEnter the number of the product you want to purchase (1-3): ")
        # choice = input("\nEnter the number of the product you want to purchase (1-3): ")
        show_text(choice, sender="user")
        
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(catalog_items):
                selected_product = catalog_items[choice_idx]
                show_text(f"\nYou selected: {json.dumps(selected_product, indent=2)}", sender="ai")
                print(f"\nYou selected: {selected_product}")

                session = await session_memory.get_session(app_name=AppName, user_id=UserId, session_id=SessionId)
                state = session.state
                state["selected_product"] = selected_product
                # state["purchases"].append({"product": selected_product, "status": "success"})
                await session_memory.create_session(app_name=AppName, user_id=UserId, session_id=SessionId, state=state)

            else:
                show_text("Invalid choice. Defaulting to first product.", sender="ai")
                print("Invalid choice. Defaulting to first product.")
                selected_product = catalog_items[0]
        except ValueError:
            show_text("Invalid choice. Defaulting to first product.", sender="ai")
            print("Invalid input. Defaulting to first product.")
            selected_product = catalog_items[0]
    
    show_text("\n Processing simulated purchase...", sender="ai")
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
            show_text("\n Purchase agent processing:", sender="ai")
            show_text(f"\n{json.dumps(event.content.parts[0].text, indent=2)}", sender="ai")
            # show_text(event.content.parts[0].text, sender="ai")
            print("\n Purchase agent processing:")
            print(event.content.parts[0].text)
            session = await session_memory.get_session(app_name=AppName, user_id=UserId, session_id=SessionId)
            state = session.state
            state['history'].append(state["selected_product"])
            await session_memory.create_session(app_name=AppName, user_id=UserId, session_id=SessionId, state=state)
    show_text("User History is \n", sender="ai")
    print("User History is \n")
    for i in session.state['history']:
        show_text(json.dumps(i, indent=2), sender="ai")
        print(i)
    show_text(json.dumps(f"Purchases are {session.state['purchases']}", indent=2), sender="ai")
    print(f"Purchases are {session.state['purchases']}")
    save_history_to_json(session.state["history"])
asyncio.run(main())
start_ui_loop()
