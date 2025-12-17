import sys
import os
import logging

# Configure logging to output to console (stderr)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

# Add project root to path so imports work if running directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def exception_hook(exctype, value, traceback):
    """Global exception hook to catch unhandled exceptions."""
    logger.critical("Unhandled exception", exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)

def main():
    # Set the exception hook
    sys.excepthook = exception_hook
    
    logger.info("Starting Nano Banana Studio...")
    
    app = QApplication(sys.argv)
    
    # Set dark theme or styling here if desired
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
