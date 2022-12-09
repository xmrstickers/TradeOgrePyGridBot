#!/usr/bin/env python3

#This work is devoted to God.

#This is free and unencumbered work released into the public domain.

#Anyone is free to copy, modify, publish, use, compile, sell, or
#distribute this work, either in source code form or as a compiled
#binary, for any purpose, commercial or non-commercial, and by any
#means.

#In jurisdictions that recognize copyright laws, the author or authors
#of this work dedicate any and all copyright interest in the
#work to the public domain. We make this dedication for the benefit
#of the public at large and to the detriment of our heirs and
#successors. We intend this dedication to be an overt act of
#relinquishment in perpetuity of all present and future rights to this
#work under copyright law.

#THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR
#OTHER DEALINGS IN THE WORK.

#For more information, please refer to <https://unlicense.org>


import requests #for making API requests
import time #for delay in the loop
import tradeogre #import tradeogre.py to use TradeOgre() API class
from funcs import * #import all(*) of our functions from funcs.py
#-------------------------------------------------------------
# market-making bot 
# starts at the lower bound 100% weighted in the currency pair -- does not force rebalance like kucoin and others
# in other words, for example, the bot starts as 100% sell on XMR given BTC-XMR as the input pair and only requires XMR to start. AKA "bullish bias" 
# 
#ghetto API -- specify currency pair(bot_ticker), api key file path(uri), buffer, upper-bound, bot_balance, and grid-count
#
#-------------------------------------------------------------
#------------------------------------#
#---examples of API usage/output:----
#print(trade_ogre.ticker('BTC-XMR')) #'intial price'(?), price, 24h-high, 24h-low, volume, bid, ask 
#print(trade_ogre.order_book('BTC-XMR')) #shows first page of bid/ask order depth 
#print(trade_ogre.order('aeb3b137-1178-2715-b20c-8255e8aecf41')) #look up specific order by UUID
#print(trade_ogre.cancel('aeb3b137-1178-2715-b20c-8255e8aecaf41')) #cancel order by UUID - or .... .
#print(trade_ogre.cancel('all')) #... set UUID='all' and cancel all active orders
#print(trade_ogre.orders('BTC-XMR')) #uuid, date(unix), type(buy/sell), price, quantity, market 
#print(trade_ogre.buy('BTC-XMR', 0.1, 0.00696969)) #buy 0.1 monero @ a rate of 0.0069 BTC/XMR - returns uuid 
#print(trade_ogre.sell('BTC-XMR', 0.1, 0.00696969)) #sell 0.1 monero @ a rate of 0.0069 BTC/XMR - returns uuid 
#print(trade_ogre.balance('XMR')) #shows account balance of specific asset -- account API key required 
#print(trade_ogre.balances()) #shows total account balance -- account API key required 
#-----------------------------------#

bot_ticker = 'BTC-XMR' #the market pair as denoted in the tradeogre URL (ex: tradeogre.com/exchange/BTC-XMR    bot_ticker =  'BTC-XMR'
bot_balance = 1 #amount of <pair> the bot should use when trading BTC-<pair> e.g. 1 XMR 
api_file_uri = '/home/boop/Desktop/TradeOgreDev/TradeOgre.key' #api key - required (key and secret on line 1/2)
buffer = 0.000005 # buffer between ask price and the first sell-order in the grid -- varies greatly based on pair - maybe implement %? 
upper_bound = 0.0073 #lower_bound defaults to ask price + buffer
grid_count = 6 #number of trades to use total
bot_trade_size = (bot_balance/grid_count) #e.g. if the total amount to trade is 1 XMR and the grid count is 5, each sell will be 0.2 XMR each

#-------------------------------------------------------------
# 
#-------------------------------------------------------------
trade_ogre = tradeogre.TradeOgre() #make Object
trade_ogre.load_key(api_file_uri) #load API keys

print(get_time()+" -- Bot Started - TradeOgre() initialized --")
#print(trade_ogre.sell('BTC-XMR', 0.1, 0.00696969))
ticker_raw_json = trade_ogre.ticker(bot_ticker) #initialize market-data
#print("raw JSON:")
#print(ticker_raw_json)
init_price = float(ticker_raw_json['price']) #last-traded price 
init_ask = float(ticker_raw_json['ask']) #lowest ask
init_bid = float(ticker_raw_json['bid']) #highest bid 
init_24high = float(ticker_raw_json['high']) #24h price
init_24low = float(ticker_raw_json['low']) #24h low price
time.sleep(1)
init_btc_balance = trade_ogre.balance(ticker_base_currency(bot_ticker))['available']
time.sleep(1)
init_pair_balance = trade_ogre.balance(ticker_pair_currency(bot_ticker))['available'] 

num_trades = 0 #how many swaps we have done _after_ the initial 

lower_bound = (init_ask+buffer) #defaults to ask price + buffer


print("-- Pair: "+str(bot_ticker)+" --")
print("-- Creating "+str(grid_count)+" trades @ "+str(bot_trade_size)+" each for total of "+str(bot_balance)+" "+ticker_pair_currency(bot_ticker)+" for sale --")
print("-- "+ticker_base_currency(bot_ticker)+"-Available: "+str(init_btc_balance)+" - "+ticker_pair_currency(bot_ticker)+"-available: "+str(init_pair_balance)+" --")

time.sleep(2)
#open_orders_raw = trade_ogre.orders('BTC-XMR') 
#print(open_orders_raw) # DEBUG SHIT
#for i in range(len(open_orders_raw)): #print all open-order UUIDs on BTC-XMR
#	print(str(open_orders_raw[i]['uuid']))

sellgrid = generate_grid(lower_bound, upper_bound, grid_count)
grid_spacing = sellgrid[1]-sellgrid[0] #the price spread between grid-levels
orders = [-1]*grid_count  #internal order tracker (uuid)
orders_type = [-1]*grid_count  #internal order type  (buy/sell)
orders_price = [-1]*grid_count #internal order price  

open_orders = [-1]*grid_count #open orders on TradeOgre's end

for i in range(len(sellgrid)):
	print("placing sell order for "+str(bot_trade_size)+" XMR  @ "+str(sellgrid[i])+" "+bot_ticker)
	orders_type[i] = 'sell'
	orders_price[i] = sellgrid[i]
	raw_sell_json = trade_ogre.sell(bot_ticker, bot_trade_size, sellgrid[i])
	orders[i] = raw_sell_json['uuid']
	time.sleep(0.22) #avoid rate-limiting by not spamming all the sells at once

#our sells are placed -- now we must monitor for fills and then re-place and sells as buys 

print("sells placed, entering pulse-loop...")

pulse_count = 0 #every 12 pulses @ 5 seconds we will output the time 

while True:
	pulse_count += 1 #increment counter to 1min
	time.sleep(5) #avoid rate-limiting by globalist API scum
	#print("Pulsing...")
	if(pulse_count == 12): #12*5sec = 1min #TODO its delaying 75-90sec instead of expected 60
		pulse_count = 0 #reset counter
		print(get_time()+" Number of Trades: "+str(num_trades)+" - Pulsing...") #print the time every minute
	
	open_orders_raw = trade_ogre.orders(bot_ticker) #get current open orders
	#print(open_orders_raw)
	open_orders = ([-1]*(len(open_orders_raw))) #adjust open_orders length appropirately 
	for i in range(len(open_orders_raw)):
		open_orders[i] = open_orders_raw[i]['uuid'] #populate open order UUIDs...
	
	for i in range(len(orders)):
		#print("debug orders[i]-> "+str(orders[i]))
		#print("debug open_orders[i]-> "+str(open_orders[i]))
		
		if (orders[i] not in open_orders):
			print(str(orders_type[i])+" order "+str(orders[i])+" not found, assumed filled @ "+str(orders_price[i])+" -- flipping order type...")
			if(orders_type[i] == 'sell'):
				new_price = (orders_price[i]-grid_spacing)
				buy_json = trade_ogre.buy(bot_ticker, bot_trade_size, new_price) #create new buy 
				orders[i] = buy_json['uuid']
				orders_type[i] = 'buy'
				orders_price[i] = new_price
				print(str("New Order: "+orders_type[i])+" order @ "+str(orders_price[i])+" "+bot_ticker)
				num_trades += 1
			elif(orders_type[i] == 'buy'):
				new_price = (orders_price[i]+grid_spacing)
				sell_json = trade_ogre.sell(bot_ticker, bot_trade_size, new_price)
				orders[i] = sell_json['uuid']
				orders_type[i] = 'sell'
				orders_price[i] = new_price
				print(str("New Order: "+orders_type[i])+" order @ "+str(orders_price[i])+" "+bot_ticker)
				num_trades += 1	
		#else: 
			#print ("all expected UUIDs present...")
			#print(str(orders_type[i])+" order "+str(orders[i])+" found")



#print(trade_ogre.sell('BTC-XMR', 0.1, 0.0068803298765432105)) #success - truncates to 0.00688032
print(get_time()+" -- Bot Ended --")
