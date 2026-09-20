from pathlib import Path
import pandas as pd
import pytest

from src.analyzer import EduDataAnalyzer
from src.fetchers.base import EducationDataset
from src.insights import EducationalInsights
from src.reporter import EduReportBuilder


def test_reporter_builds_valid_documents(tmp_path):
    df = pd.DataFrame({
        "年度": [2022, 2023, 2024],
        "正答率": [63.3, 62.7, 63.6],
    })
    dataset = EducationDataset(
        id="test_reporter_ds",
        title="テスト算数レポート",
        category="math",
        region="japan",
        source_name="文部科学省",
        source_url="https://example.com",
        description="テストデータ概要",
        df=df,
        metrics=["正答率"],
        time_col="年度",
        unit="%",
    )

    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    dummy_chart = tmp_path / "chart_test.png"
    dummy_chart.write_bytes(b"dummy image bytes")

    insights = EducationalInsights(
        executive_summary="テストサマリーです。",
        pedagogical_implications="テスト授業示唆です。",
        future_challenges_and_policy="テスト政策提言です。",
    )

    builder = EduReportBuilder()
    report = builder.build_report(dataset, analysis, insights, dummy_chart)

    # Validate report attributes
    assert "テスト算数レポート" in report.title
    assert "【教育オープンデータ統計分析】" not in report.title
    assert "教育データ分析" in report.categories
    assert "算数数学教育" in report.categories

    # Validate Markdown
    assert f"# {dataset.title}" in report.markdown_content
    assert "テストサマリーです。" in report.markdown_content
    assert "正答率" in report.markdown_content
    assert "データ系列数 (K)" in report.markdown_content
    assert "分析データ規模:" in report.markdown_content
    assert "💻 統計処理に利用した Python スクリプト" in report.markdown_content
    assert "import pandas as pd" in report.python_code

    # Validate HTML
    assert f"[title {report.title}]" in report.html_content
    assert "[status publish]" in report.html_content
    assert "data:image/png;base64," in report.html_content
    assert "テスト授業示唆です。" in report.html_content
    assert ".pyファイルをダウンロード" in report.html_content

