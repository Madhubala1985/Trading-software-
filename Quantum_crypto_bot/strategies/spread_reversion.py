def spread_reversion_signal(order_book, spread_threshold=0.5):
    """
    Mean-reversion based on bid–ask spread.
    
    Args:
        order_book: dict with 'bids' and 'asks', each a list of [price, qty]
        spread_threshold: absolute spread (in price units) above which to trade
    
    Returns:
        'BUY' if spread > threshold and price near bid (expect spread to narrow),
        'SELL' if spread > threshold and price near ask,
        else 'HOLD'
    """
    bids = order_book.get('bids', [])
    asks = order_book.get('asks', [])
    if not bids or not asks:
        return 'HOLD'

    best_bid = float(bids[0][0])
    best_ask = float(asks[0][0])
    spread = best_ask - best_bid

    if spread < spread_threshold:
        return 'HOLD'

    # If price currently near bid, buy expecting rebound; vice versa
    mid = (best_bid + best_ask) / 2
    return 'BUY' if mid - best_bid < spread / 2 else 'SELL'
