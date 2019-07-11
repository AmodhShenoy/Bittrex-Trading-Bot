# Bittrex-Trading-Bot
Ping-pong bot to trade cryptocurrency through Bittrex API

### Input
This bot takes the following arguments:<br />
-ak 	:	API KEY <br />
-as 	: API SECRET <br />
-p 		:	TRADING PAIR <br />
-q 		:	QUANTITY <br />

Note: This bot works only for one ping pong cycle. 

### Logic
It takes the market ticker values and checks if the condition matches(Spread is larger than 0.25%).
If it does, it places a buy limit, and waits for it to be filled.
Then it displays the balance.
Once it reaches this point, it places a sell limit for the same quantity and again, waits for fulfillment.
