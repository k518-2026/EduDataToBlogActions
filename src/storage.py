"""
History storage and report archive manager.
Maintains machine-readable JSON history (data/posted_reports.json) and
human-readable Markdown archive table (data/REPORT_ARCHIVE.md).
"""
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import Config
from src.reporter import GeneratedReport
from src.utils_date import get_jst_now

logger = logging.getLogger(__name__)


class ReportStorage:
    """Manages record-keeping for posted educational data reports."""

    def __init__(
        self,
        json_path: Optional[Path] = None,
        archive_path: Optional[Path] = None,
    ):
        self.json_path = json_path or Config.POSTED_REPORTS_PATH
        self.archive_path = archive_path or Config.REPORT_ARCHIVE_PATH

    def load_history(self) -> List[Dict[str, Any]]:
        if not self.json_path.exists():
            return []
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read history JSON {self.json_path}: {e}")
            return []

    def get_posted_dataset_ids(self) -> List[str]:
        history = self.load_history()
        return [entry["dataset_id"] for entry in history if "dataset_id" in entry]

    def get_past_angles_for_dataset(self, dataset_id: str) -> List[str]:
        """Returns list of past angle_ids used for a specific dataset, newest first."""
        history = self.load_history()
        angles = []
        for entry in reversed(history):
            if entry.get("dataset_id") == dataset_id:
                a_id = entry.get("angle_id")
                if a_id and a_id not in angles:
                    angles.append(a_id)
        return angles

    def get_recent_research_topics(
        self, dataset_id: Optional[str] = None, limit: int = 5
    ) -> List[Dict[str, str]]:
        """
        Retrieves recent post topics and angles to prevent thematic duplication.
        If dataset_id is provided, filters for that dataset; otherwise returns globally recent posts.
        """
        history = self.load_history()
        results = []
        for entry in reversed(history):
            if dataset_id and entry.get("dataset_id") != dataset_id:
                continue
            item = {
                "dataset_id": entry.get("dataset_id", ""),
                "angle_id": entry.get("angle_id", ""),
                "angle_name": entry.get("angle_name", ""),
                "title": entry.get("title", ""),
                "date": entry.get("date", ""),
            }
            if item not in results:
                results.append(item)
            if len(results) >= limit:
                break
        return results

    def record_post(self, report: GeneratedReport, platform: str):
        history = self.load_history()

        entry = {
            "dataset_id": report.dataset_id,
            "angle_id": getattr(report, "angle_id", "") or "",
            "angle_name": getattr(report, "angle_name", "") or "",
            "title": report.title,
            "categories": report.categories,
            "tags": report.tags,
            "platform": platform,
            "posted_at": get_jst_now().isoformat(),
            "date": report.created_at,
        }

        # If an entry for the same dataset and date already exists, replace it in-place
        replaced = False
        for i, h in enumerate(history):
            if h.get("dataset_id") == report.dataset_id and h.get("date") == report.created_at:
                history[i] = entry
                replaced = True
                logger.info(f"Replaced existing history record for {report.dataset_id} on {report.created_at} in-place.")
                break

        if not replaced:
            history.append(entry)

        # Save JSON
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        logger.info(f"Recorded post to {self.json_path} (Total: {len(history)})")

        # Sync REPORT_ARCHIVE.md
        self._sync_markdown_archive(history)

    def _sync_markdown_archive(self, history: List[Dict[str, Any]]):
        lines = [
            "# 📚 教育オープンデータ統計分析 配信レポート履歴アーカイブ",
            "",
            "本システム（EduDataToBlogActions）が毎日自動生成してブログに投稿したレポートの配信履歴です。",
            "",
            "| 配信日 | カテゴリ | レポートタイトル | データセットID | 配信方式 |",
            "| :---: | :---: | :--- | :---: | :---: |",
        ]

        # Reverse order: newest first
        for item in reversed(history):
            date = item.get("date", "-")
            cats = ",".join(item.get("categories", ["-"]))
            title = item.get("title", "-")
            ds_id = item.get("dataset_id", "-")
            platform = item.get("platform", "-")
            lines.append(f"| {date} | {cats} | {title} | `{ds_id}` | {platform} |")

        lines.append("")
        with open(self.archive_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Synced human-readable archive to {self.archive_path}")
