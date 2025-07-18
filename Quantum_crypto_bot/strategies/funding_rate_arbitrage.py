def funding_rate_arbitrage_signal(funding_rate, price_trend, rate_threshold=0.001):
    """
    Trade based on funding rate spikes vs. spot trend.
    
    Args:
        funding_rate: current funding rate (e.g. 0.0005 for +0.05%)
        price_trend: recent price trend metric (e.g. 1 if up, -1 if down)
        rate_threshold: minimum absolute rate to consider
    
    Returns:
        'BUY' if funding_rate < -rate_threshold and price_trend > 0
        'SELL' if funding_rate > rate_threshold and price_trend < 0
        else 'HOLD'
    """
    if funding_rate is None or abs(funding_rate) < rate_threshold:
        return 'HOLD'
    if funding_rate < -rate_threshold and price_trend > 0:
        return 'BUY'
    if funding_rate > rate_threshold and price_trend < 0:
        return 'SELL'
    return 'HOLD'
