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


def test_reporter_builds_dual_tables_and_figures(tmp_path):
    import numpy as np
    from src.academic_contexts import DatasetAcademicContext

    np.random.seed(42)
    x1 = np.random.uniform(40, 90, 20)
    x2 = np.random.uniform(20, 80, 20)
    y = 10.0 + 0.5 * x1 + 0.3 * x2 + np.random.normal(0, 1.0, 20)
    df_reg = pd.DataFrame({"自治体": [f"市{i}" for i in range(20)], "学力": y, "意欲": x1, "活用": x2})
    dataset = EducationDataset(
        id="test_dual_rep",
        title="重回帰デュアルレポートテスト",
        category="math",
        region="japan",
        source_name="文科省",
        source_url="https://example.com",
        description="重回帰レポートテスト",
        df=df_reg,
        metrics=["学力", "意欲", "活用"],
        group_col="自治体",
        unit="点",
    )
    angle = DatasetAcademicContext(
        angle_id="a2",
        angle_name="Reg",
        title_theme="テーマ",
        academic_discipline="教育計量",
        analysis_method="multiple_regression",
        regression_y="学力",
        regression_x_list=["意欲", "活用"],
        secondary_chart_type="multiple_regression",
    )

    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset, selected_angle=angle)

    chart1 = tmp_path / "chart1.png"
    chart1.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
    chart2 = tmp_path / "chart2.png"
    chart2.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")

    insights = EducationalInsights(
        executive_summary="重回帰サマリー",
        pedagogical_implications="重回帰授業示唆",
        future_challenges_and_policy="重回帰政策",
    )

    builder = EduReportBuilder()
    report = builder.build_report(
        dataset=dataset,
        analysis=analysis,
        insights=insights,
        chart_path=chart1,
        secondary_chart_path=chart2,
        selected_angle=angle,
    )

    # Check Table 1 and Table 2 in Markdown
    assert "### 表1" in report.markdown_content
    assert "### 表2" in report.markdown_content
    assert "重回帰分析の係数推定量" in report.markdown_content
    assert "ベイズファクター" in report.markdown_content

    # Check Figure 1 and Figure 2 in Markdown
    assert "### 図1" in report.markdown_content
    assert "### 図2" in report.markdown_content

    # Check HTML contains both tables and both base64 images
    assert "基本記述統計量一覧" in report.html_content
    assert "表2: 重回帰分析推定量" in report.html_content
    assert report.html_content.count("data:image/png;base64,") >= 2


