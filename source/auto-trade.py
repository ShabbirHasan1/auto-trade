import datetime
import pandas as pd
import requests
from API_functions import *

def three_rule_trade(symbol,cash_buying_power_fraction, trade_type='paper'):
    # The stock that will be traded
    if "." in symbol or '^' in symbol or '/' in symbol: # remove invalid characters
        return
    elif symbol in ["CTL", "CXO", "ETFC", "MYL", "NBL", "TIF", "VAR",
                    "AAC", "ACAHW", 'ACII', 'ADEX', 'ADRA', 'AGNCP', 'ANAC',
                    'ANDAR', "ASAI", 'ATAQ', 'AUS', 'FLIR']: # Stocks without historical data
        return
    traded_symbol = symbol
    buy_count = 0
    sell_count = 0
    trade_list = []
    print(f"################## Begin analysis of {traded_symbol} ###################")
    # Find ticker's seven day low and most recent close

        # Get today's date and seven calenday days ago TODO: exclude weekends from data
    current_time_extended = datetime.datetime.now().isoformat() # looks like '2010-08-03T03:00:00.000000'
    today = current_time_extended[:10]
    subtractable_time = datetime.datetime.now()
    sevenDaysAgo = subtractable_time - datetime.timedelta(days=9)
    a_while_ago = sevenDaysAgo.isoformat()[:10]

        # Gather the data for the stock that will be traded

    bump = 1.005 # Correction to solve problem of hardly any trades taking place.
    # The notion is that this will decrease the price at which a purchase will be made.
    # the idea here is that we are calibrating the hunch that a current price being below the seven day low
    # means that it's a good buying point. This could be true for a higher number of stocks that have a more
    # granular curve than can be sampled by a 7 day low.

    myHistoricalTickerData = EOD_historical_data(traded_symbol, today, sevenDaysAgo)
    ticker_seven_day_low = bump*myHistoricalTickerData.min(axis=0)['Close']
    current_closing_price = iex_api(traded_symbol)['previousClose']



    print(f'Bumped seven day low for {traded_symbol} = {ticker_seven_day_low}')
    print(f'Most recent closing price for {traded_symbol} = {current_closing_price}')

    # repeat the process for the SPY index to
    # retrieve market 200 day moving average

    market_symbol = 'SPY'
    market_iex_data = iex_api(market_symbol)

    twoHundredDaysAgo = subtractable_time - datetime.timedelta(days=200)
    market_myHistoricalTickerData = EOD_historical_data(market_symbol, today, twoHundredDaysAgo)
    market_two_hundred_day_average = market_myHistoricalTickerData.mean(axis=0)['Close']
    market_current_closing_price = market_iex_data['previousClose']
    print(f'Two hundred day average {market_symbol} = {market_two_hundred_day_average}')
    print(f'Most recent closing price for {market_symbol} = {market_current_closing_price}')

    # Find the market seven daying closing low

    market_myHistoricalTickerData = EOD_historical_data(market_symbol, today, sevenDaysAgo)
    market_seven_day_low = market_myHistoricalTickerData.min(axis=0)['Close']
    print(f'seven day low for {market_symbol} = {market_seven_day_low}')

    # Now trade the stock based on the following rules

    # Show my alpaca account status

    # get_account_status()
    # determine how much of the marginal stock I will buy based on trading budget
    myBudget = float(get_account_status(trade_type='live')['buying_power'])
    fractions_to_trade = cash_buying_power_fraction*myBudget/current_closing_price

    print(f" Alloting {cash_buying_power_fraction*100} percent of my portfolio of {myBudget} to consider buying {fractions_to_trade} of {traded_symbol}")
        #The strategy buys when the current closing price on daily time frame closes below the previous
        #Seven day low and the market is above its 200 day mvoing average.
    import math

    if (current_closing_price < ticker_seven_day_low) and (market_current_closing_price > market_two_hundred_day_average):
        print(f"$$$$$$$$$$$$$$$$$$ Initiating purchase of about {fractions_to_trade} units of {traded_symbol} securities")
        if myBudget > 0.00:
            place_trade(traded_symbol,fractions_to_trade, #todo: If I already own it don't buy it again.
                    trade_type=trade_type,
                    direction='buy')
        else:
            print("Insufficient funds, trade not made.")
    # elif market_current_closing_price < 1.0*market_seven_day_low: # Don't sell based on the same fraction. Sell all of it.
    #     print(f"$$$$$$$$$$$$$$$$$$ Initiating sale of {fractions_to_trade} units of {traded_symbol} securities")
    #     try:
    #         fractions_to_trade = float(get_symbol_position(traded_symbol)['qty'])
    #         place_trade(traded_symbol,fractions_to_trade,
    #                 trade_type=trade_type,
    #                 direction='sell')
    #     except: print("Warning: Position not held in alpaca, can not sell")
    else:
        print("##################  Rules not met, no trades made ####################")

if __name__ == '__main__':
    # Iterate through my portfolio of stocks
    # Source: https://stockstotrade.com/stocks-to-watch/
    # my_favorite_companies = ['GOOGL', 'CSCO','HMHC', 'LOW', 'NUE','RCON','TGT','X']
    my_favorite_companies = gather_SPY_stock_names()[0].split(',')
    NASDAQ_Companies = gather_NASDAQ_stock_names()[0].split(',')
    print(f'Companies being traded {my_favorite_companies}')
    portion_of_cash_to_spend = 10/100
    print(f" Trading {len(my_favorite_companies)} companies and spending {portion_of_cash_to_spend*100} percent"
          f" of my cash buying power on each")
    while True:
        for company in my_favorite_companies:
            three_rule_trade(company, portion_of_cash_to_spend,trade_type='live')
        #todo: Better tracking of sales and purchases. Hard to know what's going on right now with the output. 
        for company in NASDAQ_Companies:
            try:
                three_rule_trade(company, portion_of_cash_to_spend,trade_type='live')
            except:
                pass