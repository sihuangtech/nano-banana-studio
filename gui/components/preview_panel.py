from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import io

class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.image_label = QLabel("Generated image will appear here")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3c3f41;")
        self.image_label.setMinimumSize(400, 400)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

    def display_image(self, pil_image):
        # Convert PIL image to QPixmap
        im_data = io.BytesIO()
        pil_image.save(im_data, format='PNG')
        qimg = QImage.fromData(im_data.getvalue())
        pixmap = QPixmap.fromImage(qimg)
        
        # Scale if too large, but keep aspect ratio
        self.image_label.setPixmap(pixmap)
        self.image_label.resize(pixmap.size())
