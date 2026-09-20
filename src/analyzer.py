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

        # 5. Extract automated key insights
        insights = self._generate_key_insights(dataset, desc_stats, trends, correlations, rankings)

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
        )

    def _compute_trend(
        self, sub_df: pd.DataFrame, time_col: str, metric: str, group_name: Optional[str] = None
    ) -> Optional[TrendResult]:
        clean = sub_df[[time_col, metric]].dropna()
        if len(clean) < 2:
            return None

        # Convert time to numeric if possible
        try:
            x_vals = pd.to_numeric(clean[time_col]).values
        except Exception:
            x_vals = np.arange(len(clean))

        y_vals = clean[metric].values
        start_time, end_time = clean[time_col].iloc[0], clean[time_col].iloc[-1]
        start_val, end_val = float(y_vals[0]), float(y_vals[-1])
        diff = round(end_val - start_val, 2)
        pct_change = round(((end_val - start_val) / start_val * 100), 2) if start_val != 0 else 0.0

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
        r_squared = round(float(r_value**2), 3)
        bf10, bf_interp = compute_bayes_factor_correlation(float(r_value), len(x_vals))

        # CAGR calculation
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
    ) -> List[str]:
        insights = []

        # 1. Trend insights with unexpectedness detection
        for tr in trends[:3]:
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
            insights.append(
                f"{tag}: {prefix}「{tr.metric}」は{tr.start_time}年の {tr.start_val}{m_unit} から "
                f"{tr.end_time}年には {tr.end_val}{m_unit} へと "
                f"{tr.diff:+.1f}{m_unit}（{tr.pct_change:+.1f}%）{growth_desc}しました{cagr_str}。"
                f"（線形トレンド決定係数 R² = {tr.r_squared}{bf_info}）"
            )

        # Divergence between multiple trends
        if len(trends) >= 2:
            tr1, tr2 = trends[0], trends[1]
            if (tr1.diff > 0 and tr2.diff < 0) or (tr1.diff < 0 and tr2.diff > 0):
                insights.append(
                    f"⚡ 意外な乖離（逆相関推移）: 「{tr1.metric}」が {tr1.diff:+.1f} と上昇傾向を示す一方、"
                    f"「{tr2.metric}」は {tr2.diff:+.1f} と減少しており、連動せず対照的な動きを見せています。"
                )

        # 2. Ranking & Disparity insights
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

        # 3. Correlation insights with unexpected non-correlation detection
        for cr in correlations[:2]:
            corr_tag = "🔗 相関分析"
            if abs(cr.pearson_r) < 0.3:
                corr_tag = "⚡ 意外な非連動（独立性）"
            elif cr.pearson_r < -0.4:
                corr_tag = "⚡ 逆転の相関（トレードオフ）"
            bf_info = f", ベイズファクター BF₁₀ = {format_bayes_factor(cr.bf10)} [{cr.bf_interpretation}]" if cr.bf10 is not None else ""
            insights.append(
                f"{corr_tag}: 「{cr.metric_x}」と「{cr.metric_y}」の間には、{cr.interpretation}が認められました"
                f"（相関係数 r = {cr.pearson_r}, p = {cr.p_value}{bf_info}）。"
            )

        return insights
