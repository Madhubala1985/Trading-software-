def iceberg_detector_signal(trade_msg, order_book_msg, size_threshold=50):
    """
    Detect iceberg trades: large trades that exceed visible depth at that price.
    
    Args:
        trade_msg: dict with 'p' (price) and 'q' (qty) from trade socket
        order_book_msg: dict with 'bids' & 'asks' lists of [price, qty]
        size_threshold: minimum trade size to consider (e.g. 50 units)
    
    Returns:
        'BUY' if large hidden bid detected,
        'SELL' if large hidden ask detected,
        else 'HOLD'
    """
    price = float(trade_msg['p'])
    qty   = float(trade_msg['q'])
    if qty < size_threshold:
        return 'HOLD'

    # Find visible size at this price
    visible = 0.0
    for side in ('bids', 'asks'):
        for p_str, q_str in order_book_msg.get(side, []):
            if float(p_str) == price:
                visible += float(q_str)

    # If trade qty > visible, it's likely an iceberg
    if visible and qty > visible:
        # If it hit the bid side, it's selling into bids → SELL signal
        # If it hit the ask side, it's buying into asks → BUY signal
        # We approximate by comparing price to mid-price
        best_bid = float(order_book_msg['bids'][0][0])
        best_ask = float(order_book_msg['asks'][0][0])
        mid = (best_bid + best_ask) / 2
        return 'SELL' if price <= mid else 'BUY'

    return 'HOLD'
