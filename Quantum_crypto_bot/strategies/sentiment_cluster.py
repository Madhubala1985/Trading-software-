import numpy as np

class SentimentCluster:
    def __init__(self, window=20):
        self.scores = []
        self.window = window

    def update(self, sentiment_score):
        self.scores.append(sentiment_score)
        if len(self.scores) > self.window:
            self.scores.pop(0)

    def cluster_strength(self):
        if len(self.scores) < self.window:
            return 0
        return np.std(self.scores)

def sentiment_cluster_signal(sentiment_score, volatility, cluster: SentimentCluster, 
                             vol_threshold=0.02, cluster_threshold=0.3):
    """
    Combines sentiment clustering with volatility spike.
    
    Args:
        sentiment_score: latest sentiment (-1 to +1)
        volatility: recent price volatility (e.g., std of returns)
        cluster: SentimentCluster instance
        vol_threshold: minimum volatility to require
        cluster_threshold: minimum sentiment STD to require
    
    Returns:
        'BUY' if sentiment_score > 0 and both thresholds met
        'SELL' if sentiment_score < 0 and both thresholds met
        else 'HOLD'
    """
    cluster.update(sentiment_score)
    strength = cluster.cluster_strength()
    if volatility < vol_threshold or strength < cluster_threshold:
        return 'HOLD'
    return 'BUY' if sentiment_score > 0 else 'SELL'
