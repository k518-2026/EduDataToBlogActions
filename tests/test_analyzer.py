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
