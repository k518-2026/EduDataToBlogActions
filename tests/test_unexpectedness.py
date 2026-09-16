"""
Unit tests for counter-intuitive insights, unexpected findings, and anti-monotony features.
"""
from pathlib import Path
import pandas as pd
import pytest

from src.academic_paper import AcademicPaperGenerator
from src.analyzer import EduDataAnalyzer
from src.fetchers.base import EducationDataset
from src.fetchers.catalog import DatasetCatalog
from src.insights import EducationalInsights, parse_insights_json
from src.reporter import EduReportBuilder


def test_parse_insights_json_with_counter_intuitive_finding():
    """Verifies that parse_insights_json extracts counter_intuitive_finding properly."""
    raw = '''{
        "executive_summary": "全体要約です。",
        "counter_intuitive_finding": "正答率が高いのに嫌いが増えるという意外な逆説が判明しました。",
        "pedagogical_implications": "あえて誤答を共有する指導法が有効です。",
        "future_challenges_and_policy": "端末充足の裏で広がる活用格差が課題です。"
    }'''
    res = parse_insights_json(raw)
    assert res["executive_summary"] == "全体要約です。"
    assert "意外な逆説" in res["counter_intuitive_finding"]
    assert res["pedagogical_implications"] == "あえて誤答を共有する指導法が有効です。"
    assert res["future_challenges_and_policy"] == "端末充足の裏で広がる活用格差が課題です。"


def test_reporter_renders_counter_intuitive_paradox(tmp_path):
    """Verifies that EduReportBuilder outputs the counter-intuitive paradox section in both MD and HTML."""
    df = pd.DataFrame({
        "年度": [2021, 2022, 2023],
        "得点": [520, 525, 530],
    })
    dataset = EducationDataset(
        id="test_ds",
        title="テスト教育調査",
        category="math",
        region="japan",
        source_name="テスト機関",
        source_url="https://example.com",
        description="概要",
        df=df,
        metrics=["得点"],
        time_col="年度",
        unit="点",
    )
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    dummy_chart = tmp_path / "chart.png"
    dummy_chart.write_bytes(b"dummy")

    insights = EducationalInsights(
        executive_summary="サマリーです。",
        pedagogical_implications="指導示唆です。",
        future_challenges_and_policy="政策展望です。",
        counter_intuitive_finding="【常識とデータの逆説】高得点層ほど自己効力感が低迷するパラドックス。",
    )

    builder = EduReportBuilder()
    report = builder.build_report(dataset, analysis, insights, dummy_chart)

    # Check Markdown
    assert "⚡ データが暴く意外な事実・常識の逆説（教育パラドックス）" in report.markdown_content
    assert "高得点層ほど自己効力感が低迷するパラドックス" in report.markdown_content

    # Check HTML
    assert "⚡ データが暴く意外な事実・常識の逆説（教育パラドックス）" in report.html_content
    assert "高得点層ほど自己効力感が低迷するパラドックス" in report.html_content


def test_analyzer_detects_unexpected_patterns():
    """Verifies that EduDataAnalyzer flags rapid trends, stagnation, and divergence."""
    # 1. Divergence: Metric 1 goes up significantly, Metric 2 drops
    df = pd.DataFrame({
        "年度": [2020, 2021, 2022, 2023, 2024],
        "配備率": [20.0, 40.0, 60.0, 80.0, 100.0],   # Rapid rise
        "好意度": [80.0, 75.0, 70.0, 65.0, 60.0],     # Decline
    })
    dataset = EducationDataset(
        id="test_divergence",
        title="乖離テストデータ",
        category="info",
        region="japan",
        source_name="文部科学省",
        source_url="https://example.com",
        description="乖離テスト",
        df=df,
        metrics=["配備率", "好意度"],
        time_col="年度",
        unit="%",
    )
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    insights_text = "\n".join(analysis.key_insights)
    assert "⚡ 急伸長トレンド" in insights_text or "推移トレンド" in insights_text
    assert "⚡ 意外な乖離（逆相関推移）" in insights_text


def test_academic_prompt_anti_monotony_guidelines():
    """Verifies that _build_academic_prompt includes strict anti-monotony and counter-intuitive RQ/discussion rules."""
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_timss_math_science")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    paper_gen = AcademicPaperGenerator()
    prompt = paper_gen._build_academic_prompt(dataset, analysis)

    assert "★【論文の単調さの完全打破と「意外性・学術的緊張」の徹底（極めて重要）】" in prompt
    assert "★【単調なRQの完全禁止】" in prompt
    assert "★【考察の弁証法的高度化：単調な共通点・相違点の羅列を完全禁止】" in prompt
    assert "パラドックス" in prompt
    assert "深層メカニズム" in prompt
