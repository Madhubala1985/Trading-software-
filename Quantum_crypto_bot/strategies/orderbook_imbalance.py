def orderbook_imbalance_signal(order_book, top_n=5, imbalance_threshold=0.6):
    """
    Generate BUY/SELL/HOLD based on top-N order-book imbalance.
    
    Args:
        order_book: dict with 'bids' and 'asks', each is list of [price, qty]
        top_n: number of price levels on each side to consider
        imbalance_threshold: fraction above which an imbalance is significant (0.5–1.0)
    
    Returns:
        'BUY' if bid_pressure > imbalance_threshold,
        'SELL' if ask_pressure > imbalance_threshold,
        else 'HOLD'
    """
    # Sum sizes at top N levels
    total_bid = sum(float(qty) for _, qty in order_book.get('bids', [])[:top_n])
    total_ask = sum(float(qty) for _, qty in order_book.get('asks', [])[:top_n])
    total = total_bid + total_ask

    if total == 0:
        return 'HOLD'

    bid_pressure = total_bid / total
    ask_pressure = total_ask / total

    if bid_pressure > imbalance_threshold:
        return 'BUY'
    elif ask_pressure > imbalance_threshold:
        return 'SELL'
    else:
        return 'HOLD'
