def liquidity_trap_signal(order_book, threshold=100):
    """
    Detect liquidity traps by summing bid/ask sizes in small price buckets.
    
    Args:
        order_book: dict with 'bids' and 'asks', each is list of [price, qty]
        threshold: minimum size to consider a liquidity cluster
    
    Returns:
        'BUY' if strong bid cluster detected (support),
        'SELL' if strong ask cluster detected (resistance),
        else 'HOLD'
    """

    def cluster_size(orders, bucket_size=0.5):
        clusters = {}
        for price_str, qty_str in orders:
            price = float(price_str)
            qty = float(qty_str)
            bucket = round(price / bucket_size) * bucket_size
            clusters[bucket] = clusters.get(bucket, 0) + qty
        return clusters

    bid_clusters = cluster_size(order_book.get('bids', []))
    ask_clusters = cluster_size(order_book.get('asks', []))

    max_bid_bucket = max(bid_clusters, key=bid_clusters.get, default=0)
    max_ask_bucket = max(ask_clusters, key=ask_clusters.get, default=0)

    max_bid_qty = bid_clusters.get(max_bid_bucket, 0)
    max_ask_qty = ask_clusters.get(max_ask_bucket, 0)

    if max_bid_qty > threshold and max_bid_qty > max_ask_qty:
        return 'BUY'
    elif max_ask_qty > threshold and max_ask_qty > max_bid_qty:
        return 'SELL'
    else:
        return 'HOLD'
