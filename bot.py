'''
This bot takes the following arguments:
-ak 	:	API KEY
-as 	: 	API SECRET
-p 		:	TRADING PAIR
-q 		:	QUANTITY

This bot works only for one ping pong cycle. 
It takes the market ticker values and checks if the condition matches(Spread is larger than 0.25%).
If it does, it places a buy limit, and waits for it to be filled.
Then it displays the balance.
Once it reaches this point, it places a sell limit for the same quantity and again, waits for fulfillment.'''



import requests
import hashlib
import time
import hmac
import argparse

def signed_request(url):
	now = time.time()
	url += '&nonce=' + str(now)
	signed = hmac.new(api_secret, url.encode('utf-8'), hashlib.sha512).hexdigest()
	#print("HASH:",signed)
	headers = {'apisign': signed}
	r = requests.get(url, headers=headers)
	return r.json()

def getMarketValues(market):
	return requests.get('https://api.bittrex.com/api/v1.1/public/getticker'+'?market='+market).json()['result']

def buy_limit(market, quantity, rate):
	url = 'https://bittrex.com/api/v1.1/market/buylimit?apikey=' + api_key + '&market=' + market + '&quantity=' + str(quantity) + '&rate=' + format_float(rate)
	return signed_request(url)

def format_float(f):
	return "%.8f" % f

def orderPending(market):
	orders = signed_request('https://api.bittrex.com/api/v1.1/market/getopenorders?apikey='+api_key+'&market='+market)
	if len(orders['result'])>0:
		return True
	else:
		return False
def printBalances():
	balances = signed_request('https://api.bittrex.com/api/v1.1/account/getbalances?apikey=',api_key)['result']
	if len(balances)>0:
		print("Your Balances are:\n")
		for curr in balances:
			print("Currency:",curr['Currency'])
			print("Balance:",curr['Balance'])
			print("Available:",curr['Available'],'\n')
	else:
		print("No Balance")
	
def main():
	#Taking all input from arguments
	global api_key
	global api_secret
	parser = argparse.ArgumentParser()
	parser.add_argument('-a','--apikey',type=str,help='API KEY goes here')
	parser.add_argument('-as','--apisecret',type=str,help='API SECRET goes here')
	parser.add_argument('-p','--tradingpair',type=str,help='Trading Pair goes here')
	parser.add_argument('-q','--quantity',type=float,help='Quantity of cryptocurrency to trade')
	args = parser.parse_args()
	api_key = args.apikey
	market = args.tradingpair
	quantity = args.quantity
	api_secret = bytes(args.apisecret,'utf-8')
	#used to keep a track of time
	start = time.time()

	print("Bot running! Searching for condition satisfaction...(max searching time is 24 hrs)")

	while time.time()<start+24*60*60:
		#getting market ticker values
		currentMarket = getMarketValues(market)
		spread = currentMarket['Ask'] - currentMarket['Bid']
		#checking for condition pass
		if spread>=0.0025 * currentMarket['Bid']:
			print("Condition satisfied!")
			print('Placing buy limit at',currentMarket['Bid'],'for quantity=',quantity)
			buyResponse = buy_limit(market,quantity,currentMarket['Bid'])

			if buyResponse['success']==True:    #if successfully placed buy limit
				print("Waiting for order fulfillment...")
				while orderPending(market):
					time.sleep(10)
				#program reaches here only if no order pending
				print("Order fulfilled! \n\n")
				printBalances()

				#placing sell limit 
				print('Placing sell limit at',currentMarket['Ask'],'for quantity=',quantity)
				sellResponse = sell_limit(market,quantity,currentMarket['Ask'])

				if sellResponse['success']==True: #if successfully places sell limit
					print("Waiting for order fulfillment...")
					while orderPending(market):
						time.sleep(10)
					#program reaches here only if no order pending
					print("Order fulfilled! \n\n")
					printBalances()
					print("\n\nPing-Pong cycle finished!")
				else:
					#sell limit not placed due to error
					print(sellResponse['message'])
			else: 
				#buy limit not placed due to error
				print(buyResponse['message'])
			break
		else:
			#condition not satisfied
			time.sleep(10)


if __name__=='__main__':
	main()
