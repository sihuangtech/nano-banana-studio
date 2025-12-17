from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, 
    QPushButton, QTextEdit, QComboBox, QSplitter,
    QScrollArea, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
import io
import logging

from api.models import GenerationParameters
from core.generator import GeneratorCore
from .workers import GenerationWorker

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
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left Panel - Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        
        # API Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Google API Key:"))
        self.key_input = QLineEdit(self.core.settings.get("api_key", ""))
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Enter your Gemini API Key")
        self.key_input.editingFinished.connect(self.update_api_key)
        key_layout.addWidget(self.key_input)
        controls_layout.addLayout(key_layout)
        
        # Prompt
        controls_layout.addWidget(QLabel("Prompt:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter prompt here... (e.g. 'A futuristic nano banana city')")
        self.prompt_input.setMaximumHeight(100)
        controls_layout.addWidget(self.prompt_input)
        
        # Negative Prompt (Gemini handles this via instructions)
        controls_layout.addWidget(QLabel("Negative Prompt (Optional):"))
        self.neg_prompt_input = QTextEdit()
        self.neg_prompt_input.setPlaceholderText("Elements to avoid...")
        self.neg_prompt_input.setMaximumHeight(80)
        controls_layout.addWidget(self.neg_prompt_input)
        
        # Parameters Grid
        params_layout = QHBoxLayout()
        
        # Col 1: Basic
        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        # Load available models from settings
        models = self.core.settings.get("models", [])
        self.model_combo.addItems(models)
        self.model_combo.setCurrentText(self.core.settings.get("current_model", ""))
        col1.addWidget(self.model_combo)
        
        col1.addWidget(QLabel("Aspect Ratio:"))
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(["1:1", "16:9", "4:3", "3:4", "9:16"])
        col1.addWidget(self.aspect_combo)

        col1.addWidget(QLabel("Image Size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["1K", "2K", "4K"])
        col1.addWidget(self.size_combo)
        
        params_layout.addLayout(col1)
        
        # Col 2: Generation Config
        col2 = QVBoxLayout()
        
        col2.addWidget(QLabel("Number of Images:"))
        self.num_images_spin = QSpinBox()
        self.num_images_spin.setRange(1, 4)
        self.num_images_spin.setValue(1)
        col2.addWidget(self.num_images_spin)

        col2.addWidget(QLabel("Person Generation:"))
        self.person_combo = QComboBox()
        self.person_combo.addItems(["allow_adult", "allow_all", "dont_allow"])
        col2.addWidget(self.person_combo)

        col2.addWidget(QLabel("Safety Filter:"))
        self.safety_combo = QComboBox()
        self.safety_combo.addItems(["block_none", "block_only_high", "block_medium_and_above", "block_low_and_above"])
        self.safety_combo.setCurrentText("block_none")
        col2.addWidget(self.safety_combo)
        
        params_layout.addLayout(col2)

        # Col 3: Advanced
        col3 = QVBoxLayout()

        col3.addWidget(QLabel("Seed (-1 for random):"))
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(-1, 2147483647)
        self.seed_spin.setValue(-1)
        col3.addWidget(self.seed_spin)

        col3.addWidget(QLabel("Guidance Scale (0 for auto):"))
        self.guidance_spin = QDoubleSpinBox()
        self.guidance_spin.setRange(0.0, 100.0)
        self.guidance_spin.setValue(0.0)
        self.guidance_spin.setSingleStep(0.5)
        col3.addWidget(self.guidance_spin)

        col3.addStretch()
        params_layout.addLayout(col3)
        
        controls_layout.addLayout(params_layout)
        
        # Generate Button
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #FFC107; color: black;")
        self.generate_btn.clicked.connect(self.start_generation)
        controls_layout.addWidget(self.generate_btn)
        
        controls_layout.addStretch()
        
        # Right Panel - Preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        self.image_label = QLabel("Generated image will appear here")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3c3f41;")
        self.image_label.setMinimumSize(400, 400)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        preview_layout.addWidget(scroll_area)
        
        # Add widgets to splitter
        splitter.addWidget(controls_widget)
        splitter.addWidget(preview_widget)
        splitter.setStretchFactor(1, 2)
        
        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    def update_api_key(self):
        key = self.key_input.text()
        self.core.update_api_key(key)
        self.statusBar().showMessage("API Key updated")

    def start_generation(self):
        if not self.key_input.text():
            QMessageBox.warning(self, "Missing API Key", "Please enter your Google API Key.")
            return

        self.toggle_inputs(False)
        self.statusBar().showMessage("Generating with Nano Banana (Gemini)...")
        
        # Prepare optional parameters
        seed_val = self.seed_spin.value()
        seed = seed_val if seed_val != -1 else None
        
        guidance_val = self.guidance_spin.value()
        guidance = guidance_val if guidance_val != 0.0 else None
        
        params = GenerationParameters(
            prompt=self.prompt_input.toPlainText(),
            negative_prompt=self.neg_prompt_input.toPlainText(),
            aspect_ratio=self.aspect_combo.currentText(),
            number_of_images=self.num_images_spin.value(),
            model=self.model_combo.currentText(),
            image_size=self.size_combo.currentText(),
            person_generation=self.person_combo.currentText(),
            safety_filter=self.safety_combo.currentText(),
            seed=seed,
            guidance_scale=guidance
        )
        
        # Save last used model
        self.core.settings.set("current_model", self.model_combo.currentText())
        
        self.worker = GenerationWorker(self.core, params)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.worker.start()

    def on_generation_finished(self, images):
        self.toggle_inputs(True)
        self.statusBar().showMessage("Generation complete")
        
        if images:
            self.display_image(images[0])

    def on_generation_error(self, error_msg):
        self.toggle_inputs(True)
        self.statusBar().showMessage(f"Error: {error_msg}")
        logger.error(f"Generation error displayed to user: {error_msg}")
        QMessageBox.critical(self, "Generation Error", error_msg)

    def display_image(self, pil_image):
        # Convert PIL image to QPixmap
        im_data = io.BytesIO()
        pil_image.save(im_data, format='PNG')
        qimg = QImage.fromData(im_data.getvalue())
        pixmap = QPixmap.fromImage(qimg)
        
        # Scale if too large, but keep aspect ratio
        self.image_label.setPixmap(pixmap)
        self.image_label.resize(pixmap.size())

    def toggle_inputs(self, enabled):
        self.generate_btn.setEnabled(enabled)
        self.prompt_input.setEnabled(enabled)
