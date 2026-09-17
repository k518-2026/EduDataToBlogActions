import base64
import logging
from typing import Optional
import requests

from src.config import Config
from src.publishers.base import BasePublisher
from src.reporter import GeneratedReport

logger = logging.getLogger(__name__)


class WordPressRestPublisher(BasePublisher):
    """
    Publishes reports to WordPress using the official REST API (wp/v2/posts).
    Uploads chart image as media attachment and sets it as featured image.
    Requires WordPress Application Password.
    """

    def __init__(
        self,
        site_url: Optional[str] = None,
        username: Optional[str] = None,
        app_password: Optional[str] = None,
    ):
        self.site_url = (site_url or Config.WP_SITE_URL).strip().rstrip("/")
        self.username = (username or Config.WP_USER).strip()
        self.app_password = (app_password or Config.WP_APP_PASSWORD).replace(" ", "").strip()

    def _get_auth_header(self) -> dict:
        creds = f"{self.username}:{self.app_password}"
        token = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {token}"}

    def _upload_media(self, chart_path) -> Optional[int]:
        if not chart_path or not chart_path.exists():
            return None
        media_url = f"{self.site_url}/wp-json/wp/v2/media"
        headers = self._get_auth_header()
        headers["Content-Disposition"] = f'attachment; filename="{chart_path.name}"'
        headers["Content-Type"] = "image/png"

        try:
            with open(chart_path, "rb") as f:
                resp = requests.post(media_url, headers=headers, data=f, timeout=30)
            if resp.status_code in (200, 201):
                media_id = resp.json().get("id")
                logger.info(f"Uploaded chart image to WordPress Media Library (ID: {media_id})")
                return media_id
            else:
                logger.warning(f"Media upload failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.warning(f"Error uploading media to WordPress: {e}")
        return None

    def publish(self, report: GeneratedReport) -> bool:
        if not self.site_url or not self.username or not self.app_password:
            raise ValueError("WordPress REST credentials (WP_SITE_URL, WP_USER, WP_APP_PASSWORD) not configured.")

        # Upload chart image first
        featured_media_id = self._upload_media(report.chart_path)

        post_url = f"{self.site_url}/wp-json/wp/v2/posts"
        headers = self._get_auth_header()
        headers["Content-Type"] = "application/json"

        # Clean email-specific shortcodes from HTML content for web display
        content = report.html_content
        if "<!-- WordPress Post by Email Shortcodes" in content:
            content = content.split("<!-- WordPress Post by Email Shortcodes")[0].rstrip()

        status = Config.WP_POST_STATUS or "publish"
        payload = {
            "title": report.title,
            "content": content,
            "status": status,
        }
        if featured_media_id:
            payload["featured_media"] = featured_media_id

        logger.info(f"Posting to WordPress REST API: {post_url} (status: {status})")
        resp = requests.post(post_url, headers=headers, json=payload, timeout=30)
        if resp.status_code in (200, 201):
            post_id = resp.json().get("id")
            post_link = resp.json().get("link")
            logger.info(f"Successfully published post via REST API! Post ID: {post_id}, URL: {post_link}")
            return True
        else:
            logger.error(f"Failed to post via REST API: {resp.status_code} - {resp.text}")
            raise RuntimeError(f"WordPress REST API post failed with code {resp.status_code}")
