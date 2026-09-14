import logging
from pathlib import Path
import shutil
from typing import Optional

from src.config import REPORTS_DIR
from src.publishers.base import BasePublisher
from src.reporter import GeneratedReport

logger = logging.getLogger(__name__)


class MarkdownFilePublisher(BasePublisher):
    """
    Saves the generated report as a Markdown document and stores chart assets locally.
    Enables persistent repository archiving and GitHub Pages / Jekyll rendering.
    """

    def __init__(self, reports_dir: Optional[Path] = None):
        self.reports_dir = reports_dir or REPORTS_DIR
        self.assets_dir = self.reports_dir / "assets"
        self.pdf_dir = self.reports_dir / "pdf"
        self.reports_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        self.pdf_dir.mkdir(exist_ok=True)

    def publish(self, report: GeneratedReport) -> bool:
        # 1. Copy chart asset to reports/assets/
        dest_chart_filename = f"{report.created_at}_{report.chart_path.name}"
        dest_chart_path = self.assets_dir / dest_chart_filename
        if report.chart_path.exists():
            shutil.copy(report.chart_path, dest_chart_path)
            logger.info(f"Copied chart asset to {dest_chart_path}")

        # 2. Copy academic thesis PDF to reports/pdf/
        if report.pdf_path and report.pdf_path.exists():
            dest_pdf_path = self.pdf_dir / report.pdf_path.name
            if report.pdf_path.resolve() != dest_pdf_path.resolve():
                shutil.copy(report.pdf_path, dest_pdf_path)
            logger.info(f"Archived academic thesis PDF to {dest_pdf_path}")

        # 3. Adjust chart path in markdown content to point to assets/
        md_content = report.markdown_content.replace(
            f"({report.chart_path.name})", f"(assets/{dest_chart_filename})"
        )

        # 4. Write markdown report
        report_file = self.reports_dir / f"{report.created_at}_{report.dataset_id}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Successfully archived report to {report_file}")
        return True
