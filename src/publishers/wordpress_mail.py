import logging
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import Optional

from src.config import Config
from src.publishers.base import BasePublisher
from src.reporter import GeneratedReport

logger = logging.getLogger(__name__)


class WordPressMailPublisher(BasePublisher):
    """
    Publishes reports to WordPress via the Post by Email feature using SMTP.
    Attaches the generated statistical chart image so WordPress saves it to media library.
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_pass: Optional[str] = None,
        wp_post_email: Optional[str] = None,
    ):
        self.smtp_host = (smtp_host or Config.SMTP_HOST).strip()
        self.smtp_port = smtp_port or Config.SMTP_PORT
        self.smtp_user = (smtp_user or Config.SMTP_USER).strip()
        self.smtp_pass = (smtp_pass or Config.SMTP_PASS).replace(" ", "").strip()
        self.wp_post_email = (wp_post_email or Config.WP_POST_EMAIL).strip()

    def publish(self, report: GeneratedReport) -> bool:
        if not self.wp_post_email:
            raise ValueError("WP_POST_EMAIL is not configured in environment variables.")
        if not self.smtp_user or not self.smtp_pass:
            raise ValueError("SMTP credentials (SMTP_USER / SMTP_PASS) are not configured.")

        # Construct multipart MIME message
        msg = MIMEMultipart("related")
        msg["Subject"] = report.title
        msg["From"] = self.smtp_user
        msg["To"] = self.wp_post_email

        alt_part = MIMEMultipart("alternative")
        msg.attach(alt_part)

        # Plain text fallback (exactly like PaperToBlogActions)
        plain_text = "この投稿を表示するにはHTML対応のメールクライアントが必要です。"
        alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))

        # HTML content
        alt_part.attach(MIMEText(report.html_content, "html", "utf-8"))

        # Attach chart image
        if report.chart_path and report.chart_path.exists():
            try:
                with open(report.chart_path, "rb") as img_f:
                    img_data = img_f.read()
                mime_img = MIMEImage(img_data, _subtype="png")
                mime_img.add_header(
                    "Content-Disposition", "attachment", filename=report.chart_path.name
                )
                mime_img.add_header("Content-ID", f"<{report.chart_path.stem}>")
                msg.attach(mime_img)
                logger.info(f"Attached chart {report.chart_path.name} to email.")
            except Exception as e:
                logger.warning(f"Failed to attach chart image {report.chart_path}: {e}")

        # Send through SMTP
        logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port}...")
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            logger.info(f"Successfully sent report '{report.title}' to {self.wp_post_email}!")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to WordPress: {e}")
            raise
