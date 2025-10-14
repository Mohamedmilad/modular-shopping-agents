from google.adk.agents import Agent

async def create_purchase_agent(session_service,AppName,UserId,SessionId,selected_product):
    session = await session_service.get_session(
        app_name=AppName,
        user_id=UserId,
        session_id=SessionId
    )
    selected_product = session.state.get("selected_product", {})

    return Agent(
        name="PurchaseAgent",
        model="gemini-2.0-flash",
        description="Handles simulated product purchases.",
        instruction="""
        You are a purchase agent.
        When given a product {selected_product}, simulate completing the purchase.
        Mention it's name it's category and it's price all found in the catalog
        Confirm success and update the user’s history.
        """
    )
