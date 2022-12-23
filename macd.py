from binance.client import Client
import keys
import matplotlib.pyplot as plt
import pandas as pd

client = Client(keys.api_key, keys.api_secret)

coin = pd.DataFrame(client.get_historical_klines('ETHUSDT', '1d', "120 day ago UTC"))


def get_frame_macd(base_coin):
    frame = base_coin.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame = frame.astype(float)
    frame['EMA12'] = frame['Close'].ewm(span=12, adjust=False).mean()
    frame['EMA26'] = frame['Close'].ewm(span=26, adjust=False).mean()
    frame['MACD'] = frame.EMA12 - frame.EMA26
    frame['signal'] = frame.MACD.ewm(span=9).mean()
    plt.plot(frame.signal, label='signal', color='red')
    plt.plot(frame.MACD, label='MACD', color='green')
    plt.legend()
    plt.show()
    print('Indicators added')
    buy, sell = [], []
    for i in range(2, len(frame)):
        if frame.MACD.iloc[i] > frame.signal.iloc[i] and frame.MACD.iloc[i - 1] < frame.signal.iloc[i - 1]:
            buy.append(i)
        elif frame.MACD.iloc[i] < frame.signal.iloc[i] and frame.MACD.iloc[i - 1] > frame.signal.iloc[i - 1]:
            sell.append(i)

    plt.figure(figsize=(12, 4))
    plt.scatter(frame.iloc[buy].index, frame.iloc[buy].Close, marker='^', color='green')
    plt.scatter(frame.iloc[sell].index, frame.iloc[sell].Close, marker='v', color='red')
    plt.plot(frame.Close, label='ETHUSDT', color='black')
    plt.legend()
    plt.show()

    real_buy = [i + 1 for i in buy]
    real_sells = [i + 1 for i in sell]

    buy_prices = frame.Open.iloc[real_buy]
    sell_prices = frame.Open.iloc[real_sells]

    if sell_prices.index[0] < buy_prices.index[0]:
        sell_prices = sell_prices.drop(sell_prices.index[0])
    elif buy_prices.index[-1] > sell_prices.index[-1]:
        buy_prices = buy_prices.drop(buy_prices.index[-1])

    profit = []
    for i in range(len(sell_prices)):
        profit.append((sell_prices.array[i] - buy_prices.array[i]) / buy_prices.array[i])

    print(sum(profit))


get_frame_macd(coin)



