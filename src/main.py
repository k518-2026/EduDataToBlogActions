"""
EduDataToBlogActions - Main Pipeline Entry Point.
Coordinates fetching, statistical analysis, visualization, AI insight generation,
report assembly, blog publishing, and history storage.
"""
import argparse
import logging
import os
from pathlib import Path
import sys

from src.analyzer import EduDataAnalyzer
from src.config import Config, REPORTS_DIR, TEMP_DIR
from src.fetchers.catalog import DatasetCatalog
from src.insights import GeminiInsightGenerator
from src.publishers.markdown_file import MarkdownFilePublisher
from src.publishers.wordpress_mail import WordPressMailPublisher
from src.publishers.wordpress_rest import WordPressRestPublisher
from src.reporter import EduReportBuilder
from src.storage import ReportStorage

import io

# Ensure UTF-8 output on all platforms
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("EduDataToBlogActions")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Daily Open Educational Data Statistical Analysis & Blog Auto-Poster"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate pipeline without sending email/blog post or updating history.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force execution ignoring recently posted dataset history.",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="",
        help="Target topic filter: 'math' (算数・数学), 'info' (情報教育・プログラミング), or 'all'.",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="",
        help="Target specific dataset ID (e.g. 'japan_national_assessment_math').",
    )
    parser.add_argument(
        "--publisher",
        type=str,
        default="",
        help="Override publisher type ('wordpress_mail', 'wordpress_rest', 'markdown_only').",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logger.info("==================================================")
    logger.info("🚀 Starting EduDataToBlogActions Pipeline")
    logger.info("==================================================")

    # 1. Initialize components
    catalog = DatasetCatalog()
    analyzer = EduDataAnalyzer()
    visualizer_dir = TEMP_DIR
    visualizer_dir.mkdir(exist_ok=True)
    from src.visualizer import EduDataVisualizer
    visualizer = EduDataVisualizer(output_dir=visualizer_dir)
    insight_gen = GeminiInsightGenerator()
    report_builder = EduReportBuilder()
    storage = ReportStorage()

    topic = (args.topic or Config.DEFAULT_TOPIC or "all").strip().strip("'\"").lower()
    publisher_type = (args.publisher or Config.BLOG_PUBLISHER_TYPE or "wordpress_mail").strip().strip("'\"").lower()

    # 2. Select dataset
    posted_ids = storage.get_posted_dataset_ids()
    if args.dataset:
        dataset = catalog.get_by_id(args.dataset)
        if not dataset:
            logger.error(f"Specified dataset '{args.dataset}' not found in catalog.")
            sys.exit(1)
        logger.info(f"Selected explicit dataset: {dataset.title} ({dataset.id})")
    else:
        dataset = catalog.select_dataset(
            topic=topic,
            posted_history_ids=posted_ids,
            force=args.force,
        )
        logger.info(f"Selected dataset for analysis: {dataset.title} ({dataset.id})")

    logger.info(f"Dataset category: {dataset.category}, Region: {dataset.region}, Rows: {len(dataset.df)}")

    # 3. Perform statistical analysis
    logger.info("📊 Running statistical analysis engine...")
    analysis = analyzer.analyze(dataset)
    logger.info(f"Calculated statistics for {len(analysis.descriptive_stats)} metrics.")
    for ins in analysis.key_insights:
        logger.info(f"  Insight: {ins}")

    # 4. Generate visualization chart
    logger.info("🎨 Generating publication-quality chart...")
    chart_path = visualizer.generate_chart(dataset, analysis)
    logger.info(f"Chart generated successfully: {chart_path}")

    # 5. Generate pedagogical insights
    logger.info("💡 Generating educational pedagogical insights...")
    insights = insight_gen.generate_insights(dataset, analysis)

    # 6. Assemble report
    logger.info("📝 Assembling comprehensive HTML and Markdown report...")
    report = report_builder.build_report(dataset, analysis, insights, chart_path)

    # Save local previews
    preview_html_path = TEMP_DIR / "preview_post.html"
    preview_md_path = TEMP_DIR / "preview_report.md"
    with open(preview_html_path, "w", encoding="utf-8") as f:
        f.write(report.html_content)
    with open(preview_md_path, "w", encoding="utf-8") as f:
        f.write(report.markdown_content)
    logger.info(f"Saved preview files to {preview_html_path} and {preview_md_path}")

    # 7. Always archive report to local markdown / reports directory
    md_publisher = MarkdownFilePublisher(reports_dir=REPORTS_DIR)
    md_publisher.publish(report)

    # 8. Publish to target blog
    if args.dry_run:
        logger.info("🔍 [DRY-RUN] Skipped remote blog publishing and history updating.")
        logger.info("Pipeline completed successfully in simulation mode!")
        return

    logger.info(f"🌐 Publishing report using platform: '{publisher_type}'...")
    if publisher_type == "wordpress_mail":
        publisher = WordPressMailPublisher()
        publisher.publish(report)
    elif publisher_type == "wordpress_rest":
        publisher = WordPressRestPublisher()
        publisher.publish(report)
    elif publisher_type == "markdown_only":
        logger.info("Blog publisher set to 'markdown_only'. Archiving to reports/ completed.")
    else:
        logger.warning(f"Unknown publisher type '{publisher_type}'. Falling back to markdown archive only.")

    # 9. Record history
    storage.record_post(report, platform=publisher_type)
    logger.info("✅ Pipeline executed and recorded successfully!")


if __name__ == "__main__":
    main()
