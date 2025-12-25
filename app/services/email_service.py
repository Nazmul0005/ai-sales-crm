"""
Email service for sending outreach emails via SMTP.
"""
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = "sales@ai-crm.com"  # Demo sender
        
        logger.info(f"Email Service initialized with SMTP: {self.smtp_host}:{self.smtp_port}")
    
    def _create_html_email(self, subject: str, body: str, recipient_name: str) -> str:
        """
        Create HTML formatted email body.
        
        Args:
            subject: Email subject
            body: Plain text body
            recipient_name: Recipient's name
            
        Returns:
            HTML formatted email
        """
        # Convert plain text to HTML with basic formatting
        html_body = body.replace('\n\n', '</p><p>').replace('\n', '<br>')
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .email-header {{
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .email-body {{
                    padding: 20px 0;
                }}
                .email-footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <h2 style="color: #007bff; margin: 0;">AI Sales CRM</h2>
                </div>
                <div class="email-body">
                    <p>{html_body}</p>
                </div>
                <div class="email-footer">
                    <p>This is an automated message from AI Sales CRM.</p>
                    <p>If you'd like to unsubscribe, please reply with "UNSUBSCRIBE".</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_template
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        recipient_name: str
    ) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body text
            recipient_name: Recipient's name for personalization
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            logger.debug(f"Sending email to {to_email}")
            
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add plain text part
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML part
            html_content = self._create_html_email(subject, body, recipient_name)
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=False  # MailHog doesn't use TLS
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}", exc_info=True)
            return False
    
    async def send_bulk_emails(
        self,
        recipients: list[tuple[str, str, str, str]]
    ) -> tuple[int, int]:
        """
        Send multiple emails.
        
        Args:
            recipients: List of (email, subject, body, name) tuples
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        successful = 0
        failed = 0
        
        logger.info(f"Starting bulk email send for {len(recipients)} recipients")
        
        for to_email, subject, body, name in recipients:
            try:
                result = await self.send_email(to_email, subject, body, name)
                if result:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Unexpected error sending to {to_email}: {e}")
                failed += 1
        
        logger.info(f"Bulk email send complete: {successful} sent, {failed} failed")
        return successful, failed
    
    async def test_connection(self) -> bool:
        """
        Test SMTP connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Testing SMTP connection...")
            
            # Try to connect
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                timeout=5.0  # Fail fast if unavailable
            ) as smtp:
                await smtp.connect(timeout=5.0)
                logger.info("SMTP connection test successful")
                return True
                
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}", exc_info=True)
            return False