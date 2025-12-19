import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formatdate, make_msgid
from typing import Optional, List
import os

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, settings_manager):
        self.settings = settings_manager
        
    def _get_config(self):
        return self.settings.get("email", {})

    def is_enabled(self) -> bool:
        config = self._get_config()
        return config.get("enabled", False)

    def _load_template(self, template_name: str) -> str:
        """
        Load HTML template from templates directory.
        Falls back to empty string if not found.
        """
        try:
            # Assuming templates are in 'templates' folder at project root
            # or relative to core/notifications.py -> ../../templates
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_path = os.path.join(base_dir, "templates", template_name)
            
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Failed to load email template {template_name}: {e}")
        
        return ""

    def send_success(self, image_paths: List[str], prompt: str):
        if not self.is_enabled():
            return
            
        subject = "Nano Banana Studio - Generation Success"
        
        # Try to load HTML template
        html_template = self._load_template("email_success.html")
        html_body = None
        
        if html_template:
            try:
                # Use simple replacement instead of .format() to avoid conflict with CSS braces
                html_body = html_template.replace("{prompt}", prompt)
            except Exception as e:
                logger.error(f"Failed to format success email template: {e}")

        plain_body = f"Your image generation was successful.\n\nPrompt: {prompt}"
        
        self._send_email(subject, plain_body, html_body, attachments=image_paths)

    def send_failure(self, error_msg: str, prompt: str):
        if not self.is_enabled():
            return

        subject = "Nano Banana Studio - Generation Failed"
        
        # Try to load HTML template
        html_template = self._load_template("email_failure.html")
        html_body = None
        
        if html_template:
            try:
                # Use simple replacement instead of .format() to avoid conflict with CSS braces
                html_body = html_template.replace("{prompt}", prompt).replace("{error_msg}", error_msg)
            except Exception as e:
                logger.error(f"Failed to format failure email template: {e}")

        plain_body = f"Your image generation failed.\n\nPrompt: {prompt}\n\nError:\n{error_msg}"
        
        self._send_email(subject, plain_body, html_body)

    def _send_email(self, subject: str, plain_body: str, html_body: Optional[str] = None, attachments: Optional[List[str]] = None):
        config = self._get_config()
        
        smtp_server = config.get("smtp_server")
        smtp_port = config.get("smtp_port")
        sender_email = config.get("sender_email")
        sender_password = config.get("sender_password")
        receiver_email = config.get("receiver_email")

        if not all([smtp_server, sender_email, receiver_email]):
            logger.warning("Email configuration incomplete. Skipping email notification.")
            return

        # Use 'mixed' as the outer container if we have attachments
        if attachments:
            msg = MIMEMultipart('mixed')
            # Create the body container
            body_container = MIMEMultipart('alternative')
            msg.attach(body_container)
        else:
            msg = MIMEMultipart('alternative')
            body_container = msg

        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid()

        # Attach plain text version to the body container
        body_container.attach(MIMEText(plain_body, 'plain'))
        
        # Attach HTML version if available to the body container
        if html_body:
            body_container.attach(MIMEText(html_body, 'html'))

        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            img_data = f.read()
                            image = MIMEImage(img_data, name=os.path.basename(file_path))
                            # Add header for attachment
                            image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                            msg.attach(image)
                    except Exception as e:
                        logger.error(f"Failed to attach image {file_path}: {e}")

        try:
            # Ensure port is int
            port = int(smtp_port) if smtp_port else 587
            
            logger.info(f"Connecting to SMTP server {smtp_server}:{port}...")
            # Use SMTP_SSL if port is 465, otherwise use SMTP + starttls
            if port == 465:
                server = smtplib.SMTP_SSL(smtp_server, port, timeout=30)
            else:
                server = smtplib.SMTP(smtp_server, port, timeout=30)
                server.starttls()

            if sender_password:
                server.login(sender_email, sender_password)
            
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent successfully to {receiver_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            # Raise exception if in CLI/debug mode? For now just log.
