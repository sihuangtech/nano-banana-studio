from PyQt6.QtCore import QThread, pyqtSignal
from api.models import GenerationParameters
from core.generator import GeneratorCore
from PIL import Image
import logging
import traceback

logger = logging.getLogger(__name__)

class GenerationWorker(QThread):
    finished = pyqtSignal(object)  # Emits list[Image.Image]
    error = pyqtSignal(str)

    def __init__(self, core: GeneratorCore, params: GenerationParameters):
        super().__init__()
        self.core = core
        self.params = params

    def run(self):
        try:
            logger.info(f"Starting generation with params: {self.params}")
            images = self.core.generate(self.params)
            # Save images automatically or let the UI decide? 
            # Let's save automatically for safety.
            saved_paths = []
            for img in images:
                path = self.core.save_image(img)
                saved_paths.append(path)
                logger.info(f"Image saved to: {path}")
            
            self.finished.emit(images)
        except Exception as e:
            # Log the full traceback to the console
            logger.error("Error during generation", exc_info=True)
            self.error.emit(str(e))
