import time
import logging
from typing import Callable, Optional
from api.models import GenerationParameters
from core.generator import GeneratorCore
from core.notifications import EmailService
from core.settings import SettingsManager

logger = logging.getLogger(__name__)

class GenerationRunner:
    """
    Shared runner for both GUI and CLI to handle generation workflow:
    1. Retry logic
    2. Notifications
    3. Status updates
    """
    def __init__(self, core: GeneratorCore, params: GenerationParameters,
                 retry_enabled: bool = False, retry_interval: int = 5, max_retries: int = 0,
                 status_callback: Optional[Callable[[str], None]] = None,
                 stop_check_callback: Optional[Callable[[], bool]] = None):
        self.core = core
        self.params = params
        self.retry_enabled = retry_enabled
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.status_callback = status_callback
        self.stop_check_callback = stop_check_callback
        
        self.email_service = EmailService(core.settings)

    def _should_stop(self) -> bool:
        if self.stop_check_callback:
            return self.stop_check_callback()
        return False

    def _update_status(self, msg: str):
        if self.status_callback:
            self.status_callback(msg)
        else:
            logger.info(msg)

    def run(self):
        retry_count = 0
        
        while True:
            try:
                if retry_count > 0:
                    self._update_status(f"Retry attempt {retry_count} starting...")
                
                logger.info(f"Starting generation with params: {self.params}")
                images = self.core.generate(self.params)
                
                if self._should_stop():
                    return

                # Save images
                saved_paths = []
                for img in images:
                    path = self.core.save_image(img)
                    saved_paths.append(path)
                    logger.info(f"Image saved to: {path}")
                
                # Send Success Email
                self.email_service.send_success(saved_paths, self.params.prompt)
                
                return images

            except Exception as e:
                logger.error("Error during generation", exc_info=True)
                error_msg = str(e)

                # Send Failure Email immediately on first failure? 
                # Or wait until all retries failed?
                # Usually better to wait until final failure, but user might want to know about delays.
                # Let's send only on final failure to avoid spamming.
                
                # Check retry condition
                if not self.retry_enabled or (self.max_retries > 0 and retry_count >= self.max_retries):
                    self.email_service.send_failure(error_msg, self.params.prompt)
                    raise e
                
                if self._should_stop():
                    return

                # Prepare for retry
                retry_count += 1
                
                # Wait loop with interrupt check
                wait_time = 0
                step = 0.5
                while wait_time < self.retry_interval:
                    if self._should_stop():
                        return
                    
                    remaining = int(self.retry_interval - wait_time) + 1
                    self._update_status(f"Error: {error_msg.splitlines()[0]}. Retrying in {remaining}s... (Attempt {retry_count})")
                    
                    time.sleep(step)
                    wait_time += step
                
                if self._should_stop():
                    return
