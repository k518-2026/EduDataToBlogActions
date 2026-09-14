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

    def record_post(self, report: GeneratedReport, platform: str):
        history = self.load_history()

        entry = {
            "dataset_id": report.dataset_id,
            "title": report.title,
            "categories": report.categories,
            "tags": report.tags,
            "platform": platform,
            "posted_at": datetime.now().isoformat(),
            "date": report.created_at,
        }

        # Append new entry
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
