import os
from datetime import datetime
from PIL import Image
from api.client import APIClient
from api.models import GenerationParameters
from .settings import SettingsManager

class GeneratorCore:
    def __init__(self):
        self.settings = SettingsManager()
        # Load API Key from settings if available
        api_key = self.settings.get("api_key", "")
        self.client = APIClient(api_key)

    def update_api_key(self, api_key: str):
        self.settings.set("api_key", api_key)
        self.client.update_api_key(api_key)

    def generate(self, params: GenerationParameters) -> list[Image.Image]:
        return self.client.generate(params)

    def save_image(self, image: Image.Image, prefix: str = "img"):
        output_dir = self.settings.get("output_dir")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        path = os.path.join(output_dir, filename)
        
        counter = 1
        while os.path.exists(path):
            filename = f"{prefix}_{timestamp}_{counter}.png"
            path = os.path.join(output_dir, filename)
            counter += 1
            
        image.save(path)
        return path
