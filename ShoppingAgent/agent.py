from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.genai import types
from pydantic import BaseModel,Field
import json
import uuid
import asyncio

async def main():
    load_dotenv() #load env file (api key, etc..)
    session_memory=InMemorySessionService()
    AppName="ShoppingAssistant"
    UserId="A123"
    SessionId=str(uuid.uuid4())

    user_history={
        "user_id": UserId,
        "history": [
            {"product": "Bluetooth headphones", "category": "electronics", "price": 120},
            {"product": "Running shoes", "category": "sportswear", "price": 80}
        ]
    }

    await session_memory.create_session(
        app_name=AppName,
        user_id=UserId,
        session_id=SessionId,
        state=user_history,
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
                    print(f"The recommended product is: {product}")
                    justification=data.get("justification", "Unknown")
                    print(f"The justification is: {justification}")
                except json.JSONDecodeError:
                    print("Model did not return valid JSON.")
    print("Session Event")
    session=await session_memory.get_session(
        app_name=AppName,
        user_id=UserId,
        session_id=SessionId,
    )
    print("Final session state")
    for key, value in session.state.items():
        print(f"{key}:{value}")

asyncio.run(main())