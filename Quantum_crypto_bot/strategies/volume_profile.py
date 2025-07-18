class VolumeProfile:
    def __init__(self, bucket_size=1.0):
        self.buckets = {}            # price_bucket -> cumulative qty
        self.bucket_size = bucket_size

    def update(self, price, qty):
        bucket = round(price / self.bucket_size) * self.bucket_size
        self.buckets[bucket] = self.buckets.get(bucket, 0.0) + qty

    def poc(self):
        """Point of Control: price bucket with highest volume."""
        if not self.buckets:
            return None
        return max(self.buckets, key=self.buckets.get)

def volume_profile_signal(trade_msg, vp: VolumeProfile, threshold=1.0):
    """
    Mean-reversion around the POC of the volume profile.
    
    Args:
        trade_msg: dict with 'p' (price) and 'q' (qty)
        vp: instance of VolumeProfile
        threshold: price distance from POC to trigger (in same units as price)
    
    Returns:
        'SELL' if price > POC + threshold,
        'BUY'  if price < POC - threshold,
        else 'HOLD'
    """
    price = float(trade_msg['p'])
    qty   = float(trade_msg['q'])
    vp.update(price, qty)
    poc_price = vp.poc()
    if poc_price is None:
        return None
    if price > poc_price + threshold:
        return 'SELL'
    if price < poc_price - threshold:
        return 'BUY'
    return 'HOLD'
