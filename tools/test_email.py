import os
import sys
import logging
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings import SettingsManager
from core.notifications import EmailService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Test email configuration")
    parser.add_argument("--attach", action="store_true", help="Include a dummy attachment")
    args = parser.parse_args()

    logger.info("Starting email test...")
    
    settings = SettingsManager()
    email_service = EmailService(settings)
    
    if not email_service.is_enabled():
        logger.error("Email is disabled in config.json")
        return

    config = email_service._get_config()
    logger.info(f"Configuration:")
    logger.info(f"  SMTP Server: {config.get('smtp_server')}")
    logger.info(f"  SMTP Port: {config.get('smtp_port')}")
    logger.info(f"  Sender: {config.get('sender_email')}")
    logger.info(f"  Receiver: {config.get('receiver_email')}")
    
    # Create dummy attachment if requested
    attachments = []
    if args.attach:
        dummy_file = "test_attachment.txt"
        with open(dummy_file, "w") as f:
            f.write("This is a test attachment from Nano Banana Studio.")
        attachments.append(dummy_file)
        logger.info(f"Created dummy attachment: {dummy_file}")

    try:
        logger.info("Sending test email...")
        email_service.send_success(attachments, "Test Prompt (Diagnostics)")
        logger.info("Test completed. Check your inbox (and SPAM folder).")
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        if args.attach and os.path.exists("test_attachment.txt"):
            os.remove("test_attachment.txt")

if __name__ == "__main__":
    main()
