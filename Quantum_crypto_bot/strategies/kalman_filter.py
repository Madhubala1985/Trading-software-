import numpy as np

class KalmanMeanReverter:
    def __init__(self, R=0.01, Q=1e-5):
        """
        R: observation noise covariance
        Q: process noise covariance
        """
        self.R = R
        self.Q = Q
        self.x = None  # state estimate (mean price)
        self.P = 1.0   # estimate covariance

    def signal(self, price, entry_z=1.5):
        """
        price: new observed price
        entry_z: z-score threshold to trade
        Returns BUY/SELL/HOLD
        """
        if self.x is None:
            self.x = price
            return None

        # Prediction update
        P_pred = self.P + self.Q

        # Measurement update
        K = P_pred / (P_pred + self.R)
        self.x = self.x + K * (price - self.x)
        self.P = (1 - K) * P_pred

        # z-score
        z = (price - self.x) / np.sqrt(self.P)

        if z > entry_z:
            return 'SELL'
        if z < -entry_z:
            return 'BUY'
        return 'HOLD'
