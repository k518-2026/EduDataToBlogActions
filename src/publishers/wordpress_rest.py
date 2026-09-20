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

    def _find_existing_post(self, report: GeneratedReport) -> Optional[int]:
        """
        Searches for an existing WordPress post matching the report dataset and date
        to allow in-place replacement instead of creating a duplicate post.
        """
        if not self.site_url or not self.username or not self.app_password:
            return None
        try:
            import re
            headers = self._get_auth_header()
            list_url = f"{self.site_url}/wp-json/wp/v2/posts?per_page=20&status=publish,draft,future,private"
            resp = requests.get(list_url, headers=headers, timeout=20)
            if resp.status_code == 200:
                posts = resp.json()
                today_iso = report.created_at  # e.g., "2026-09-21"
                today_jp = today_iso.replace("-", "年", 1).replace("-", "月", 1) + "日"

                # Extract identifier keywords from current report title (e.g. "児童生徒指導要録調査")
                match = re.search(r"【(.*?)】", report.title)
                main_tag = match.group(1) if match else ""

                for p in posts:
                    p_id = p.get("id")
                    p_date = str(p.get("date", ""))
                    p_title_obj = p.get("title", {})
                    p_title = p_title_obj.get("rendered", "") if isinstance(p_title_obj, dict) else str(p_title_obj)

                    date_matches = p_date.startswith(today_iso) or today_iso in p_title or today_jp in p_title
                    if date_matches:
                        # If tag matches or dataset keywords match, it is the same post to replace
                        if main_tag and main_tag in p_title:
                            logger.info(f"Found existing post on WordPress for {today_iso} matching '{main_tag}' (ID: {p_id}). Will update/replace it.")
                            return p_id
                        elif not main_tag and report.dataset_id in p.get("slug", ""):
                            logger.info(f"Found existing post on WordPress for {today_iso} matching dataset ID (ID: {p_id}). Will update/replace it.")
                            return p_id
        except Exception as e:
            logger.warning(f"Error checking existing WordPress posts: {e}")
        return None

    def publish(self, report: GeneratedReport) -> bool:
        if not self.site_url or not self.username or not self.app_password:
            raise ValueError("WordPress REST credentials (WP_SITE_URL, WP_USER, WP_APP_PASSWORD) not configured.")

        # Upload chart image first
        featured_media_id = self._upload_media(report.chart_path)

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

        # Check if an existing post for today/dataset can be updated/replaced in-place
        existing_post_id = self._find_existing_post(report)
        if existing_post_id:
            post_url = f"{self.site_url}/wp-json/wp/v2/posts/{existing_post_id}"
            logger.info(f"Updating/replacing existing WordPress post (ID: {existing_post_id}) via REST API: {post_url}")
        else:
            post_url = f"{self.site_url}/wp-json/wp/v2/posts"
            logger.info(f"Posting new article to WordPress REST API: {post_url} (status: {status})")

        resp = requests.post(post_url, headers=headers, json=payload, timeout=30)
        if resp.status_code in (200, 201):
            post_id = resp.json().get("id")
            post_link = resp.json().get("link")
            action_desc = "updated/replaced" if existing_post_id else "published"
            logger.info(f"Successfully {action_desc} post via REST API! Post ID: {post_id}, URL: {post_link}")
            return True
        else:
            logger.error(f"Failed to post via REST API: {resp.status_code} - {resp.text}")
            raise RuntimeError(f"WordPress REST API post failed with code {resp.status_code}")
