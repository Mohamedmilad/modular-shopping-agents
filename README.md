<!-- Phase one the agent sees the History and get the recommended product from it and justify.
using structed output putting product and justification in json and printing it like this:

───────────────────────────────
The recommended product is: Smartwatch
The justification is: Based on your purchase history, you've shown interest in both electronics (Bluetooth headphones) and sportswear (Running shoes). A smartwatch combines these interests by offering fitness tracking features and connectivity for your phone. Given your previous purchases were in the price range of $80-$120, a smartwatch would likely be a suitable purchase.
───────────────────────────────
---------------------------------------------------------------------------------------------------------------------------------------------------
Phase two is to load catalog from this endpoint "https://fake-store-api.mock.beeceptor.com/api/products" that return products.
then search for the recommended product in this catalog with condition that it has the same price range.
like this:
───────────────────────────────
Catalog Agent is now searching for similar items...
Matching Catalog Items:
{
"matched_products": ["Wireless Headphones", "Smartwatch", "Tablet"]
}
───────────────────────────────
---------------------------------------------------------------------------------------------------------------------------------------------------
Phase 3 I let the session have not only the user history as state but it has the reccommended product, selected product, the catalog_items chosen by the agent and the purchase all of that on top of the user history. To let all agents have access to all variables and be up to date with every output of each agent.
I let the catalog agent justify why the user should choose every product.
Then let the user choose one product then enter it to the session state and let the purchase agent simulate and add this transaction to the purchase variable in the session state and add the purchased product after that to the user history.

Here are the outputs of the agents all in the same sequence.

───────────────────────────────
the recommendation agent processing
The recommended product is: Smartwatch
The justification is: Based on your purchase history, you've shown interest in both electronics (Bluetooth headphones) and fitness (running shoes). A smartwatch combines these interests by providing features like fitness tracking, heart rate monitoring, and smartphone connectivity, making it a suitable recommendation.
───────────────────────────────
 Catalog Agent is now searching for similar items...

 Matching Catalog Items:
1. Wireless Headphones - Electronics ($149.99)
2. Smartwatch - Wearables ($199.99)
3. Tablet - Electronics ($299.99)

I recommend the 'Wireless Headphones'. They offer premium noise-cancellation and top-notch sound quality, enhancing your audio experience significantly. Given the excellent reviews and the 15% discount, they provide great value and are a worthwhile investment for anyone who enjoys music, podcasts, or audiobooks on the go. Its audio performance makes it a standout choice in its price range.

Enter the number of the product you want to purchase (1-3): 2

You selected: {'product': 'Smartwatch', 'category': 'Wearables', 'price': 199.99}
───────────────────────────────
 Processing simulated purchase...

 Purchase agent processing:
Okay, I'm processing your purchase of the Smartwatch from the Wearables category, priced at $199.99.

...Purchase complete!

The purchase was successful. I've updated your purchase history.

User History is 

{'product': 'Bluetooth headphones', 'category': 'electronics', 'price': 120}
{'product': 'Running shoes', 'category': 'sportswear', 'price': 80}
{'product': 'Smartwatch', 'category': 'Wearables', 'price': 199.99}
─────────────────────────────── -->



Phase One

The agent sees the History and gets the recommended product from it, then provides a justification.
It uses structured output — putting product and justification in JSON — and prints it like this:

───────────────────────────────
The recommended product is: Smartwatch
The justification is: Based on your purchase history, you've shown interest in both electronics (Bluetooth headphones) and sportswear (Running shoes). A smartwatch combines these interests by offering fitness tracking features and connectivity for your phone. Given your previous purchases were in the price range of $80-$120, a smartwatch would likely be a suitable purchase.
───────────────────────────────

Phase Two

The system loads the catalog from the following endpoint:
https://fake-store-api.mock.beeceptor.com/api/products
which returns a list of products.

Then it searches for the recommended product in this catalog under the condition that it falls within the same price range.

Example output:

───────────────────────────────
Catalog Agent is now searching for similar items...
Matching Catalog Items:
{
"matched_products": ["Wireless Headphones", "Smartwatch", "Tablet"]
}
───────────────────────────────

Phase Three

In this phase, the session contains not only the user history as state but also:

The recommended product

The selected product

The catalog items chosen by the agent

The purchase history

All of these are built on top of the user history, allowing every agent to have access to all variables and stay updated with every output of each agent.

The Catalog Agent justifies why the user should choose each product.
Then the user selects one product, which is added to the session state.
Finally, the Purchase Agent simulates and adds this transaction to the purchase variable in the session state and appends the purchased product to the user history.

Here are the outputs of the agents in sequence:

───────────────────────────────
the recommendation agent processing
The recommended product is: Smartwatch
The justification is: Based on your purchase history, you've shown interest in both electronics (Bluetooth headphones) and fitness (running shoes). A smartwatch combines these interests by providing features like fitness tracking, heart rate monitoring, and smartphone connectivity, making it a suitable recommendation.
───────────────────────────────

Catalog Agent is now searching for similar items...

Matching Catalog Items:
1. Wireless Headphones - Electronics ($149.99)
2. Smartwatch - Wearables ($199.99)
3. Tablet - Electronics ($299.99)

I recommend the 'Wireless Headphones'. They offer premium noise-cancellation and top-notch sound quality, enhancing your audio experience significantly. Given the excellent reviews and the 15% discount, they provide great value and are a worthwhile investment for anyone who enjoys music, podcasts, or audiobooks on the go. Its audio performance makes it a standout choice in its price range.

Enter the number of the product you want to purchase (1-3): 2

You selected: {'product': 'Smartwatch', 'category': 'Wearables', 'price': 199.99}
───────────────────────────────

Processing simulated purchase...

Purchase agent processing:
Okay, I'm processing your purchase of the Smartwatch from the Wearables category, priced at $199.99.

...Purchase complete!

The purchase was successful. I've updated your purchase history.

User History is 

{'product': 'Bluetooth headphones', 'category': 'electronics', 'price': 120}
{'product': 'Running shoes', 'category': 'sportswear', 'price': 80}
{'product': 'Smartwatch', 'category': 'Wearables', 'price': 199.99}
───────────────────────────────