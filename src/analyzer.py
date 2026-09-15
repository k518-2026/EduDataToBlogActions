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
from src.utils import resolve_metric_unit

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


@dataclass
class CorrelationResult:
    metric_x: str
    metric_y: str
    pearson_r: float
    p_value: float
    interpretation: str


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


class EduDataAnalyzer:
    """Statistical analyzer for education datasets."""

    def analyze(self, dataset: EducationDataset) -> AnalysisResult:
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
                    sub = df[[col_x, col_y]].dropna()
                    if len(sub) >= 4:
                        r, p_val = stats.pearsonr(sub[col_x], sub[col_y])
                        interp = self._interpret_correlation(r)
                        correlations.append(
                            CorrelationResult(
                                metric_x=col_x,
                                metric_y=col_y,
                                pearson_r=round(float(r), 3),
                                p_value=round(float(p_val), 4),
                                interpretation=interp,
                            )
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
        )

    def _interpret_correlation(self, r: float) -> str:
        abs_r = abs(r)
        direction = "正の相関" if r > 0 else "負の相関"
        if abs_r >= 0.7:
            strength = "極めて強い"
        elif abs_r >= 0.5:
            strength = "強い"
        elif abs_r >= 0.3:
            strength = "中程度の"
        else:
            strength = "弱い（相関ほぼなし）"
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

        # Trend insights
        for tr in trends[:3]:
            prefix = f"【{tr.group_name}】" if tr.group_name else ""
            growth_desc = "増加" if tr.diff > 0 else "減少"
            cagr_str = f"（年平均成長率 CAGR: {tr.cagr:+.1f}%）" if tr.cagr is not None else ""
            m_unit = resolve_metric_unit(tr.metric, dataset.unit)
            insights.append(
                f"{prefix}{tr.metric}は{tr.start_time}年の {tr.start_val}{m_unit} から "
                f"{tr.end_time}年には {tr.end_val}{m_unit} へと "
                f"{tr.diff:+.1f}{m_unit}（{tr.pct_change:+.1f}%）{growth_desc}しました{cagr_str}。"
                f"（線形トレンド決定係数 R² = {tr.r_squared}）"
            )

        # Ranking insights
        for metric, r_list in rankings.items():
            if len(r_list) >= 2:
                top_name, top_val = r_list[0]
                bottom_name, bottom_val = r_list[-1]
                gap = round(top_val - bottom_val, 1)
                m_unit = resolve_metric_unit(metric, dataset.unit)
                insights.append(
                    f"最新データにおける「{metric}」のトップは{top_name}（{top_val}{m_unit}）、"
                    f"最下位は{bottom_name}（{bottom_val}{m_unit}）で、格差は {gap}{m_unit} に達しています。"
                )

        # Correlation insights
        for cr in correlations[:2]:
            insights.append(
                f"「{cr.metric_x}」と「{cr.metric_y}」の間には、{cr.interpretation}が認められました"
                f"（相関係数 r = {cr.pearson_r}, p = {cr.p_value}）。"
            )

        return insights
