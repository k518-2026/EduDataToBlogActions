import pytest
import pandas as pd
from src.insights import parse_insights_json, EducationalInsights
from src.utils import clean_insight_text
from src.reporter import EduReportBuilder
from src.analyzer import EduDataAnalyzer
from src.fetchers.base import EducationDataset


def test_clean_insight_text_user_corrupted_case():
    raw_corrupted = (
        '{"executive_summary":"2018年から2024年にかけて、GIGAスクール構想の下で端末の日常的利用率（週3日以上）は劇的に上昇しました。'
        '小学校では15.2%から91.8%（CAGR 35.0%）...校種ごとの活用と指導力の乖離が顕著な注目点となっています。","pedagogical_implicatio'
    )
    cleaned = clean_insight_text(raw_corrupted)
    assert not cleaned.startswith('{"executive_summary":"')
    assert not cleaned.startswith('executive_summary')
    assert not cleaned.endswith('pedagogical_implicatio')
    assert not cleaned.endswith('",')
    assert "2018年から2024年にかけて" in cleaned
    assert "校種ごとの活用と指導力の乖離が顕著な注目点となっています。" in cleaned


def test_clean_insight_text_partial_key_residue():
    text = 'ns":"現場での指導力向上が急務です。"}'
    cleaned = clean_insight_text(text)
    assert cleaned == "現場での指導力向上が急務です。"


def test_clean_insight_text_escaped_characters():
    text = r'これは\"引用文\"です。\n次の行です。'
    cleaned = clean_insight_text(text)
    assert 'これは"引用文"です。' in cleaned
    assert "次の行です。" in cleaned
    assert r"\n" not in cleaned
    assert r'\"' not in cleaned


def test_parse_insights_json_valid():
    raw = '''{
        "executive_summary": "サマリーです。",
        "pedagogical_implications": "指導実践です。",
        "future_challenges_and_policy": "政策展望です。"
    }'''
    res = parse_insights_json(raw)
    assert res["executive_summary"] == "サマリーです。"
    assert res["pedagogical_implications"] == "指導実践です。"
    assert res["future_challenges_and_policy"] == "政策展望です。"


def test_parse_insights_json_with_markdown_fences():
    raw = '''```json
    {
        "executive_summary": "マークダウンサマリー",
        "pedagogical_implications": "マークダウン示唆",
        "future_challenges_and_policy": "マークダウン政策"
    }
    ```'''
    res = parse_insights_json(raw)
    assert res["executive_summary"] == "マークダウンサマリー"
    assert res["pedagogical_implications"] == "マークダウン示唆"
    assert res["future_challenges_and_policy"] == "マークダウン政策"


def test_parse_insights_json_truncated_user_case():
    raw = (
        '{"executive_summary":"2018年から2024年にかけて、端末利用率は上昇しました。","pedagogical_implicatio'
    )
    res = parse_insights_json(raw)
    assert res["executive_summary"] == "2018年から2024年にかけて、端末利用率は上昇しました。"
    assert res["pedagogical_implications"] == ""
    assert res["future_challenges_and_policy"] == ""


def test_parse_insights_json_unescaped_newlines():
    raw = '{\n"executive_summary": "1行目\n2行目",\n"pedagogical_implications": "指導\n示唆",\n"future_challenges_and_policy": "政策\n提言"\n}'
    res = parse_insights_json(raw)
    assert "1行目" in res["executive_summary"]
    assert "2行目" in res["executive_summary"]


def test_reporter_sanitizes_corrupted_insights(tmp_path):
    df = pd.DataFrame({"年度": [2023, 2024], "指標": [50.0, 60.0]})
    dataset = EducationDataset(
        id="test_sanitization",
        title="端末利用率の推移",
        category="ict",
        region="japan",
        source_name="文部科学省",
        source_url="https://example.com",
        description="テストデータ",
        df=df,
        metrics=["指標"],
        time_col="年度",
        unit="%",
    )
    analysis = EduDataAnalyzer().analyze(dataset)
    dummy_chart = tmp_path / "chart.png"
    dummy_chart.write_bytes(b"dummy")

    corrupted_insights = EducationalInsights(
        executive_summary='{"executive_summary":"端末利用率は劇的に向上しました。","pedagogical_implicatio',
        pedagogical_implications='ns":"授業内での対話的活動を深める必要があります。"}',
        future_challenges_and_policy='{"future_challenges_and_policy":"地域間格差の是正が求められます。"}',
    )

    builder = EduReportBuilder()
    report = builder.build_report(dataset, analysis, corrupted_insights, dummy_chart)

    for content in (report.markdown_content, report.html_content):
        assert '{"executive_summary":' not in content
        assert '","pedagogical_implicatio' not in content
        assert 'ns":' not in content
        assert '{"future_challenges_and_policy":' not in content
        assert "端末利用率は劇的に向上しました。" in content
        assert "授業内での対話的活動を深める必要があります。" in content
        assert "地域間格差の是正が求められます。" in content
