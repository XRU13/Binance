from binance.client import Client
from binance.exceptions import BinanceAPIException
from time import sleep
import pandas as pd
import keys
import ta

client = Client(keys.api_key, keys.api_secret)


def klines(symbol):
    try:
        df = pd.DataFrame(client.get_historical_klines(symbol, '1m', '40m UTC'))
    except BinanceAPIException as e:
        print(e)
        sleep(60)
        df = pd.DataFrame(client.get_historical_klines(symbol, '1m', '40m UTC'))

    df = df.iloc[:, :6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df


def strategy(symbol, qty, open_position=True):
    while True:
        buy_price = 0
        df = klines(symbol)
        if not open_position:
            if ta.trend.macd_diff(df.Close).iloc[-1] > 0 and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
                order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                print(order)
                open_position = True
                buy_price = float(order['fills'][0]['price'])
                print(buy_price)
                break
        else:
            while True:
                df = klines(symbol)
                if ta.trend.macd_diff(df.Close).iloc[-1] < 0 and ta.trend.macd_diff(df.Close).iloc[-2] > 0:
                    order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                    print(order)
                    sell_price = float(order['fills'][0]['price'])
                    open_position = False
                    print(f'profit = {(sell_price - buy_price) / buy_price}')
                    break


strategy('ALGOUSDT', qty=0)
