import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt

from core.generator import GeneratorCore
from .workers import GenerationWorker
from .components.controls_panel import ControlsPanel
from .components.preview_panel import PreviewPanel

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nano Banana Studio")
        self.resize(1200, 800)
        
        self.core = GeneratorCore()
        self.worker = None
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Components
        self.controls = ControlsPanel(self.core)
        self.preview = PreviewPanel()
        
        # Connect signals
        self.controls.api_key_updated.connect(self.update_api_key)
        self.controls.generate_requested.connect(self.start_generation)
        self.controls.stop_requested.connect(self.stop_generation)
        
        # Add to splitter
        splitter.addWidget(self.controls)
        splitter.addWidget(self.preview)
        splitter.setStretchFactor(1, 2)
        
        # Status Bar
        self.setStatusBar(QStatusBar())
        
        # Load YAML defaults and update status
        status_msg = self.controls.load_yaml_defaults()
        if status_msg:
            self.statusBar().showMessage(status_msg)
        else:
            self.statusBar().showMessage("Ready")

    def update_api_key(self, key):
        self.core.update_api_key(key)
        self.statusBar().showMessage("API Key updated")

    def stop_generation(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.controls.generate_btn.setText("Stopping...")
            self.controls.generate_btn.setEnabled(False)

    def start_generation(self, params):
        self.controls.set_generating(True)
        self.statusBar().showMessage("Generating with Nano Banana (Gemini)...")
        
        # Save last used model
        self.core.settings.set("current_model", params.model)
        
        # Get retry settings from controls
        retry_enabled, retry_interval, max_retries = self.controls.get_retry_settings()

        self.worker = GenerationWorker(self.core, params, retry_enabled, retry_interval, max_retries)
        self.worker.result_ready.connect(self.on_generation_success)
        self.worker.error.connect(self.on_generation_error)
        self.worker.status_update.connect(self.on_status_update)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_generation_success(self, images):
        self.statusBar().showMessage("Generation complete")
        if images:
            self.preview.display_image(images[0])

    def on_generation_error(self, error_msg):
        first_line = error_msg.split('\n')[0] if '\n' in error_msg else error_msg
        self.statusBar().showMessage(f"Error: {first_line}")
        logger.error(f"Generation error displayed to user: {error_msg}")
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Generation Error")
        msg_box.setText("Image generation failed")
        msg_box.setDetailedText(error_msg)
        msg_box.exec()

    def on_status_update(self, msg):
        self.statusBar().showMessage(msg)

    def on_worker_finished(self):
        self.controls.set_generating(False)
