class VWAPCalculator:
    def __init__(self):
        self.cum_pq = 0.0
        self.cum_q  = 0.0

    def update(self, price, qty):
        self.cum_pq += price * qty
        self.cum_q  += qty

    def vwap(self):
        return (self.cum_pq / self.cum_q) if self.cum_q else None

def vwap_signal(trade_msg, vwap_calc, threshold=0.002):
    """
    Signal on price’s deviation from VWAP.
    
    Args:
        trade_msg: dict with 'p' (price) and 'q' (qty)
        vwap_calc: an instance of VWAPCalculator
        threshold: fraction, e.g. 0.002 = 0.2%
    
    Returns:
        'SELL' if price > VWAP*(1+threshold),
        'BUY'  if price < VWAP*(1-threshold),
        else 'HOLD'
    """
    price = float(trade_msg['p'])
    qty   = float(trade_msg['q'])
    vwap_calc.update(price, qty)
    v = vwap_calc.vwap()
    if v is None:
        return None
    if price > v * (1 + threshold):
        return 'SELL'
    if price < v * (1 - threshold):
        return 'BUY'
    return 'HOLD'
