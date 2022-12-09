#!/usr/bin/env python3
#helper functions for the __trading bot__ or __x___
#all helper functions explicitly related to __only__ tradeogre should be placed within "tradeogre.py" to keep things organized
#################################################################################################################################
from datetime import datetime


def generate_grid(lower_bound, upper_bound, grid_count):
	if upper_bound <= lower_bound:
		print("generate_grid(): ERROR -- upper_bound less than or equal to lower_bound -- check values.")
		return
	if grid_count <= 2:
		print("generate_grid(): ERROR -- grid_count too low -- need moar grid")
		return
	if lower_bound <= 0 or upper_bound <= 0:
		print("generate_grid(): ERROR -- lower_bound/upper_bound must be positive -- check values.")
		return
	levels = [-1]*grid_count #levels[] will store our grid pricing between lower_bound and upper_bound
	grid_spacing = ((upper_bound-lower_bound)/grid_count) #evenly space each grid between upper_bound and lower_bound with this constant
	c = lower_bound #counter variable starting @ lower-bound 
	for i in range(len(levels)): #for every item in levels....
		levels[i] = c #populate sell levels
		c = c+grid_spacing #increment the grid
	return levels
	
def flipOrderType(bs): #unusued for now - unsure if 'worth it' or just keeping logic in the loop
	if(bs == 'buy'):
		return 'sell'
	elif(bs == 'sell'):
		return 'buy'
	else:
		return 'flipOrderType(): Error'
def ticker_base_currency(bot_ticker):
	base = bot_ticker.split('-')[0] #if given 'BTC-XMR' return 'BTC'
	return base
def ticker_pair_currency(bot_ticker):
	pair = bot_ticker.split('-')[1] #if given 'BTC-XMR' return 'XMR'
	return pair
def get_time():
	dateTimeObj = datetime.now()
	timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
	return timestampStr
