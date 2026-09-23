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


def test_visualizer_rq_aligned_charts(tmp_path):
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
    )

    angle = get_academic_context("japan_school_absenteeism_bullying", angle_id="absenteeism_ict_safetynet")

    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset, selected_angle=angle)

    vis = EduDataVisualizer(output_dir=tmp_path)
    sec_chart = vis.generate_secondary_chart(dataset, analysis, selected_angle=angle)

    assert sec_chart is not None
    assert sec_chart.exists()
    assert sec_chart.stat().st_size > 1000


def test_visualizer_advanced_analysis_charts(tmp_path):
    import numpy as np
    from src.academic_contexts import DatasetAcademicContext

    vis = EduDataVisualizer(output_dir=tmp_path)
    analyzer = EduDataAnalyzer()

    # 1. ANOVA Interaction Plot
    prefectures = ["A県", "B県", "C県", "D県"] * 4
    years = [2021] * 8 + [2024] * 8
    school_types = (["小学校"] * 4 + ["中学校"] * 4) * 2
    scores = [70.0 if s == "小学校" else 55.0 for s in school_types]

    df_anova = pd.DataFrame({
        "地域": prefectures,
        "年度": years,
        "学校区分": school_types,
        "正答率": scores,
    })
    ds_anova = EducationDataset(
        id="test_vis_anova",
        title="ANOVA可視化テスト",
        category="math",
        region="japan",
        source_name="文科省",
        source_url="https://example.com",
        description="ANOVAテスト",
        df=df_anova,
        metrics=["正答率"],
        time_col="年度",
        group_col="学校区分",
        unit="%",
    )
    angle_anova = DatasetAcademicContext(
        angle_id="a1",
        angle_name="ANOVA",
        title_theme="テーマ",
        academic_discipline="教育統計",
        analysis_method="two_way_anova",
        anova_dv="正答率",
        anova_factor_a="学校区分",
        anova_factor_b="年度",
        secondary_chart_type="anova_interaction",
    )
    res_anova = analyzer.analyze(ds_anova, selected_angle=angle_anova)
    chart_anova = vis.generate_secondary_chart(ds_anova, res_anova, selected_angle=angle_anova)
    assert chart_anova is not None
    assert chart_anova.exists()
    assert chart_anova.stat().st_size > 1000

    # 2. Multiple Regression Observed vs Predicted Plot
    np.random.seed(42)
    x1 = np.random.uniform(40, 90, 20)
    x2 = np.random.uniform(20, 80, 20)
    y = 10.0 + 0.5 * x1 + 0.3 * x2 + np.random.normal(0, 1.0, 20)
    df_reg = pd.DataFrame({"自治体": [f"市{i}" for i in range(20)], "学力": y, "意欲": x1, "活用": x2})
    ds_reg = EducationDataset(
        id="test_vis_reg",
        title="重回帰可視化テスト",
        category="math",
        region="japan",
        source_name="文科省",
        source_url="https://example.com",
        description="重回帰テスト",
        df=df_reg,
        metrics=["学力", "意欲", "活用"],
        group_col="自治体",
        unit="点",
    )
    angle_reg = DatasetAcademicContext(
        angle_id="a2",
        angle_name="Reg",
        title_theme="テーマ",
        academic_discipline="教育計量",
        analysis_method="multiple_regression",
        regression_y="学力",
        regression_x_list=["意欲", "活用"],
        secondary_chart_type="multiple_regression",
    )
    res_reg = analyzer.analyze(ds_reg, selected_angle=angle_reg)
    chart_reg = vis.generate_secondary_chart(ds_reg, res_reg, selected_angle=angle_reg)
    assert chart_reg is not None
    assert chart_reg.exists()
    assert chart_reg.stat().st_size > 1000

    # 3. No-Correlation Scatter Plot
    df_nc = pd.DataFrame({
        "年度": [2020, 2021, 2022, 2023, 2024],
        "支出": [3.4, 3.5, 3.4, 3.5, 3.4],
        "普及率": [80.0, 85.0, 90.0, 95.0, 98.0],
    })
    ds_nc = EducationDataset(
        id="test_vis_nc",
        title="無相関可視化テスト",
        category="ict",
        region="japan",
        source_name="文科省",
        source_url="https://example.com",
        description="無相関テスト",
        df=df_nc,
        metrics=["支出", "普及率"],
        time_col="年度",
        unit="%",
    )
    angle_nc = DatasetAcademicContext(
        angle_id="a3",
        angle_name="NC",
        title_theme="テーマ",
        academic_discipline="教育統計",
        analysis_method="no_correlation",
        no_corr_x="支出",
        no_corr_y="普及率",
        secondary_chart_type="no_correlation_scatter",
    )
    res_nc = analyzer.analyze(ds_nc, selected_angle=angle_nc)
    chart_nc = vis.generate_secondary_chart(ds_nc, res_nc, selected_angle=angle_nc)
    assert chart_nc is not None
    assert chart_nc.exists()
    assert chart_nc.stat().st_size > 1000




