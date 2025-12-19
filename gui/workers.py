from PyQt6.QtCore import QThread, pyqtSignal
from api.models import GenerationParameters
from core.generator import GeneratorCore
from core.runner import GenerationRunner
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class GenerationWorker(QThread):
    result_ready = pyqtSignal(object)  # Emits list[Image.Image]
    error = pyqtSignal(str)
    status_update = pyqtSignal(str) # Emits status messages (e.g. retry countdown)

    def __init__(self, core: GeneratorCore, params: GenerationParameters, 
                 retry_enabled: bool = False, retry_interval: int = 5, max_retries: int = 0):
        super().__init__()
        self.core = core
        self.params = params
        self.retry_enabled = retry_enabled
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        runner = GenerationRunner(
            core=self.core,
            params=self.params,
            retry_enabled=self.retry_enabled,
            retry_interval=self.retry_interval,
            max_retries=self.max_retries,
            status_callback=self.status_update.emit,
            stop_check_callback=lambda: not self._is_running
        )

        try:
            images = runner.run()
            if images:
                self.result_ready.emit(images)
        except Exception as e:
            self.error.emit(str(e))
