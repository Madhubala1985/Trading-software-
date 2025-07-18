import pandas as pd

def rsi(prices, period=14):
    if len(prices) < period:
        return None
    df = pd.DataFrame(prices, columns=['price'])
    delta = df['price'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    rsi_val = 100 - (100 / (1 + rs))
    latest = rsi_val.iloc[-1]
    if latest > 70:
        return 'SELL'
    elif latest < 30:
        return 'BUY'
    else:
        return 'HOLD'
