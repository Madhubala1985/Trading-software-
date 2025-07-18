from datetime import datetime, timedelta

LAST_SPIKE_TIME = None

def news_spike_signal(sentiment_score, spike_threshold=0.8, cooldown=300):
    """
    Generate signal on sudden sentiment spike.
    
    Args:
        sentiment_score: float between -1 (very negative) and +1 (very positive)
        spike_threshold: minimum abs change to count as a spike
        cooldown: seconds to wait before next trade
    
    Returns:
        'BUY' if sentiment_score > spike_threshold
        'SELL' if sentiment_score < -spike_threshold
        else 'HOLD'
    """
    global LAST_SPIKE_TIME
    now = datetime.utcnow()
    if LAST_SPIKE_TIME and (now - LAST_SPIKE_TIME).total_seconds() < cooldown:
        return 'HOLD'
    if sentiment_score > spike_threshold:
        LAST_SPIKE_TIME = now
        return 'BUY'
    if sentiment_score < -spike_threshold:
        LAST_SPIKE_TIME = now
        return 'SELL'
    return 'HOLD'
