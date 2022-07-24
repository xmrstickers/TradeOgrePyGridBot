#!/usr/bin/env python3
import requests #for making API requests
import tradeogre #import tradeogre.py to use TradeOgre() class
#-------------------------------------------------------------
# please be careful not to spam TO's API endpoint -- code delays between requests if they do not alter functional performance to avoid rate-limiting
#-------------------------------------------------------------
trade_ogre = tradeogre.TradeOgre() #make Object
trade_ogre.load_key("/home/user/Desktop/TradeOgreDev/TradeOgre.key") #load API keys
#---examples of API usage/output:----
print(trade_ogre.ticker('BTC-XMR')) #'intial price'(?), price, 24h-high, 24h-low, volume, bid, ask 
print(trade_ogre.order_book('BTC-XMR')) #shows first page of bid/ask order depth 
print(trade_ogre.orders('BTC-XMR')) #uuid, date(unix), type(buy/sell), price, quantity, market 
print(trade_ogre.sell('BTC-XMR', 0.1, 0.0069)) #sell 0.1 monero @ a rate of 0.0069 BTC/XMR - returns uuid
print(trade_ogre.balance('XMR')) #shows account balance of specific asset -- account API key required 
print(trade_ogre.balances()) #shows total account balance -- account API key required 
#-----------------------------------
