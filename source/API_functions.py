import requests
import pandas as pd
import datetime

from polygon import RESTClient

# Allows us to convert timestamps to datetime format
def ts_to_datetime(ts) -> str:
    return datetime.datetime.fromtimestamp(ts / 1000.0).strftime('%Y-%m-%d %H:%M')

base_url = r"https://api.alpaca.markets/v2/"
API_key_dict = {
    'live':
        {"APCA-API-KEY-ID": "my key",
        "APCA-API-SECRET-KEY": "my secret key"},
    'paper':
        {"APCA-API-KEY-ID": "my key",
        "APCA-API-SECRET-KEY": "my secret key"},
}

def get_symbol_position(symbol,trade_type='paper'):

    paper_boolean = ''
    if trade_type == 'paper':
        paper_boolean = 'paper-'
    url = f"https://{paper_boolean}api.alpaca.markets/v2/positions/{symbol}"

    response = requests.get(url, headers=API_key_dict[trade_type])
    print(response.json())
    return response


def get_account_status(trade_type='paper'):
    paper_boolean = ''
    if trade_type == 'paper':
        paper_boolean = 'paper-'
    url = f"https://{paper_boolean}api.alpaca.markets/v2/account"

    response = requests.get(url,headers=API_key_dict[trade_type])
    print("Alpaca API Status code: " + str(response.status_code))
    # print(response.json())
    return response.json()

def get_symbol_info(symbol):
    endpoint = 'https://api.alpaca.markets/v2/assets/'
    response = requests.get(endpoint + symbol, headers=API_key_dict)
    print(response.json())
    return response

def place_trade(symbol, fraction_of_stock,trade_type='paper',direction='buy'):
    import json
    paper_boolean = ''
    if trade_type == 'paper':
        paper_boolean = 'paper-'
    url = f"https://{paper_boolean}api.alpaca.markets/v2/orders"
    import math
    if fraction_of_stock > 1:
        fraction_of_stock = math.floor(fraction_of_stock)
    payload = json.dumps({
        "symbol": symbol,
        "qty": fraction_of_stock,
        "side": direction,
        "type": "market",
        "time_in_force": "day"
    })
    headers = {
        **API_key_dict[trade_type],
        'Content-Type': 'application/json',
        'Cookie': '__cfduid=d110fb04d25dd6f054f0e4887ee45d7831619350798'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def price_info(symbol):
    key = ""

    # RESTClient can be used as a context manager to facilitate closing the underlying http session
    # https://requests.readthedocs.io/en/master/user/advanced/#session-objects
    with RESTClient(key) as client:
        from_ = "2020-05-01"
        to = "2021-02-01"
        resp = client.stocks_equities_aggregates(symbol, 1, "day", from_, to, unadjusted=False)

        print(f"Day aggregates for {resp.ticker} between {from_} and {to}.")

        for result in resp.results:
            dt = ts_to_datetime(result["t"])
            print(f"{dt}\n\tO: {result['o']}\n\tH: {result['h']}\n\tL: {result['l']}\n\tC: {result['c']} ")

def polygon_web_socket():
    import time

    from polygon import WebSocketClient, STOCKS_CLUSTER

    def my_custom_process_message(message):
        print("this is my custom message processing", message)

    def my_custom_error_handler(ws, error):
        print("this is my custom error handler", error)

    def my_custom_close_handler(ws):
        print("this is my custom close handler")

    def main():
        key = ''
        my_client = WebSocketClient(STOCKS_CLUSTER, key, my_custom_process_message)
        my_client.run_async()

        my_client.subscribe("T.MSFT", "T.AAPL", "T.AMD", "T.NVDA")
        time.sleep(1)

        my_client.close_connection()

    if __name__ == "__main__":
        main()

def yahoo_finance_approach():
    import requests

    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/auto-complete"

    querystring = {"q": "tesla", "region": "US"}

    headers = {
        'x-rapidapi-key': "",
        'x-rapidapi-host': ""
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)

def EOD_historical_data(symbol, today, pastDate):
    exchange_id = 'US'
    api_token = ''
    url = f'https://eodhistoricaldata.com/api/eod/{symbol}.{exchange_id}' \
          f'?from={pastDate}&to={today}&api_token={api_token}'
    response = requests.get(url)
    # print(response.text)
    import pandas, io
    data = io.StringIO(response.text)
    myCVasDF = pandas.read_csv(data, sep=',')
    return myCVasDF

def iex_api(symbol):
    from starter_files.secrets import IEX_CLOUD_API_TOKEN
    api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
    iex_data = requests.get(api_url).json()
    return iex_data
# Function sourced from
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def gather_SPY_stock_names():
    stocks = pd.read_csv('../../../sp_500_stocks.csv')
    print(stocks)
    symbol_groups = list(chunks(stocks['Ticker'], 505))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))
        print(symbol_strings[i])
    return symbol_strings

def gather_NASDAQ_stock_names():
    stocks = pd.read_csv('../../../nasdaq_screener_1619729271011.csv')
    print(stocks)
    symbol_groups = list(chunks(stocks['Symbol'], 10000))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))
        print(symbol_strings[i])
    return symbol_strings

if __name__ == '__main__':
    # get_account_status()
    # get_symbol_position('GOOGL')
    gather_NASDAQ_stock_names()
    # place_trade('GOOGL',0.001)
    # polygon_web_socket()
    # yahoo_finance_approach()
    #EOD_historical_data('GOOGL')
