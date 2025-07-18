import torch
from torch import nn
import numpy as np

class TimeSeriesTransformer(nn.Module):
    """
    Example Transformer model skeleton for time-series forecasting.
    You can load your own checkpoint and fine-tune as needed.
    """

    def __init__(self, input_size=1, d_model=64, nhead=4, num_layers=2):
        super().__init__()
        self.input_proj = nn.Linear(input_size, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output_proj = nn.Linear(d_model, 1)

    def forward(self, x):
        # x: [seq_len, batch, input_size]
        x = self.input_proj(x)
        x = self.transformer(x)
        return self.output_proj(x)[-1]  # predict next point

class TransformerForecast:
    def __init__(self, model_path: str):
        self.device = torch.device('cpu')
        self.model = TimeSeriesTransformer()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def signal(self, prices: list, threshold=0.001) -> str:
        """
        Args:
            prices: list of floats, recent price series
        
        Returns:
            'BUY' if predicted change > threshold,
            'SELL' if predicted change < -threshold,
            else 'HOLD'
        """
        if len(prices) < 50:
            return 'HOLD'
        seq = torch.tensor(prices[-50:], dtype=torch.float32).view(50, 1, 1)
        with torch.no_grad():
            pred = self.model(seq.to(self.device)).item()
        change = (pred - prices[-1]) / prices[-1]
        if change > threshold:
            return 'BUY'
        if change < -threshold:
            return 'SELL'
        return 'HOLD'
