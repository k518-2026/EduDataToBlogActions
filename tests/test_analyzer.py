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


def test_apa_formatting():
    from src.analyzer import format_apa_p, format_apa_stat

    # p-value formatting (omit leading zero, < .001)
    assert format_apa_p(0.0004) == "< .001"
    assert format_apa_p(0.0498) == "= .050"
    assert format_apa_p(0.001) == "= .001"
    assert format_apa_p(0.85) == "= .850"

    # Statistics bounded by 1 (e.g. r, R2, eta_p2, beta) - strictly omit leading zero
    assert format_apa_stat(0.612, decimals=2, bounded=True) == ".61"
    assert format_apa_stat(-0.456, decimals=2, bounded=True) == "-.46"
    assert format_apa_stat(1.0, decimals=2, bounded=True) == "1.00"

    # Statistics unbounded (e.g. t, F, VIF) - include leading zero
    assert format_apa_stat(3.456, decimals=2, bounded=False) == "3.46"
    assert format_apa_stat(0.85, decimals=2, bounded=False) == "0.85"


def test_bayes_factor_calculators():
    from src.analyzer import (
        compute_bayes_factor_anova,
        compute_bayes_factor_regression,
        compute_bayes_factor_no_correlation,
    )

    # ANOVA: large F-stat gives large BF10
    bf_anova, interp_anova = compute_bayes_factor_anova(f_val=15.0, df_effect=2, df_error=60, n=63)
    assert bf_anova > 10.0
    assert "強い" in interp_anova or "決定的な" in interp_anova

    # ANOVA: near-zero F-stat gives small BF10 (< 0.33, H0 support)
    bf_anova_null, _ = compute_bayes_factor_anova(f_val=0.1, df_effect=1, df_error=50, n=52)
    assert bf_anova_null < 0.33

    # Multiple Regression: high R2 gives high BF10
    bf_reg, interp_reg = compute_bayes_factor_regression(r_squared=0.85, n=50, k=3)
    assert bf_reg > 100.0
    assert "強い" in interp_reg

    # No-Correlation: small r and moderate n gives high BF01 (evidence for null)
    bf10_nc, bf01_nc, interp_nc = compute_bayes_factor_no_correlation(r=0.05, n=47)
    assert bf01_nc > 3.0  # Moderate evidence for H0
    assert "無相関" in interp_nc


def test_analyzer_two_way_anova():
    import numpy as np
    from src.academic_contexts import DatasetAcademicContext

    # Construct balanced 2x2 factorial dataset with clear main effect
    prefectures = ["A県", "B県", "C県", "D県", "E県", "F県"] * 4
    years = [2021] * 12 + [2024] * 12
    # School types: 小学校 (12) vs 中学校 (12)
    school_types = (["小学校"] * 6 + ["中学校"] * 6) * 2
    scores = [70.0 + np.random.uniform(-1, 1) if s == "小学校" else 55.0 + np.random.uniform(-1, 1) for s in school_types]

    df = pd.DataFrame({
        "地域": prefectures,
        "年度": years,
        "学校区分": school_types,
        "正答率": scores,
    })

    dataset = EducationDataset(
        id="test_anova_ds",
        title="二要因分散分析テストデータ",
        category="math",
        region="japan",
        source_name="文科省",
        source_url="https://example.com",
        description="ANOVAテスト",
        df=df,
        metrics=["正答率"],
        time_col="年度",
        group_col="学校区分",
        unit="%",
    )

    angle = DatasetAcademicContext(
        angle_id="anova_test_angle",
        angle_name="二要因分散分析検証",
        title_theme="学校区分と年次の要因効果",
        academic_discipline="教育統計学",
        analysis_method="two_way_anova",
        anova_dv="正答率",
        anova_factor_a="学校区分",
        anova_factor_b="年度",
        secondary_chart_type="anova_interaction",
    )

    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(dataset, selected_angle=angle)

    assert res.two_way_anova is not None
    assert res.two_way_anova.dv == "正答率"
    assert res.two_way_anova.factor_a == "学校区分"
    assert res.two_way_anova.main_effect_a.f_val > 5.0
    assert res.two_way_anova.main_effect_a.eta_sq_p > 0.1
    assert res.two_way_anova.main_effect_a.bf10 > 1.0


def test_analyzer_multiple_regression():
    import numpy as np
    from src.academic_contexts import DatasetAcademicContext

    np.random.seed(42)
    x1 = np.random.uniform(40, 90, 30)
    x2 = np.random.uniform(20, 80, 30)
    y = 10.0 + 0.5 * x1 + 0.3 * x2 + np.random.normal(0, 1.0, 30)

    df = pd.DataFrame({
        "自治体": [f"自治体{i}" for i in range(30)],
        "平均正答率": y,
        "勉強が好き肯定率": x1,
        "将来役立つ肯定率": x2,
    })

    dataset = EducationDataset(
        id="test_regression_ds",
        title="重回帰分析テストデータ",
        category="math",
        region="japan",
        source_name="文科省",
        source_url="https://example.com",
        description="重回帰テスト",
        df=df,
        metrics=["平均正答率", "勉強が好き肯定率", "将来役立つ肯定率"],
        group_col="自治体",
        unit="%",
    )

    angle = DatasetAcademicContext(
        angle_id="regression_test_angle",
        angle_name="多変量因果連動性の重回帰分析",
        title_theme="意欲指標が学力に及ぼす影響",
        academic_discipline="教育計量学",
        analysis_method="multiple_regression",
        regression_y="平均正答率",
        regression_x_list=["勉強が好き肯定率", "将来役立つ肯定率"],
        secondary_chart_type="multiple_regression",
    )

    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(dataset, selected_angle=angle)

    assert res.multiple_regression is not None
    assert res.multiple_regression.y_metric == "平均正答率"
    assert res.multiple_regression.r_squared > 0.8
    assert res.multiple_regression.adj_r_squared > 0.8
    assert res.multiple_regression.f_val > 10.0
    assert res.multiple_regression.bf10 > 10.0
    assert len(res.multiple_regression.coefficients) == 2  # x1, x2


def test_analyzer_no_correlations():
    from src.academic_contexts import DatasetAcademicContext

    df = pd.DataFrame({
        "年度": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
        "教育支出対GDP比": [3.4, 3.5, 3.4, 3.6, 3.5, 3.4, 3.5],
        "インターネット利用率": [82.1, 85.3, 89.0, 92.5, 94.2, 95.8, 97.0],
    })

    dataset = EducationDataset(
        id="test_no_corr_ds",
        title="無相関分析テストデータ",
        category="ict",
        region="global",
        source_name="世界銀行",
        source_url="https://example.com",
        description="無相関テスト",
        df=df,
        metrics=["教育支出対GDP比", "インターネット利用率"],
        time_col="年度",
        unit="%",
    )

    angle = DatasetAcademicContext(
        angle_id="no_corr_test_angle",
        angle_name="支出と接続性の独立性検証",
        title_theme="教育支出とネット利用率の無相関検証",
        academic_discipline="教育経済学",
        analysis_method="no_correlation",
        no_corr_x="教育支出対GDP比",
        no_corr_y="インターネット利用率",
        secondary_chart_type="no_correlation_scatter",
    )

    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(dataset, selected_angle=angle)

    assert len(res.no_correlations) >= 1
    nc = res.no_correlations[0]
    assert nc.metric_x == "教育支出対GDP比"
    assert nc.metric_y == "インターネット利用率"
    assert nc.bf01 > 0.0


