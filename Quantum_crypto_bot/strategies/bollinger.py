import pandas as pd

def bollinger_band(prices, period=20, num_std=2):
    if len(prices) < period:
        return None
    df = pd.DataFrame(prices, columns=['price'])
    rolling_mean = df['price'].rolling(window=period).mean()
    rolling_std = df['price'].rolling(window=period).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    last_price = df['price'].iloc[-1]
    if last_price > upper_band.iloc[-1]:
        return 'SELL'
    elif last_price < lower_band.iloc[-1]:
        return 'BUY'
    else:
        return 'HOLD'
