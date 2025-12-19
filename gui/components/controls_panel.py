import logging
import yaml
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QPushButton, QTextEdit, 
    QComboBox, QGroupBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from api.models import GenerationParameters

logger = logging.getLogger(__name__)

class ControlsPanel(QWidget):
    generate_requested = pyqtSignal(object)  # Emits GenerationParameters
    stop_requested = pyqtSignal()
    api_key_updated = pyqtSignal(str)

    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core
        self.init_ui()
        # Note: MainWindow will call load_yaml_defaults to handle status bar feedback

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # API Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Google API Key:"))
        self.key_input = QLineEdit(self.core.settings.get("api_key", ""))
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Enter your Gemini API Key")
        self.key_input.editingFinished.connect(self._on_api_key_changed)
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)
        
        # Prompt
        layout.addWidget(QLabel("Prompt:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter prompt here... (e.g. 'A futuristic nano banana city')")
        self.prompt_input.setMaximumHeight(100)
        layout.addWidget(self.prompt_input)
        
        # Negative Prompt
        layout.addWidget(QLabel("Negative Prompt (Optional):"))
        self.neg_prompt_input = QTextEdit()
        self.neg_prompt_input.setPlaceholderText("Elements to avoid...")
        self.neg_prompt_input.setMaximumHeight(80)
        layout.addWidget(self.neg_prompt_input)
        
        # Parameters Grid
        params_layout = QHBoxLayout()
        
        # Col 1: Basic
        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
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

        # Retry Settings
        retry_group = QGroupBox("Retry Settings")
        retry_layout = QVBoxLayout()
        self.retry_check = QCheckBox("Auto Retry on Failure")
        retry_layout.addWidget(self.retry_check)
        
        retry_grid = QHBoxLayout()
        retry_grid.addWidget(QLabel("Interval:"))
        time_layout = QHBoxLayout()
        time_layout.setSpacing(2)
        
        self.retry_h_spin = QSpinBox()
        self.retry_h_spin.setRange(0, 24)
        self.retry_h_spin.setSuffix("h")
        time_layout.addWidget(self.retry_h_spin)
        
        self.retry_m_spin = QSpinBox()
        self.retry_m_spin.setRange(0, 59)
        self.retry_m_spin.setSuffix("m")
        time_layout.addWidget(self.retry_m_spin)
        
        self.retry_s_spin = QSpinBox()
        self.retry_s_spin.setRange(0, 59)
        self.retry_s_spin.setValue(10)
        self.retry_s_spin.setSuffix("s")
        time_layout.addWidget(self.retry_s_spin)
        
        retry_grid.addLayout(time_layout)
        retry_grid.addWidget(QLabel("Max Retries:"))
        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(0, 100)
        self.max_retries_spin.setValue(0)
        retry_grid.addWidget(self.max_retries_spin)
        
        retry_layout.addLayout(retry_grid)
        retry_group.setLayout(retry_layout)
        col3.addWidget(retry_group)
        col3.addStretch()
        params_layout.addLayout(col3)
        
        layout.addLayout(params_layout)
        
        # Generate Button
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #FFC107; color: black;")
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        layout.addWidget(self.generate_btn)
        layout.addStretch()

    def load_yaml_defaults(self):
        """Check for 'generate.yaml' and pre-fill UI fields. Returns status message if loaded."""
        if not os.path.exists("generate.yaml"):
            return None

        try:
            with open("generate.yaml", 'r') as f:
                config = yaml.safe_load(f)
            if not config:
                return None
                
            logger.info("Loading defaults from generate.yaml")

            if "prompt" in config and config["prompt"]:
                self.prompt_input.setPlainText(str(config["prompt"]))
            if "negative_prompt" in config and config["negative_prompt"]:
                self.neg_prompt_input.setPlainText(str(config["negative_prompt"]))
            elif "neg_prompt" in config and config["neg_prompt"]:
                self.neg_prompt_input.setPlainText(str(config["neg_prompt"]))
            if "model" in config and config["model"]:
                index = self.model_combo.findText(str(config["model"]))
                if index >= 0: self.model_combo.setCurrentIndex(index)
            if "aspect_ratio" in config and config["aspect_ratio"]:
                index = self.aspect_combo.findText(str(config["aspect_ratio"]))
                if index >= 0: self.aspect_combo.setCurrentIndex(index)
            if "image_size" in config and config["image_size"]:
                index = self.size_combo.findText(str(config["image_size"]))
                if index >= 0: self.size_combo.setCurrentIndex(index)
            if "num_images" in config and config["num_images"]:
                self.num_images_spin.setValue(int(config["num_images"]))
            if "person_generation" in config and config["person_generation"]:
                index = self.person_combo.findText(str(config["person_generation"]))
                if index >= 0: self.person_combo.setCurrentIndex(index)
            if "safety_filter" in config and config["safety_filter"]:
                index = self.safety_combo.findText(str(config["safety_filter"]))
                if index >= 0: self.safety_combo.setCurrentIndex(index)
            if "seed" in config and config["seed"] is not None:
                self.seed_spin.setValue(int(config["seed"]))
            if "guidance_scale" in config and config["guidance_scale"] is not None:
                self.guidance_spin.setValue(float(config["guidance_scale"]))
            if "retry" in config:
                self.retry_check.setChecked(bool(config["retry"]))
            if "retry_interval" in config and config["retry_interval"] is not None:
                total_seconds = int(config["retry_interval"])
                self.retry_h_spin.setValue(total_seconds // 3600)
                self.retry_m_spin.setValue((total_seconds % 3600) // 60)
                self.retry_s_spin.setValue(total_seconds % 60)
            if "max_retries" in config and config["max_retries"] is not None:
                self.max_retries_spin.setValue(int(config["max_retries"]))

            return "Defaults loaded from generate.yaml"
        except Exception as e:
            logger.error(f"Failed to load generate.yaml: {e}")
            return f"Failed to load YAML: {e}"

    def _on_api_key_changed(self):
        self.api_key_updated.emit(self.key_input.text())

    def _on_generate_clicked(self):
        if self.generate_btn.text() == "Stop Generation":
            self.stop_requested.emit()
            return

        if not self.key_input.text():
            QMessageBox.warning(self, "Missing API Key", "Please enter your Google API Key.")
            return

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
        self.generate_requested.emit(params)

    def get_retry_settings(self):
        retry_enabled = self.retry_check.isChecked()
        h = self.retry_h_spin.value()
        m = self.retry_m_spin.value()
        s = self.retry_s_spin.value()
        retry_interval = (h * 3600) + (m * 60) + s
        if retry_enabled and retry_interval < 1:
            retry_interval = 1
        max_retries = self.max_retries_spin.value()
        return retry_enabled, retry_interval, max_retries

    def set_generating(self, generating: bool):
        self.toggle_inputs(not generating)
        if generating:
            self.generate_btn.setText("Stop Generation")
            self.generate_btn.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #F44336; color: white;")
            self.generate_btn.setEnabled(True)
        else:
            self.generate_btn.setText("Generate")
            self.generate_btn.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #FFC107; color: black;")

    def toggle_inputs(self, enabled: bool):
        self.generate_btn.setEnabled(enabled)
        self.prompt_input.setEnabled(enabled)
        self.neg_prompt_input.setEnabled(enabled)
        self.model_combo.setEnabled(enabled)
        self.aspect_combo.setEnabled(enabled)
        self.size_combo.setEnabled(enabled)
        self.num_images_spin.setEnabled(enabled)
        self.person_combo.setEnabled(enabled)
        self.safety_combo.setEnabled(enabled)
        self.seed_spin.setEnabled(enabled)
        self.guidance_spin.setEnabled(enabled)
        self.retry_check.setEnabled(enabled)
        self.retry_h_spin.setEnabled(enabled)
        self.retry_m_spin.setEnabled(enabled)
        self.retry_s_spin.setEnabled(enabled)
        self.max_retries_spin.setEnabled(enabled)
