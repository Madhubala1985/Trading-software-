import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint

class PairTrader:
    def __init__(self, series_x, series_y, window=100, z_thresh=2.0):
        """
        series_x/y: historical price lists for two assets
        window: lookback for ratio/z-score
        z_thresh: z-score threshold to open trades
        """
        self.window = window
        self.z_thresh = z_thresh
        self.prices_x = pd.Series(series_x)
        self.prices_y = pd.Series(series_y)

    def zscore(self, spread):
        return (spread - spread.mean()) / spread.std()

    def signal(self, price_x, price_y):
        # update series
        self.prices_x = self.prices_x.append(pd.Series([price_x]), ignore_index=True).iloc[-self.window:]
        self.prices_y = self.prices_y.append(pd.Series([price_y]), ignore_index=True).iloc[-self.window:]
        
        if len(self.prices_x) < self.window:
            return None
        
        # ratio and z-score
        ratio = np.log(self.prices_x) - np.log(self.prices_y)
        z = self.zscore(ratio)
        latest_z = z.iloc[-1]

        if latest_z > self.z_thresh:
            return 'SELL_PAIR'  # short X, long Y
        if latest_z < -self.z_thresh:
            return 'BUY_PAIR'   # long X, short Y
        return 'HOLD'
