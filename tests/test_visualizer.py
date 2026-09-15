from pathlib import Path
import pandas as pd
import pytest

from src.analyzer import EduDataAnalyzer
from src.config import TEMP_DIR
from src.fetchers.base import EducationDataset
from src.visualizer import EduDataVisualizer


def test_visualizer_generate_trend_chart(tmp_path):
    df = pd.DataFrame({
        "年度": [2021, 2022, 2023, 2024],
        "算数正答率": [65.0, 68.0, 71.0, 74.0],
    })
    dataset = EducationDataset(
        id="test_vis_math",
        title="テスト可視化算数",
        category="math",
        region="japan",
        source_name="テスト出典",
        source_url="https://example.com",
        description="テスト",
        df=df,
        metrics=["算数正答率"],
        time_col="年度",
        recommended_chart="trend_line",
        unit="%",
    )

    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    vis = EduDataVisualizer(output_dir=tmp_path)
    chart_path = vis.generate_chart(dataset, analysis)

    assert chart_path.exists()
    assert chart_path.suffix == ".png"
    assert chart_path.stat().st_size > 1000  # Non-empty image file


def test_visualizer_generate_ranking_chart(tmp_path):
    df = pd.DataFrame({
        "国名": ["日本", "シンガポール", "エストニア", "アメリカ"],
        "プログラミング保有率": [14.6, 24.5, 25.8, 18.0],
    })
    dataset = EducationDataset(
        id="test_vis_ranking",
        title="テスト可視化ランキング",
        category="info",
        region="global",
        source_name="テスト出典",
        source_url="https://example.com",
        description="テスト",
        df=df,
        metrics=["プログラミング保有率"],
        group_col="国名",
        recommended_chart="ranking_bar",
        unit="%",
    )

    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    vis = EduDataVisualizer(output_dir=tmp_path)
    chart_path = vis.generate_chart(dataset, analysis)

    assert chart_path.exists()
    assert chart_path.stat().st_size > 1000


def test_visualizer_generate_secondary_chart(tmp_path):
    df = pd.DataFrame({
        "年度": [2021, 2022, 2023, 2024],
        "算数正答率": [65.0, 68.0, 71.0, 74.0],
        "勉強肯定率": [60.0, 62.0, 64.0, 66.0],
    })
    dataset = EducationDataset(
        id="test_vis_secondary",
        title="テスト可視化二次チャート",
        category="math",
        region="japan",
        source_name="テスト出典",
        source_url="https://example.com",
        description="テスト",
        df=df,
        metrics=["算数正答率", "勉強肯定率"],
        time_col="年度",
        recommended_chart="trend_line",
        unit="%",
    )

    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    vis = EduDataVisualizer(output_dir=tmp_path)
    sec_chart_path = vis.generate_secondary_chart(dataset, analysis)

    assert sec_chart_path is not None
    assert sec_chart_path.exists()
    assert sec_chart_path.stat().st_size > 1000


def test_compute_trend_ci_errors():
    import numpy as np
    import pandas as pd
    from src.visualizer import EduDataVisualizer

    # Linear series test
    df = pd.DataFrame({
        "年度": [2020, 2021, 2022, 2023, 2024],
        "正答率": [60.0, 62.0, 63.5, 65.0, 67.0],
    })
    ci_err = EduDataVisualizer._compute_trend_ci_errors(df, "年度", "正答率", 2.0)

    assert len(ci_err) == len(df)
    assert np.all(ci_err > 0)
    # The middle points generally have smaller SE in regression CI than outer points
    assert ci_err[2] <= ci_err[0]
    assert ci_err[2] <= ci_err[4]


