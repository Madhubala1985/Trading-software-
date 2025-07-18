import pandas as pd

def moving_average_crossover(prices, fast=10, slow=21):
    if len(prices) < slow:
        return None
    df = pd.DataFrame(prices, columns=['price'])
    df['fast_ma'] = df['price'].rolling(window=fast).mean()
    df['slow_ma'] = df['price'].rolling(window=slow).mean()
    if df['fast_ma'].iloc[-2] < df['slow_ma'].iloc[-2] and df['fast_ma'].iloc[-1] > df['slow_ma'].iloc[-1]:
        return 'BUY'
    if df['fast_ma'].iloc[-2] > df['slow_ma'].iloc[-2] and df['fast_ma'].iloc[-1] < df['slow_ma'].iloc[-1]:
        return 'SELL'
    return 'HOLD'
