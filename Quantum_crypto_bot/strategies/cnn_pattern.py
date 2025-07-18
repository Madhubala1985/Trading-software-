import torch
from torchvision import transforms
from PIL import Image
import io
import numpy as np

class CNNPatternDetector:
    """
    Uses a CNN to classify recent price action images into BUY/SELL/HOLD.
    You need to train and export your own model (e.g. a PyTorch .pt file).
    """

    def __init__(self, model_path: str):
        # Load your trained PyTorch model
        self.device = torch.device('cpu')
        self.model = torch.jit.load(model_path, map_location=self.device)
        self.model.eval()
        # Define any preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

    def _prices_to_image(self, prices: list) -> Image.Image:
        """
        Convert a list of recent prices to a greyscale line chart image.
        """
        # Simple matplotlib plot → image in memory (you can optimize this)
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(2.24, 2.24), dpi=100)
        ax.plot(prices, color='black')
        ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf).convert('L')  # greyscale

    def signal(self, prices: list) -> str:
        """
        Args:
            prices: list of floats, recent price series
        
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        if len(prices) < 20:
            return 'HOLD'  # not enough data
        img = self._prices_to_image(prices[-100:])  # last 100 points
        x = self.transform(img).unsqueeze(0)  # add batch dim
        with torch.no_grad():
            out = self.model(x.to(self.device))
            pred = torch.argmax(out, dim=1).item()
        return ['BUY', 'SELL', 'HOLD'][pred]
