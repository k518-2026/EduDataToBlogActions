import pandas as pd
import pytest

from src.analyzer import EduDataAnalyzer
from src.fetchers.base import EducationDataset


def test_analyzer_descriptive_stats():
    df = pd.DataFrame({
        "年度": [2021, 2022, 2023, 2024],
        "正答率": [60.0, 65.0, 70.0, 75.0],
        "活用率": [40.0, 50.0, 60.0, 70.0],
    })
    dataset = EducationDataset(
        id="test_math",
        title="テスト算数データ",
        category="math",
        region="japan",
        source_name="テスト機関",
        source_url="https://example.com",
        description="テスト用データ",
        df=df,
        metrics=["正答率", "活用率"],
        time_col="年度",
        recommended_chart="trend_line",
        unit="%",
    )

    analyzer = EduDataAnalyzer()
    result = analyzer.analyze(dataset)

    assert "正答率" in result.descriptive_stats
    stats_acc = result.descriptive_stats["正答率"]
    assert stats_acc.count == 4
    assert stats_acc.mean == 67.5
    assert stats_acc.min_val == 60.0
    assert stats_acc.max_val == 75.0

    # Check trend
    assert len(result.trends) >= 1
    tr = [t for t in result.trends if t.metric == "正答率"][0]
    assert tr.start_val == 60.0
    assert tr.end_val == 75.0
    assert tr.diff == 15.0
    assert tr.slope == 5.0
    assert tr.r_squared == 1.0  # Perfectly linear

    # Check correlation
    assert len(result.correlations) == 1
    cr = result.correlations[0]
    assert cr.pearson_r == 1.0


def test_analyzer_group_rankings():
    df = pd.DataFrame({
        "国名": ["日本", "シンガポール", "アメリカ"],
        "数学得点": [530.0, 570.0, 480.0],
    })
    dataset = EducationDataset(
        id="test_ranking",
        title="国別得点テスト",
        category="math",
        region="global",
        source_name="OECD",
        source_url="https://example.com",
        description="ランキングテスト",
        df=df,
        metrics=["数学得点"],
        group_col="国名",
        recommended_chart="ranking_bar",
        unit="点",
    )

    analyzer = EduDataAnalyzer()
    result = analyzer.analyze(dataset)

    assert "数学得点" in result.rankings
    ranks = result.rankings["数学得点"]
    assert ranks[0][0] == "シンガポール"
    assert ranks[0][1] == 570.0
    assert ranks[-1][0] == "アメリカ"
    assert ranks[-1][1] == 480.0


def test_is_collinear_or_redundant_pair():
    from src.analyzer import is_collinear_or_redundant_pair

    # Count vs rate of same concept -> Collinear / Redundant
    assert is_collinear_or_redundant_pair("不登校児童生徒数", "千人あたり不登校率") is True
    assert is_collinear_or_redundant_pair("千人あたり不登校率", "不登校児童生徒数") is True
    assert is_collinear_or_redundant_pair("いじめ認知件数", "千人あたりいじめ認知件数") is True
    assert is_collinear_or_redundant_pair("児童数", "児童割合") is True

    # Same metric vs same metric
    assert is_collinear_or_redundant_pair("不登校児童生徒数", "不登校児童生徒数") is True

    # Different distinct concepts -> NOT Collinear
    assert is_collinear_or_redundant_pair("不登校児童生徒数", "ICT出席扱い生徒数") is False
    assert is_collinear_or_redundant_pair("不登校児童生徒数", "いじめ認知件数") is False
    assert is_collinear_or_redundant_pair("正答率", "活用率") is False
    assert is_collinear_or_redundant_pair("小学校", "中学校") is False


def test_analyzer_rq_alignment_and_metadata():
    from src.academic_contexts import get_academic_context

    df = pd.DataFrame({
        "年度": [2019, 2020, 2021, 2022, 2023],
        "不登校児童生徒数": [181272, 196127, 244940, 299048, 346482],
        "千人あたり不登校率": [18.8, 20.5, 25.7, 31.7, 37.1],
        "ICT出席扱い生徒数": [3956, 5214, 10103, 10409, 14000],
    })
    dataset = EducationDataset(
        id="japan_school_absenteeism_bullying",
        title="児童生徒の問題行動・不登校等生徒指導上の諸課題に関する調査",
        category="support",
        region="japan",
        source_name="文部科学省",
        source_url="https://example.com",
        description="不登校データ",
        df=df,
        metrics=["不登校児童生徒数", "千人あたり不登校率", "ICT出席扱い生徒数"],
        time_col="年度",
        recommended_chart="trend_line",
        unit="人",
        observation_unit="年度×学校種別集計系列",
        sample_population_note="全国の国公私立小・中・高等学校等を対象とする悉皆調査（約950万人規模）",
        sample_population_size="約950万人（悉皆調査）",
    )

    angle = get_academic_context("japan_school_absenteeism_bullying", angle_id="absenteeism_ict_safetynet")

    analyzer = EduDataAnalyzer()
    result = analyzer.analyze(dataset, selected_angle=angle)

    # 1. Verify population metadata is preserved in result
    assert result.observation_unit == "年度×学校種別集計系列"
    assert "約950万人" in result.sample_population_note
    assert result.sample_population_size == "約950万人（悉皆調査）"

    # 2. Verify collinear pairs (e.g. 不登校児童生徒数 vs 千人あたり不登校率) are excluded
    pair_tuples = [(c.metric_x, c.metric_y) for c in result.correlations]
    assert ("不登校児童生徒数", "千人あたり不登校率") not in pair_tuples
    assert ("千人あたり不登校率", "不登校児童生徒数") not in pair_tuples

    # 3. Verify RQ target scatter pair is placed at index 0 of correlations
    assert len(result.correlations) > 0
    top_corr = result.correlations[0]
    assert (top_corr.metric_x, top_corr.metric_y) in [
        ("不登校児童生徒数", "ICT出席扱い生徒数"),
        ("ICT出席扱い生徒数", "不登校児童生徒数"),
    ]
    assert top_corr.pearson_r > 0.5

