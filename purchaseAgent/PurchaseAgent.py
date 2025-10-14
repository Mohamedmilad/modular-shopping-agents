from google.adk.agents import Agent

async def purchase_tool(session_service, AppName, UserId, SessionId):
    """Simulates a purchase and updates the user's session state."""
    session = await session_service.get_session(
        app_name=AppName,
        user_id=UserId,
        session_id=SessionId
    )
    state = session.state
    selected_product = state.get("selected_product", {})

    if selected_product:
        state["purchases"].append({"product": selected_product, "status": "success"})
        await session_service.create_session(
            app_name=AppName,
            user_id=UserId,
            session_id=SessionId,
            state=state
        )
        return {
            "message": f"Purchase recorded successfully for {selected_product['product']} (${selected_product['price']})."
        }
    else:
        return {"message": "No selected product found to purchase."}

def make_purchase_tool(session_service, AppName, UserId, SessionId):
    async def tool():
        """Tool wrapper with valid function name."""
        return await purchase_tool(session_service, AppName, UserId, SessionId)
    tool.__name__ = "purchase_tool"
    return tool

async def create_purchase_agent(session_service, AppName, UserId, SessionId, selected_product):
    session = await session_service.get_session(
        app_name=AppName,
        user_id=UserId,
        session_id=SessionId
    )
    selected_product = session.state.get("selected_product", selected_product)

    return Agent(
        name="PurchaseAgent",
        model="gemini-2.0-flash",
        description="Handles simulated product purchases.",
        instruction=f"""
        You are a purchase agent.
        When given a product {selected_product}, simulate completing the purchase.
        Mention its name, category, and price as found in the catalog.
        Confirm success and update the user's history by calling the purchase_tool.
        """,
        tools=[make_purchase_tool(session_service, AppName, UserId, SessionId)]
    )