from __future__ import annotations

"""
Statistical Analysis Engine for Educational Datasets.
Performs descriptive statistics, trend estimation, correlations, and comparative rankings.
"""
from dataclasses import dataclass, field
import logging
import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats

from src.fetchers.base import EducationDataset
from src.utils import format_bayes_factor, resolve_metric_unit

logger = logging.getLogger(__name__)


@dataclass
class MetricSummary:
    name: str
    count: int
    mean: float
    std: float
    median: float
    min_val: float
    max_val: float
    q25: float
    q75: float
    iqr: float
    skewness: float


@dataclass
class TrendResult:
    metric: str
    group_name: Optional[str]
    start_time: Any
    start_val: float
    end_time: Any
    end_val: float
    diff: float
    pct_change: float
    cagr: Optional[float]
    slope: float
    r_squared: float
    bf10: Optional[float] = None
    bf_interpretation: Optional[str] = None


@dataclass
class CorrelationResult:
    metric_x: str
    metric_y: str
    pearson_r: float
    p_value: float
    interpretation: str
    bf10: float = 1.0
    bf_interpretation: str = ""


@dataclass
class AnovaEffect:
    name: str
    ss: float
    df: int
    ms: float
    f_val: float
    p_val: float
    eta_sq_p: float
    bf10: float
    bf_interpretation: str


@dataclass
class TwoWayAnovaResult:
    dv: str
    factor_a: str
    factor_b: str
    main_effect_a: AnovaEffect
    main_effect_b: AnovaEffect
    interaction: AnovaEffect
    error_df: int
    error_ss: float
    error_ms: float
    factor_b_is_binned: bool = False
    factor_b_levels: List[str] = field(default_factory=list)


@dataclass
class RegressionCoeff:
    variable: str
    b: float
    se: float
    beta: float
    t_val: float
    p_val: float
    vif: float
    bf10: float
    bf_interpretation: str


@dataclass
class MultipleRegressionResult:
    y_metric: str
    x_metrics: List[str]
    r_squared: float
    adj_r_squared: float
    f_val: float
    p_val: float
    df_model: int
    df_resid: int
    bf10: float
    bf_interpretation: str
    coefficients: List[RegressionCoeff]


@dataclass
class NoCorrelationResult:
    metric_x: str
    metric_y: str
    pearson_r: float
    t_val: float
    df: int
    p_val: float
    bf10: float
    bf01: float
    interpretation: str
    bf_interpretation: str


def compute_bayes_factor_correlation(r: float, n: int) -> Tuple[float, str]:
    """
    Computes JZS Bayes Factor (BF10) for Pearson correlation coefficient r and sample size n
    using Wetzels & Wagenmakers (2012) / Ly et al. (2016) integral formulation.
    Returns (bf10, interpretation).
    """
    if n <= 2 or not np.isfinite(r):
        return 1.0, "証拠不十分（N数不足）"

    abs_r = abs(r)
    if abs_r >= 0.99999:
        return 99999.0, "極めて強い証拠（H1支持）"

    # Clamp extremely small r to avoid log underflow
    effective_r = max(abs_r, 1e-6)

    try:
        from scipy.integrate import quad
        def integrand(g):
            return np.exp(
                ((n - 2) / 2) * np.log(1 + g)
                + (-(n - 1) / 2) * np.log(1 + (1 - effective_r**2) * g)
                + (-1.5) * np.log(g)
                + (-n / (2 * g))
            )
        val, _ = quad(integrand, 0, np.inf)
        from scipy.special import gamma
        bf10 = float(np.sqrt(n / 2.0) / gamma(0.5) * val)
    except Exception:
        bf10 = 1.0

    if not np.isfinite(bf10) or bf10 < 0:
        bf10 = 1.0

    # Interpret BF10 following Jeffreys (1961) / Lee & Wagenmakers (2013) classification
    if bf10 >= 100.0:
        interp = "極めて強い証拠（H1支持）"
    elif bf10 >= 30.0:
        interp = "非常に強い証拠（H1支持）"
    elif bf10 >= 10.0:
        interp = "強い証拠（H1支持）"
    elif bf10 >= 3.0:
        interp = "中程度の証拠（H1支持）"
    elif bf10 >= 1.0:
        interp = "弱い証拠（H1支持: 逸話的）"
    elif bf10 >= 1.0 / 3.0:
        interp = "弱い証拠（H0支持: 逸話的）"
    elif bf10 >= 1.0 / 10.0:
        interp = "中程度の証拠（H0支持）"
    elif bf10 >= 1.0 / 30.0:
        interp = "強い証拠（H0支持）"
    else:
        interp = "極めて強い証拠（H0支持）"

    return round(bf10, 2), interp


def compute_bayes_factor_anova(
    f_val: float,
    df1: int = 1,
    df2: int = 10,
    n: int = 20,
    df_effect: Optional[int] = None,
    df_error: Optional[int] = None,
) -> Tuple[float, str]:
    """
    Computes Bayes Factor (BF10) for ANOVA effect using Wagenmakers (2007) / Masson (2011)
    BIC approximation: delta_BIC = n * ln(1 - eta_p^2) + df1 * ln(n), BF10 = exp(-delta_BIC / 2).
    """
    if df_effect is not None:
        df1 = df_effect
    if df_error is not None:
        df2 = df_error

    if n <= df1 + 1 or not np.isfinite(f_val) or f_val <= 0:
        return 1.0, "証拠不十分（N数不足またはF<=0）"

    denom = f_val * df1 + df2
    if denom <= 0:
        return 1.0, "証拠不十分"
    eta_sq_p = (f_val * df1) / denom
    eta_sq_p = max(0.0, min(0.99999, eta_sq_p))

    try:
        delta_bic = n * math.log(1.0 - eta_sq_p) + df1 * math.log(n)
        bf10 = math.exp(-delta_bic / 2.0)
    except Exception:
        bf10 = 1.0

    if not np.isfinite(bf10) or bf10 < 0:
        bf10 = 1.0
    bf10 = min(bf10, 99999.0)

    if bf10 >= 100.0:
        interp = "極めて強い証拠（H1支持）"
    elif bf10 >= 30.0:
        interp = "非常に強い証拠（H1支持）"
    elif bf10 >= 10.0:
        interp = "強い証拠（H1支持）"
    elif bf10 >= 3.0:
        interp = "中程度の証拠（H1支持）"
    elif bf10 >= 1.0:
        interp = "弱い証拠（H1支持: 逸話的）"
    elif bf10 >= 1.0 / 3.0:
        interp = "弱い証拠（H0支持: 逸話的）"
    elif bf10 >= 1.0 / 10.0:
        interp = "中程度の証拠（H0支持）"
    elif bf10 >= 1.0 / 30.0:
        interp = "強い証拠（H0支持）"
    else:
        interp = "極めて強い証拠（H0支持）"

    return round(bf10, 2), interp


def compute_bayes_factor_regression(
    r2: float = 0.0,
    n: int = 10,
    k: int = 1,
    r_squared: Optional[float] = None,
) -> Tuple[float, str]:
    """
    Computes Bayes Factor (BF10) for Multiple Linear Regression model
    using BIC approximation: delta_BIC = n * ln(1 - R^2) + k * ln(n), BF10 = exp(-delta_BIC / 2).
    """
    if r_squared is not None:
        r2 = r_squared
    if n <= k + 1 or not np.isfinite(r2):
        return 1.0, "証拠不十分（N数不足）"

    clamped_r2 = max(0.0, min(0.99999, r2))
    try:
        delta_bic = n * math.log(1.0 - clamped_r2) + k * math.log(n)
        bf10 = math.exp(-delta_bic / 2.0)
    except Exception:
        bf10 = 1.0

    if not np.isfinite(bf10) or bf10 < 0:
        bf10 = 1.0
    bf10 = min(bf10, 99999.0)

    if bf10 >= 100.0:
        interp = "極めて強い証拠（H1支持）"
    elif bf10 >= 30.0:
        interp = "非常に強い証拠（H1支持）"
    elif bf10 >= 10.0:
        interp = "強い証拠（H1支持）"
    elif bf10 >= 3.0:
        interp = "中程度の証拠（H1支持）"
    elif bf10 >= 1.0:
        interp = "弱い証拠（H1支持: 逸話的）"
    elif bf10 >= 1.0 / 3.0:
        interp = "弱い証拠（H0支持: 逸話的）"
    elif bf10 >= 1.0 / 10.0:
        interp = "中程度の証拠（H0支持）"
    elif bf10 >= 1.0 / 30.0:
        interp = "強い証拠（H0支持）"
    else:
        interp = "極めて強い証拠（H0支持）"

    return round(bf10, 2), interp


def compute_bayes_factor_no_correlation(r: float, n: int) -> Tuple[float, float, str]:
    """
    Computes BF10 and null-support BF01 (= 1/BF10) for evaluating independence / true lack of correlation.
    Returns (bf10, bf01, interpretation).
    """
    bf10, _ = compute_bayes_factor_correlation(r, n)
    bf01 = round(1.0 / bf10, 2) if bf10 > 0 else 99999.0

    if bf01 >= 100.0:
        interp = "極めて強い無相関・独立性の証拠（H0支持）"
    elif bf01 >= 30.0:
        interp = "非常に強い無相関・独立性の証拠（H0支持）"
    elif bf01 >= 10.0:
        interp = "強い無相関・独立性の証拠（H0支持）"
    elif bf01 >= 3.0:
        interp = "中程度の無相関・独立性の証拠（H0支持）"
    elif bf01 >= 1.0:
        interp = "弱い無相関の証拠（H0支持: 逸話的）"
    else:
        interp = "相関あり（対立仮説H1支持）"

    return bf10, bf01, interp


def format_apa_p(p: Any) -> str:
    """Formats p-value conforming strictly to APA 7th edition (omit leading zero, 3 decimal places, or < .001)."""
    try:
        p_val = float(p)
    except (ValueError, TypeError):
        return "= .050"
    if p_val < 0.001:
        return "< .001"
    s = f"{p_val:.3f}"
    if s.startswith("0."):
        return f"= {s[1:]}"
    if s.startswith("1.000"):
        return "> .999"
    return f"= {s}"


def format_apa_stat(val: Any, decimals: int = 2, bounded: bool = False) -> str:
    """
    Formats statistical value conforming to APA 7th edition.
    If bounded=True (e.g. r, R^2, eta_p^2 which cannot exceed 1.0), omits leading zero.
    """
    try:
        f_val = float(val)
    except (ValueError, TypeError):
        return ".00" if bounded else "0.00"
    sign = "-" if f_val < 0 else ""
    abs_v = abs(f_val)
    s = f"{abs_v:.{decimals}f}"
    if bounded:
        if s.startswith("0."):
            return f"{sign}{s[1:]}"
        elif s == "1.00" or s == "1.0":
            return f"{sign}{s}"
    return f"{sign}{s}"


@dataclass
class AnalysisResult:
    dataset_id: str
    dataset_title: str
    unit: str
    sample_size: int
    descriptive_stats: Dict[str, MetricSummary]
    trends: List[TrendResult]
    correlations: List[CorrelationResult]
    rankings: Dict[str, List[Tuple[str, float]]]
    key_insights: List[str]
    raw_df: pd.DataFrame
    observation_unit: str = ""
    sample_population_note: str = ""
    sample_population_size: str = ""
    rq_correlations: List[CorrelationResult] = field(default_factory=list)
    two_way_anova: Optional[TwoWayAnovaResult] = None
    multiple_regression: Optional[MultipleRegressionResult] = None
    no_correlations: List[NoCorrelationResult] = field(default_factory=list)
    primary_method: str = "correlation"


def is_collinear_or_redundant_pair(col_x: str, col_y: str) -> bool:
    """
    Determines if two metrics represent mathematically or conceptually redundant / collinear variables
    (e.g., headcount vs rate per 1,000 of the same metric, or derived sub-components).
    """
    if col_x == col_y:
        return True

    # Strip common prefixes/suffixes to find core root
    def extract_root(col: str) -> str:
        s = col
        for prefix in ["千人あたり", "在籍千人あたり", "全国", "公立", "1人1台"]:
            if s.startswith(prefix):
                s = s[len(prefix):]
        for suffix in ["児童生徒数", "生徒数", "児童数", "教員数", "入学者数", "人数", "総数", "数",
                       "率", "比率", "割合", "得点", "スコア", "平均正答率", "正答率", "肯定率"]:
            if s.endswith(suffix) and len(s) > len(suffix):
                s = s[:-len(suffix)]
                break
        return s.strip()

    root_x = extract_root(col_x)
    root_y = extract_root(col_y)

    # If roots match (e.g. "不登校" and "不登校", or "女性" and "女性")
    if root_x and root_y and (root_x == root_y or root_x in root_y or root_y in root_x):
        is_count_x = any(w in col_x for w in ["数", "人数", "総数"]) and not any(w in col_x for w in ["率", "比率", "割合", "千人"])
        is_rate_x = any(w in col_x for w in ["率", "比率", "割合", "千人あたり"])
        is_count_y = any(w in col_y for w in ["数", "人数", "総数"]) and not any(w in col_y for w in ["率", "比率", "割合", "千人"])
        is_rate_y = any(w in col_y for w in ["率", "比率", "割合", "千人あたり"])

        if (is_count_x and is_rate_y) or (is_rate_x and is_count_y):
            return True

    # Check for direct derivations (e.g. difference derived from components)
    if "得点差" in col_x and ("男子" in col_y or "女子" in col_y):
        return True
    if "得点差" in col_y and ("男子" in col_x or "女子" in col_x):
        return True

    return False


class EduDataAnalyzer:
    """Statistical analyzer for education datasets."""

    def analyze(
        self, dataset: EducationDataset, selected_angle: Optional[Any] = None
    ) -> AnalysisResult:
        df = dataset.df.copy()
        metrics = dataset.metrics
        time_col = dataset.time_col
        group_col = dataset.group_col

        # 1. Descriptive statistics
        desc_stats: Dict[str, MetricSummary] = {}
        for m in metrics:
            if m in df.columns and pd.api.types.is_numeric_dtype(df[m]):
                series = df[m].dropna()
                if len(series) > 0:
                    mean_val = float(series.mean())
                    std_val = float(series.std(ddof=1)) if len(series) > 1 else 0.0
                    median_val = float(series.median())
                    min_val = float(series.min())
                    max_val = float(series.max())
                    q25 = float(series.quantile(0.25))
                    q75 = float(series.quantile(0.75))
                    iqr = q75 - q25
                    skew_val = float(stats.skew(series)) if len(series) >= 3 else 0.0

                    desc_stats[m] = MetricSummary(
                        name=m,
                        count=len(series),
                        mean=round(mean_val, 2),
                        std=round(std_val, 2),
                        median=round(median_val, 2),
                        min_val=round(min_val, 2),
                        max_val=round(max_val, 2),
                        q25=round(q25, 2),
                        q75=round(q75, 2),
                        iqr=round(iqr, 2),
                        skewness=round(skew_val, 2),
                    )

        # 2. Longitudinal Trend analysis
        trends: List[TrendResult] = []
        if time_col and time_col in df.columns:
            # Sort chronologically
            df_sorted = df.sort_values(by=time_col)

            if group_col and group_col in df_sorted.columns:
                groups = df_sorted[group_col].unique()
                for grp in groups:
                    grp_sub = df_sorted[df_sorted[group_col] == grp]
                    for m in metrics:
                        if m in grp_sub.columns and len(grp_sub[m].dropna()) >= 2:
                            tr = self._compute_trend(grp_sub, time_col, m, group_name=str(grp))
                            if tr:
                                trends.append(tr)
            else:
                for m in metrics:
                    if m in df_sorted.columns and len(df_sorted[m].dropna()) >= 2:
                        tr = self._compute_trend(df_sorted, time_col, m)
                        if tr:
                            trends.append(tr)

        # 3. Correlation analysis
        correlations: List[CorrelationResult] = []
        num_cols = [m for m in metrics if m in df.columns and pd.api.types.is_numeric_dtype(df[m])]
        if len(num_cols) >= 2:
            for i in range(len(num_cols)):
                for j in range(i + 1, len(num_cols)):
                    col_x, col_y = num_cols[i], num_cols[j]
                    if is_collinear_or_redundant_pair(col_x, col_y):
                        logger.info(
                            f"Excluding collinear/redundant pair from correlation analysis: {col_x} vs {col_y}"
                        )
                        continue
                    sub = df[[col_x, col_y]].dropna()
                    if len(sub) >= 4:
                        r, p_val = stats.pearsonr(sub[col_x], sub[col_y])
                        interp = self._interpret_correlation(r)
                        bf10, bf_interp = compute_bayes_factor_correlation(float(r), len(sub))
                        correlations.append(
                            CorrelationResult(
                                metric_x=col_x,
                                metric_y=col_y,
                                pearson_r=round(float(r), 3),
                                p_value=round(float(p_val), 4),
                                interpretation=interp,
                                bf10=bf10,
                                bf_interpretation=bf_interp,
                            )
                        )

        # Prioritize the RQ target scatter pair if defined by selected_angle
        target_x = getattr(selected_angle, "scatter_x_metric", None)
        target_y = getattr(selected_angle, "scatter_y_metric", None)
        if target_x and target_y:
            has_target = any(
                (cr.metric_x == target_x and cr.metric_y == target_y)
                or (cr.metric_x == target_y and cr.metric_y == target_x)
                for cr in correlations
            )
            if not has_target and target_x in df.columns and target_y in df.columns:
                sub = df[[target_x, target_y]].dropna()
                if len(sub) >= 4:
                    r, p_val = stats.pearsonr(sub[target_x], sub[target_y])
                    interp = self._interpret_correlation(r)
                    bf10, bf_interp = compute_bayes_factor_correlation(float(r), len(sub))
                    correlations.insert(
                        0,
                        CorrelationResult(
                            metric_x=target_x,
                            metric_y=target_y,
                            pearson_r=round(float(r), 3),
                            p_value=round(float(p_val), 4),
                            interpretation=interp,
                            bf10=bf10,
                            bf_interpretation=bf_interp,
                        ),
                    )
            else:
                correlations.sort(
                    key=lambda cr: 0
                    if (
                        (cr.metric_x == target_x and cr.metric_y == target_y)
                        or (cr.metric_x == target_y and cr.metric_y == target_x)
                    )
                    else 1
                )

        # 4. Comparative rankings
        rankings: Dict[str, List[Tuple[str, float]]] = {}
        if group_col and group_col in df.columns:
            latest_df = df
            if time_col and time_col in df.columns:
                latest_time = df[time_col].max()
                latest_df = df[df[time_col] == latest_time]

            for m in metrics:
                if m in latest_df.columns and pd.api.types.is_numeric_dtype(latest_df[m]):
                    grp_rank = (
                        latest_df.groupby(group_col)[m]
                        .mean()
                        .sort_values(ascending=False)
                        .round(2)
                    )
                    rankings[m] = [(str(k), float(v)) for k, v in grp_rank.items()]

        # 5. Advanced Statistical Analysis (Two-way ANOVA, Multiple Linear Regression, No-Correlation)
        target_method = getattr(selected_angle, "analysis_method", None)

        anova_dv = getattr(selected_angle, "anova_dv", None)
        anova_fa = getattr(selected_angle, "anova_factor_a", None)
        anova_fb = getattr(selected_angle, "anova_factor_b", None)
        two_way_anova_res = self._compute_two_way_anova(
            df,
            dv=anova_dv,
            factor_a=anova_fa,
            factor_b=anova_fb,
            time_col=time_col,
            group_col=group_col,
            metrics=metrics,
        )

        reg_y = getattr(selected_angle, "regression_y", None)
        reg_xs = getattr(selected_angle, "regression_x_list", None)
        multiple_reg_res = self._compute_multiple_regression(
            df,
            y_col=reg_y,
            x_cols=reg_xs,
            metrics=metrics,
        )

        no_x = getattr(selected_angle, "no_corr_x", None)
        no_y = getattr(selected_angle, "no_corr_y", None)
        no_correlations_res = self._compute_no_correlations(
            df,
            metrics=metrics,
            target_x=no_x,
            target_y=no_y,
        )

        primary_method = "correlation"
        if target_method == "two_way_anova" and two_way_anova_res:
            primary_method = "two_way_anova"
        elif target_method == "multiple_regression" and multiple_reg_res:
            primary_method = "multiple_regression"
        elif target_method == "no_correlation" and no_correlations_res:
            primary_method = "no_correlation"
        elif target_method == "correlation":
            primary_method = "correlation"
        else:
            if target_method == "two_way_anova" and not two_way_anova_res:
                primary_method = "multiple_regression" if multiple_reg_res else "correlation"
            elif target_method == "multiple_regression" and not multiple_reg_res:
                primary_method = "two_way_anova" if two_way_anova_res else "correlation"
            elif target_method == "no_correlation" and not no_correlations_res:
                primary_method = "correlation"
            elif two_way_anova_res and group_col:
                primary_method = "two_way_anova"
            elif multiple_reg_res and len(num_cols) >= 3:
                primary_method = "multiple_regression"
            elif no_correlations_res:
                primary_method = "no_correlation"
            else:
                primary_method = "correlation"

        # 6. Extract automated key insights
        insights = self._generate_key_insights(
            dataset,
            desc_stats,
            trends,
            correlations,
            rankings,
            two_way_anova=two_way_anova_res,
            multiple_regression=multiple_reg_res,
            no_correlations=no_correlations_res,
            primary_method=primary_method,
        )

        rq_corrs = []
        if target_x and target_y:
            rq_corrs = [
                cr
                for cr in correlations
                if (cr.metric_x == target_x and cr.metric_y == target_y)
                or (cr.metric_x == target_y and cr.metric_y == target_x)
            ]

        return AnalysisResult(
            dataset_id=dataset.id,
            dataset_title=dataset.title,
            unit=dataset.unit,
            sample_size=len(df),
            descriptive_stats=desc_stats,
            trends=trends,
            correlations=correlations,
            rankings=rankings,
            key_insights=insights,
            raw_df=df,
            observation_unit=getattr(dataset, "observation_unit", ""),
            sample_population_note=getattr(dataset, "sample_population_note", ""),
            sample_population_size=getattr(dataset, "sample_population_size", ""),
            rq_correlations=rq_corrs,
            two_way_anova=two_way_anova_res,
            multiple_regression=multiple_reg_res,
            no_correlations=no_correlations_res,
            primary_method=primary_method,
        )

    def _compute_two_way_anova(
        self,
        df: pd.DataFrame,
        dv: Optional[str] = None,
        factor_a: Optional[str] = None,
        factor_b: Optional[str] = None,
        time_col: Optional[str] = None,
        group_col: Optional[str] = None,
        metrics: Optional[List[str]] = None,
    ) -> Optional[TwoWayAnovaResult]:
        """
        Computes Two-way ANOVA with main effects and interaction effect.
        If factor_b has single-observation cells, bins factor_b into categories (e.g. 前期 vs 後期)
        to ensure degrees of freedom for residual error variance.
        """
        try:
            from statsmodels.formula.api import ols
            from statsmodels.stats.anova import anova_lm
        except ImportError:
            logger.warning("statsmodels not available for Two-way ANOVA")
            return None

        # Determine DV
        target_dv = dv
        if not target_dv or target_dv not in df.columns:
            if metrics:
                for m in metrics:
                    if m in df.columns and pd.api.types.is_numeric_dtype(df[m]):
                        target_dv = m
                        break
        if not target_dv or target_dv not in df.columns:
            return None

        # Determine Factor A (group)
        target_fa = factor_a or group_col
        if not target_fa or target_fa not in df.columns:
            return None

        # Determine Factor B (time / secondary factor)
        target_fb = factor_b or time_col
        if not target_fb or target_fb not in df.columns:
            return None

        sub = df[[target_dv, target_fa, target_fb]].dropna().copy()
        if len(sub) < 6:
            return None

        n_total = len(sub)
        cell_counts = sub.groupby([target_fa, target_fb]).size()
        factor_b_is_binned = False
        factor_b_col = target_fb

        if cell_counts.max() == 1:
            # Need to bin Factor B into 2 levels (前期 / 後期)
            unique_b = sorted(sub[target_fb].unique())
            if len(unique_b) >= 2:
                mid = len(unique_b) // 2
                first_half = set(unique_b[:mid])
                sub["_binned_fb"] = sub[target_fb].apply(lambda x: "前期" if x in first_half else "後期")
                factor_b_col = "_binned_fb"
                factor_b_is_binned = True
            else:
                return None

        sub["_dv"] = pd.to_numeric(sub[target_dv], errors="coerce")
        sub["_fa"] = sub[target_fa].astype(str)
        sub["_fb"] = sub[factor_b_col].astype(str)
        sub = sub.dropna(subset=["_dv", "_fa", "_fb"])

        if len(sub["_fa"].unique()) < 2 or len(sub["_fb"].unique()) < 2:
            return None

        n_a = len(sub["_fa"].unique())
        n_b = len(sub["_fb"].unique())
        df_needed_interaction = n_a * n_b

        import warnings
        aov = None
        if len(sub) > df_needed_interaction:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = ols("_dv ~ C(_fa) + C(_fb) + C(_fa):C(_fb)", data=sub).fit()
                    aov = anova_lm(model, typ=2)
            except Exception as e:
                logger.warning(f"Two-way ANOVA interaction model fit failed: {e}. Trying additive model.")

        if aov is None:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = ols("_dv ~ C(_fa) + C(_fb)", data=sub).fit()
                    aov = anova_lm(model, typ=2)
            except Exception as e2:
                logger.warning(f"Two-way ANOVA additive model failed: {e2}")
                return None

        error_df = int(aov.loc["Residual", "df"]) if "Residual" in aov.index else max(n_total - 4, 1)
        error_ss = float(aov.loc["Residual", "sum_sq"]) if "Residual" in aov.index else 1.0
        error_ms = error_ss / error_df if error_df > 0 else 1.0

        def parse_effect(effect_key: str, effect_label: str) -> AnovaEffect:
            if effect_key in aov.index:
                ss = float(aov.loc[effect_key, "sum_sq"])
                df_eff = int(aov.loc[effect_key, "df"])
                ms = ss / df_eff if df_eff > 0 else ss
                f_val = float(aov.loc[effect_key, "F"]) if np.isfinite(aov.loc[effect_key, "F"]) else 0.0
                p_val = float(aov.loc[effect_key, "PR(>F)"]) if np.isfinite(aov.loc[effect_key, "PR(>F)"]) else 1.0
            else:
                ss, df_eff, ms, f_val, p_val = 0.0, 1, 0.0, 0.0, 1.0

            eta_p = ss / (ss + error_ss) if (ss + error_ss) > 0 else 0.0
            eta_p = max(0.0, min(0.9999, eta_p))
            bf10, interp = compute_bayes_factor_anova(f_val, df_eff, error_df, n_total)
            return AnovaEffect(
                name=effect_label,
                ss=round(ss, 2),
                df=df_eff,
                ms=round(ms, 2),
                f_val=round(f_val, 2),
                p_val=round(p_val, 4),
                eta_sq_p=round(eta_p, 3),
                bf10=bf10,
                bf_interpretation=interp,
            )

        eff_a = parse_effect("C(_fa)", f"要因A（{target_fa}）")
        eff_b = parse_effect("C(_fb)", f"要因B（{target_fb}）")
        eff_int = parse_effect("C(_fa):C(_fb)", f"交互作用（{target_fa} × {target_fb}）")

        levels_b = [str(x) for x in sorted(sub[factor_b_col].unique())]

        return TwoWayAnovaResult(
            dv=target_dv,
            factor_a=target_fa,
            factor_b=target_fb,
            main_effect_a=eff_a,
            main_effect_b=eff_b,
            interaction=eff_int,
            error_df=error_df,
            error_ss=round(error_ss, 2),
            error_ms=round(error_ms, 2),
            factor_b_is_binned=factor_b_is_binned,
            factor_b_levels=levels_b,
        )

    def _compute_multiple_regression(
        self,
        df: pd.DataFrame,
        y_col: Optional[str] = None,
        x_cols: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
    ) -> Optional[MultipleRegressionResult]:
        """
        Computes Multiple Linear Regression model with standardized coefficients (beta),
        t-statistics, p-values, VIF, and JZS/BIC Bayes Factors.
        """
        try:
            import statsmodels.api as sm
            from statsmodels.stats.outliers_influence import variance_inflation_factor
        except ImportError:
            logger.warning("statsmodels not available for Multiple Regression")
            return None

        num_metrics = [m for m in (metrics or list(df.columns)) if m in df.columns and pd.api.types.is_numeric_dtype(df[m])]
        if len(num_metrics) < 3:
            return None

        target_y = y_col if (y_col and y_col in df.columns) else num_metrics[0]
        target_xs = [x for x in (x_cols or num_metrics[1:3]) if x in df.columns and x != target_y]

        if len(target_xs) < 1:
            return None

        cols_needed = [target_y] + target_xs
        sub = df[cols_needed].dropna().copy()
        n = len(sub)
        k = len(target_xs)
        if n <= k + 2:
            return None

        y_series = pd.to_numeric(sub[target_y])
        X_df = sub[target_xs].apply(pd.to_numeric)
        X_const = sm.add_constant(X_df)

        try:
            model = sm.OLS(y_series, X_const).fit()
        except Exception as e:
            logger.warning(f"Multiple regression fit failed: {e}")
            return None

        r2 = float(model.rsquared)
        adj_r2 = float(model.rsquared_adj)
        f_val = float(model.fvalue) if np.isfinite(model.fvalue) else 0.0
        p_val = float(model.f_pvalue) if np.isfinite(model.f_pvalue) else 1.0
        df_model = int(model.df_model)
        df_resid = int(model.df_resid)

        model_bf10, model_bf_interp = compute_bayes_factor_regression(r2, n, k)

        std_y = float(y_series.std(ddof=1)) if n > 1 else 1.0
        coeffs: List[RegressionCoeff] = []

        for i, col in enumerate(target_xs):
            b_val = float(model.params[col])
            se_val = float(model.bse[col])
            t_val = float(model.tvalues[col])
            p_coef = float(model.pvalues[col])
            std_x = float(X_df[col].std(ddof=1)) if n > 1 else 1.0
            beta_val = b_val * (std_x / std_y) if std_y > 0 else 0.0

            try:
                if len(target_xs) > 1:
                    vif_val = float(variance_inflation_factor(X_const.values, i + 1))
                else:
                    vif_val = 1.0
            except Exception:
                vif_val = 1.0
            if not np.isfinite(vif_val) or vif_val < 1.0:
                vif_val = 1.0

            bf10_coef, interp_coef = compute_bayes_factor_anova(t_val**2, 1, df_resid, n)

            coeffs.append(
                RegressionCoeff(
                    variable=col,
                    b=round(b_val, 3),
                    se=round(se_val, 3),
                    beta=round(beta_val, 3),
                    t_val=round(t_val, 2),
                    p_val=round(p_coef, 4),
                    vif=round(vif_val, 2),
                    bf10=bf10_coef,
                    bf_interpretation=interp_coef,
                )
            )

        return MultipleRegressionResult(
            y_metric=target_y,
            x_metrics=target_xs,
            r_squared=round(r2, 3),
            adj_r_squared=round(adj_r2, 3),
            f_val=round(f_val, 2),
            p_val=round(p_val, 4),
            df_model=df_model,
            df_resid=df_resid,
            bf10=model_bf10,
            bf_interpretation=model_bf_interp,
            coefficients=coeffs,
        )

    def _compute_no_correlations(
        self,
        df: pd.DataFrame,
        metrics: List[str],
        target_x: Optional[str] = None,
        target_y: Optional[str] = None,
    ) -> List[NoCorrelationResult]:
        """
        Computes No-Correlation (null support) evaluation for metric pairs.
        Evaluates BF01 = 1 / BF10 to quantify evidence in favor of true independence (H0).
        """
        results: List[NoCorrelationResult] = []
        num_cols = [m for m in metrics if m in df.columns and pd.api.types.is_numeric_dtype(df[m])]

        pairs = []
        if target_x and target_y and target_x in df.columns and target_y in df.columns:
            pairs.append((target_x, target_y))

        for i in range(len(num_cols)):
            for j in range(i + 1, len(num_cols)):
                p = (num_cols[i], num_cols[j])
                if p not in pairs and (p[1], p[0]) not in pairs:
                    if not is_collinear_or_redundant_pair(p[0], p[1]):
                        pairs.append(p)

        for col_x, col_y in pairs:
            sub = df[[col_x, col_y]].dropna()
            n = len(sub)
            if n >= 4:
                r, p_val = stats.pearsonr(sub[col_x], sub[col_y])
                df_deg = n - 2
                t_val = r * math.sqrt(df_deg / max(1.0 - r**2, 1e-6)) if abs(r) < 1.0 else 0.0
                bf10, bf01, interp = compute_bayes_factor_no_correlation(float(r), n)
                interp_desc = self._interpret_correlation(float(r))
                results.append(
                    NoCorrelationResult(
                        metric_x=col_x,
                        metric_y=col_y,
                        pearson_r=round(float(r), 3),
                        t_val=round(float(t_val), 2),
                        df=df_deg,
                        p_val=round(float(p_val), 4),
                        bf10=bf10,
                        bf01=bf01,
                        interpretation=interp_desc,
                        bf_interpretation=interp,
                    )
                )

        results.sort(key=lambda x: -x.bf01)
        return results

    def _compute_trend(
        self, sub_df: pd.DataFrame, time_col: str, metric: str, group_name: Optional[str] = None
    ) -> Optional[TrendResult]:
        clean = sub_df[[time_col, metric]].dropna()
        if len(clean) < 2:
            return None

        try:
            x_vals = pd.to_numeric(clean[time_col]).values
        except Exception:
            x_vals = np.arange(len(clean))

        y_vals = clean[metric].values
        start_time, end_time = clean[time_col].iloc[0], clean[time_col].iloc[-1]
        start_val, end_val = float(y_vals[0]), float(y_vals[-1])
        diff = round(end_val - start_val, 2)
        pct_change = round(((end_val - start_val) / start_val * 100), 2) if start_val != 0 else 0.0

        slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
        r_squared = round(float(r_value**2), 3)
        bf10, bf_interp = compute_bayes_factor_correlation(float(r_value), len(x_vals))

        cagr = None
        years_span = float(x_vals[-1] - x_vals[0])
        if years_span >= 1 and start_val > 0 and end_val > 0:
            cagr_val = ((end_val / start_val) ** (1.0 / years_span) - 1.0) * 100
            cagr = round(float(cagr_val), 2)

        return TrendResult(
            metric=metric,
            group_name=group_name,
            start_time=start_time,
            start_val=round(start_val, 2),
            end_time=end_time,
            end_val=round(end_val, 2),
            diff=diff,
            pct_change=pct_change,
            cagr=cagr,
            slope=round(float(slope), 3),
            r_squared=r_squared,
            bf10=bf10,
            bf_interpretation=bf_interp,
        )

    def _interpret_correlation(self, r: float) -> str:
        abs_r = abs(r)
        direction = "正の相関" if r > 0 else "負の相関"
        if abs_r >= 0.9:
            strength = "極めて強い"
        elif abs_r >= 0.7:
            strength = "強い"
        elif abs_r >= 0.4:
            strength = "中程度の"
        elif abs_r >= 0.2:
            strength = "弱い"
        else:
            strength = "相関ほぼなし"
        return f"{strength}{direction} (r = {round(r, 2)})"

    def _generate_key_insights(
        self,
        dataset: EducationDataset,
        desc_stats: Dict[str, MetricSummary],
        trends: List[TrendResult],
        correlations: List[CorrelationResult],
        rankings: Dict[str, List[Tuple[str, float]]],
        two_way_anova: Optional[TwoWayAnovaResult] = None,
        multiple_regression: Optional[MultipleRegressionResult] = None,
        no_correlations: Optional[List[NoCorrelationResult]] = None,
        primary_method: str = "correlation",
    ) -> List[str]:
        insights = []

        # 1. Advanced Method Key Insight (prioritized based on primary_method)
        if primary_method == "two_way_anova" and two_way_anova:
            a = two_way_anova.main_effect_a
            b = two_way_anova.main_effect_b
            ab = two_way_anova.interaction
            p_a_str = format_apa_p(a.p_val)
            p_b_str = format_apa_p(b.p_val)
            p_ab_str = format_apa_p(ab.p_val)
            eta_a_str = format_apa_stat(a.eta_sq_p, bounded=True)
            eta_b_str = format_apa_stat(b.eta_sq_p, bounded=True)
            eta_ab_str = format_apa_stat(ab.eta_sq_p, bounded=True)
            bf_a_disp = format_bayes_factor(a.bf10)
            bf_b_disp = format_bayes_factor(b.bf10)
            bf_ab_disp = format_bayes_factor(ab.bf10)

            int_tag = "⚡ 交互作用の顕在化" if ab.p_val < 0.05 else "🔍 独立した主効果"
            insights.append(
                f"🔬 【二要因分散分析 (Two-way ANOVA)】: 従属変数「{two_way_anova.dv}」に対し、"
                f"{a.name}の主効果（F({a.df}, {two_way_anova.error_df}) = {a.f_val}, p {p_a_str}, η_p² = {eta_a_str}, BF₁₀ = {bf_a_disp} [{a.bf_interpretation}]）および"
                f"{b.name}の主効果（F({b.df}, {two_way_anova.error_df}) = {b.f_val}, p {p_b_str}, η_p² = {eta_b_str}, BF₁₀ = {bf_b_disp} [{b.bf_interpretation}]）を検証しました。"
            )
            insights.append(
                f"{int_tag}: {ab.name}の交互作用検定は F({ab.df}, {two_way_anova.error_df}) = {ab.f_val}, p {p_ab_str}, η_p² = {eta_ab_str} "
                f"（BF₁₀ = {bf_ab_disp} [{ab.bf_interpretation}]）であり、"
                f"{'要因間の相乗・変容効果が統計的・ベイズ統計学的に支持されました。' if ab.p_val < 0.05 else '各要因が独立かつ相加的に寄与していることが確認されました。'}"
            )

        elif primary_method == "multiple_regression" and multiple_regression:
            mr = multiple_regression
            r2_str = format_apa_stat(mr.r_squared, bounded=True)
            adj_r2_str = format_apa_stat(mr.adj_r_squared, bounded=True)
            p_model_str = format_apa_p(mr.p_val)
            bf_model_disp = format_bayes_factor(mr.bf10)

            coeff_summaries = []
            for c in mr.coefficients:
                beta_str = format_apa_stat(c.beta, bounded=True)
                p_c_str = format_apa_p(c.p_val)
                bf_c_disp = format_bayes_factor(c.bf10)
                coeff_summaries.append(
                    f"「{c.variable}」（β = {beta_str}, t = {c.t_val}, p {p_c_str}, VIF = {c.vif}, BF₁₀ = {bf_c_disp}）"
                )
            coeff_text = "、".join(coeff_summaries)

            insights.append(
                f"📊 【重回帰分析 (Multiple Linear Regression)】: 「{mr.y_metric}」を目的変数とする重回帰モデル全体は、"
                f"決定係数 R² = {r2_str}（自由度調整済 R² = {adj_r2_str}, F({mr.df_model}, {mr.df_resid}) = {mr.f_val}, p {p_model_str}, "
                f"モデル全体 BF₁₀ = {bf_model_disp} [{mr.bf_interpretation}]）を示しました。"
            )
            insights.append(
                f"💡 予測要因の相対的寄与度: 各説明変数の標準化偏回帰係数および多重共線性診断は、{coeff_text} となっています。"
            )

        elif primary_method == "no_correlation" and no_correlations:
            nc = no_correlations[0]
            r_str = format_apa_stat(nc.pearson_r, bounded=True)
            p_str = format_apa_p(nc.p_val)
            bf10_disp = format_bayes_factor(nc.bf10)
            bf01_disp = format_bayes_factor(nc.bf01)
            insights.append(
                f"⚡ 意外な非連動・真の独立性検証（無相関分析）: 「{nc.metric_x}」と「{nc.metric_y}」の間には統計的に有意な線形相関が認められず"
                f"（r = {r_str}, t({nc.df}) = {nc.t_val}, p {p_str}）、対立仮説支持の BF₁₀ = {bf10_disp} に対し、"
                f"帰無仮説（真の無相関・独立性）を支持するベイズファクター BF₀₁ = {bf01_disp}（{nc.bf_interpretation}）が算出されました。"
            )

        # 2. Trend insights with unexpectedness detection
        for tr in trends[:2]:
            prefix = f"【{tr.group_name}】" if tr.group_name else ""
            growth_desc = "増加" if tr.diff > 0 else "減少"
            cagr_str = f"（年平均成長率 CAGR: {tr.cagr:+.1f}%）" if tr.cagr is not None else ""
            m_unit = resolve_metric_unit(tr.metric, dataset.unit)

            tag = "📈 推移トレンド"
            if abs(tr.pct_change) > 30 or (tr.cagr is not None and abs(tr.cagr) > 10):
                tag = "⚡ 急伸長トレンド"
            elif abs(tr.diff) < 1.0 or abs(tr.pct_change) < 2.0:
                tag = "⚠️ 伸び悩み・停滞"

            bf_info = f", ベイズファクター BF₁₀ = {format_bayes_factor(tr.bf10)} [{tr.bf_interpretation}]" if tr.bf10 is not None else ""
            r2_apa = format_apa_stat(tr.r_squared, bounded=True)
            insights.append(
                f"{tag}: {prefix}「{tr.metric}」は{tr.start_time}年の {tr.start_val}{m_unit} から "
                f"{tr.end_time}年には {tr.end_val}{m_unit} へと "
                f"{tr.diff:+.1f}{m_unit}（{tr.pct_change:+.1f}%）{growth_desc}しました{cagr_str}。"
                f"（線形トレンド決定係数 R² = {r2_apa}{bf_info}）"
            )

        # Divergence between multiple trends
        if len(trends) >= 2:
            tr1, tr2 = trends[0], trends[1]
            if (tr1.diff > 0 and tr2.diff < 0) or (tr1.diff < 0 and tr2.diff > 0):
                insights.append(
                    f"⚡ 意外な乖離（逆相関推移）: 「{tr1.metric}」が {tr1.diff:+.1f} と上昇傾向を示す一方、"
                    f"「{tr2.metric}」は {tr2.diff:+.1f} と減少しており、連動せず対照的な動きを見せています。"
                )

        # 3. Ranking & Disparity insights
        for metric, r_list in rankings.items():
            if len(r_list) >= 2:
                top_name, top_val = r_list[0]
                bottom_name, bottom_val = r_list[-1]
                gap = round(top_val - bottom_val, 1)
                m_unit = resolve_metric_unit(metric, dataset.unit)
                ratio = round(top_val / bottom_val, 1) if bottom_val > 0 else None
                ratio_str = f"（{ratio}倍の差）" if ratio and ratio >= 1.3 else ""
                insights.append(
                    f"🔍 格差の顕在化: 最新データにおける「{metric}」の首位は{top_name}（{top_val}{m_unit}）、"
                    f"最下位は{bottom_name}（{bottom_val}{m_unit}）で、格差は {gap}{m_unit}{ratio_str} に達しています。"
                )

        # 4. Correlation insights with unexpected non-correlation detection
        for cr in correlations[:2]:
            corr_tag = "🔗 相関分析"
            if abs(cr.pearson_r) < 0.3:
                corr_tag = "⚡ 意外な非連動（独立性）"
            elif cr.pearson_r < -0.4:
                corr_tag = "⚡ 逆転の相関（トレードオフ）"
            bf_info = f", ベイズファクター BF₁₀ = {format_bayes_factor(cr.bf10)} [{cr.bf_interpretation}]" if cr.bf10 is not None else ""
            r_apa = format_apa_stat(cr.pearson_r, bounded=True)
            p_apa = format_apa_p(cr.p_value)
            insights.append(
                f"{corr_tag}: 「{cr.metric_x}」と「{cr.metric_y}」の間には、{cr.interpretation}が認められました"
                f"（相関係数 r = {r_apa}, p {p_apa}{bf_info}）。"
            )

        return insights
