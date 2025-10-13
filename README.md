Phase one the agent sees the History and get the recommended product from it and justify.
using structed output putting product and justification in json and printing it like this:

The recommended product is: Smartwatch
The justification is: Based on your purchase history, you've shown interest in both electronics (Bluetooth headphones) and sportswear (Running shoes). A smartwatch combines these interests by offering fitness tracking features and connectivity for your phone. Given your previous purchases were in the price range of $80-$120, a smartwatch would likely be a suitable purchase.
---------------------------------------------------------------------------------------------------------------------------------------------------
Phase two is to load catalog from this endpoint "https://fake-store-api.mock.beeceptor.com/api/products" that return products.
then search for the recommended product in this catalog with condition that it has the same price range.