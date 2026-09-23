from __future__ import annotations

"""
Visualization Engine for Educational Open Data.
Generates publication-quality charts using Matplotlib and Seaborn with robust Japanese font support.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import seaborn as sns

from src.analyzer import (
    AnalysisResult,
    format_apa_p,
    format_apa_stat,
    is_collinear_or_redundant_pair,
)
from src.config import TEMP_DIR
from src.fetchers.base import EducationDataset
from src.utils import format_bayes_factor, resolve_metric_unit

logger = logging.getLogger(__name__)


def setup_japanese_font():
    """Configures font family list with Japanese font fallbacks for Windows, Linux, and macOS."""
    font_fallbacks = [
        "Noto Sans CJK JP",
        "Noto Sans JP",
        "Yu Gothic",
        "Meiryo",
        "TakaoGothic",
        "IPAGothic",
        "IPAexGothic",
        "Hiragino Sans",
        "MS Gothic",
        "DejaVu Sans",
        "sans-serif",
    ]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = font_fallbacks
    plt.rcParams["axes.unicode_minus"] = False


class EduDataVisualizer:
    """Generates charts for educational datasets."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or TEMP_DIR
        self.output_dir.mkdir(exist_ok=True)
        setup_japanese_font()

        # Set clean aesthetic style
        sns.set_theme(style="whitegrid")
        setup_japanese_font()  # Re-apply font after seaborn theme reset
        plt.rcParams["figure.dpi"] = 180
        plt.rcParams["axes.titlesize"] = 14
        plt.rcParams["axes.labelsize"] = 11
        plt.rcParams["xtick.labelsize"] = 10
        plt.rcParams["ytick.labelsize"] = 10

    def generate_chart(
        self,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
    ) -> Path:
        """
        Generates the primary visualization chart for a dataset.
        Applies seaborn modern styling, confidence intervals, and high-resolution DPI.
        """
        chart_type = dataset.recommended_chart
        output_path = self.output_dir / f"chart_{dataset.id}.png"

        fig, ax = plt.subplots(figsize=(10, 5.8))

        try:
            if chart_type == "trend_line" and dataset.time_col:
                self._plot_trend_lines(fig, ax, dataset, analysis)
            elif chart_type == "ranking_bar" and dataset.group_col:
                self._plot_ranking_bar(fig, ax, dataset, analysis)
            elif chart_type == "correlation_scatter" and len(dataset.metrics) >= 2:
                self._plot_correlation_scatter(fig, ax, dataset, analysis, selected_angle=selected_angle)
            else:
                # Default fallback
                if dataset.time_col:
                    self._plot_trend_lines(fig, ax, dataset, analysis)
                else:
                    self._plot_ranking_bar(fig, ax, dataset, analysis)

            plt.tight_layout()
            fig.savefig(output_path, dpi=180, bbox_inches="tight")
            logger.info(f"Saved chart image to {output_path}")
            return output_path
        finally:
            plt.close(fig)

    def generate_secondary_chart(
        self,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
    ) -> Optional[Path]:
        """
        Generates a complementary secondary chart (e.g. correlation scatter or group comparison)
        for academic publications requiring multiple visual figures.
        Strictly aligns with the selected angle's Research Questions (RQ1/RQ2).
        """
        output_path = self.output_dir / f"chart_secondary_{dataset.id}.png"

        target_chart_type = getattr(selected_angle, "secondary_chart_type", None)
        if not target_chart_type:
            if getattr(analysis, "primary_method", "") == "two_way_anova" and analysis.two_way_anova:
                target_chart_type = "anova_interaction"
            elif getattr(analysis, "primary_method", "") == "multiple_regression" and analysis.multiple_regression:
                target_chart_type = "multiple_regression"
            elif getattr(analysis, "primary_method", "") == "no_correlation" and analysis.no_correlations:
                target_chart_type = "no_correlation_scatter"
            else:
                chart_type = dataset.recommended_chart
                if chart_type == "trend_line":
                    target_chart_type = "correlation_scatter" if len(dataset.metrics) >= 2 else "ranking_bar"
                elif chart_type == "ranking_bar":
                    target_chart_type = "correlation_scatter" if len(dataset.metrics) >= 2 else "trend_line"
                elif chart_type == "correlation_scatter":
                    target_chart_type = "trend_line" if dataset.time_col else "ranking_bar"
                else:
                    target_chart_type = "correlation_scatter"

        fig, ax = plt.subplots(figsize=(10, 5.8))
        try:
            rendered = False
            if target_chart_type == "anova_interaction" and analysis.two_way_anova:
                self._plot_interaction_anova(fig, ax, dataset, analysis, selected_angle=selected_angle)
                rendered = True
            elif target_chart_type == "multiple_regression" and analysis.multiple_regression:
                self._plot_multiple_regression(fig, ax, dataset, analysis, selected_angle=selected_angle)
                rendered = True
            elif target_chart_type == "no_correlation_scatter" and analysis.no_correlations:
                self._plot_no_correlation_scatter(fig, ax, dataset, analysis, selected_angle=selected_angle)
                rendered = True
            elif target_chart_type in ("ranking_bar", "group_comparison_bar") and dataset.group_col:
                metric_target = getattr(selected_angle, "group_comparison_metric", None)
                self._plot_ranking_bar(
                    fig, ax, dataset, analysis, metric_override=metric_target, selected_angle=selected_angle
                )
                rendered = True
            elif target_chart_type == "correlation_scatter":
                self._plot_correlation_scatter(fig, ax, dataset, analysis, selected_angle=selected_angle)
                rendered = True
            elif target_chart_type == "trend_line" and dataset.time_col:
                self._plot_trend_lines(fig, ax, dataset, analysis)
                rendered = True

            if not rendered:
                if analysis.two_way_anova:
                    self._plot_interaction_anova(fig, ax, dataset, analysis, selected_angle=selected_angle)
                    rendered = True
                elif analysis.multiple_regression:
                    self._plot_multiple_regression(fig, ax, dataset, analysis, selected_angle=selected_angle)
                    rendered = True
                elif analysis.no_correlations:
                    self._plot_no_correlation_scatter(fig, ax, dataset, analysis, selected_angle=selected_angle)
                    rendered = True
                elif len(dataset.metrics) >= 2:
                    self._plot_correlation_scatter(fig, ax, dataset, analysis, selected_angle=selected_angle)
                    rendered = True
                elif dataset.group_col:
                    self._plot_ranking_bar(fig, ax, dataset, analysis)
                    rendered = True

            if rendered:
                plt.tight_layout()
                fig.savefig(output_path, dpi=180, bbox_inches="tight")
                logger.info(f"Saved secondary chart image to {output_path}")
                return output_path
            return None
        except Exception as e:
            logger.warning(f"Could not generate secondary chart: {e}")
            return None
        finally:
            plt.close(fig)

    @staticmethod
    def _compute_trend_ci_errors(
        sub: pd.DataFrame, time_col: str, metric: str, fallback_std: float
    ) -> np.ndarray:
        """
        Computes 95% Confidence Interval error margins for a time series.
        Uses Student's t distribution with survey sampling standard error or linear regression SE.
        """
        n = len(sub)
        y_vals = pd.to_numeric(sub[metric], errors="coerce").values

        if n <= 1:
            return np.full(n, max(fallback_std * 0.8, 0.5))

        grp_std = float(np.nanstd(y_vals, ddof=1)) if n > 1 else fallback_std
        if grp_std == 0 or np.isnan(grp_std):
            grp_std = fallback_std if fallback_std > 0 else 1.5

        t_crit = float(stats.t.ppf(0.975, df=max(n - 1, 1)))
        se_base = grp_std / np.sqrt(max(n, 1))
        base_ci = max(float(t_crit * se_base), 0.6)

        # Regression-based confidence interval if numeric time_col and n >= 3
        try:
            x_num = pd.to_numeric(sub[time_col], errors="coerce").values
            if not np.isnan(x_num).any() and n >= 3:
                res = stats.linregress(x_num, y_vals)
                y_pred = res.slope * x_num + res.intercept
                residuals = y_vals - y_pred
                s_err = np.sqrt(np.sum(residuals**2) / max(n - 2, 1))
                x_bar = np.mean(x_num)
                ss_x = np.sum((x_num - x_bar) ** 2)
                if ss_x > 0 and s_err > 0:
                    ci_err = t_crit * s_err * np.sqrt(1.0 / n + (x_num - x_bar) ** 2 / ss_x)
                    return np.maximum(ci_err, base_ci * 0.7)
        except Exception:
            pass

        return np.full(n, base_ci)

    def _plot_trend_lines(
        self, fig: plt.Figure, ax: plt.Axes, dataset: EducationDataset, analysis: AnalysisResult
    ):
        df = dataset.df.copy()
        time_col = dataset.time_col
        group_col = dataset.group_col
        primary_metric = dataset.metrics[0]

        palette = sns.color_palette("tab10")
        overall_std = (
            analysis.descriptive_stats.get(primary_metric).std
            if primary_metric in analysis.descriptive_stats
            else 2.0
        )

        if group_col and group_col in df.columns:
            groups = df[group_col].unique()
            for idx, grp in enumerate(groups):
                sub = df[df[group_col] == grp].sort_values(by=time_col)
                if len(sub) == 0:
                    continue
                color = palette[idx % len(palette)]
                x_vals = sub[time_col].values
                y_vals = pd.to_numeric(sub[primary_metric], errors="coerce").values

                ci_err = self._compute_trend_ci_errors(sub, time_col, primary_metric, overall_std)

                # Plot error bar with capped ticks (95% CI)
                ax.errorbar(
                    x_vals,
                    y_vals,
                    yerr=ci_err,
                    fmt="o-",
                    linewidth=2.5,
                    markersize=6,
                    capsize=4.0,
                    capthick=1.4,
                    elinewidth=1.4,
                    color=color,
                    label=str(grp),
                    alpha=0.95,
                    zorder=3,
                )
                # Shaded 95% confidence interval band
                ax.fill_between(
                    x_vals,
                    y_vals - ci_err,
                    y_vals + ci_err,
                    color=color,
                    alpha=0.18,
                    zorder=2,
                )

                primary_unit = resolve_metric_unit(primary_metric, dataset.unit)
                last_x = x_vals[-1]
                last_y = y_vals[-1]
                ax.annotate(
                    f"{last_y:.1f}{primary_unit}",
                    (last_x, last_y),
                    textcoords="offset points",
                    xytext=(8, -3),
                    fontsize=9,
                    fontweight="bold",
                    color=color,
                    zorder=4,
                )
        else:
            primary_unit = resolve_metric_unit(primary_metric, dataset.unit)
            for idx, m in enumerate(dataset.metrics):
                if m in df.columns:
                    sub = df.sort_values(by=time_col)
                    if len(sub) == 0:
                        continue
                    color = palette[idx % len(palette)]
                    x_vals = sub[time_col].values
                    y_vals = pd.to_numeric(sub[m], errors="coerce").values
                    m_std = (
                        analysis.descriptive_stats.get(m).std
                        if m in analysis.descriptive_stats
                        else overall_std
                    )
                    ci_err = self._compute_trend_ci_errors(sub, time_col, m, m_std)

                    ax.errorbar(
                        x_vals,
                        y_vals,
                        yerr=ci_err,
                        fmt="s-",
                        linewidth=2.5,
                        markersize=6,
                        capsize=4.0,
                        capthick=1.4,
                        elinewidth=1.4,
                        color=color,
                        label=m,
                        alpha=0.95,
                        zorder=3,
                    )
                    ax.fill_between(
                        x_vals,
                        y_vals - ci_err,
                        y_vals + ci_err,
                        color=color,
                        alpha=0.18,
                        zorder=2,
                    )

                    m_unit = resolve_metric_unit(m, dataset.unit)
                    last_x = x_vals[-1]
                    last_y = y_vals[-1]
                    ax.annotate(
                        f"{last_y:.1f}{m_unit}",
                        (last_x, last_y),
                        textcoords="offset points",
                        xytext=(8, -3),
                        fontsize=9,
                        fontweight="bold",
                        color=color,
                        zorder=4,
                    )

        ax.set_title(f"{dataset.title}\n【経年推移と95%信頼区間】", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel(f"{time_col} (年/年度)", fontsize=11, labelpad=8)
        ax.set_ylabel(f"値 ({primary_unit})", fontsize=11, labelpad=8)
        ax.legend(title="【帯・誤差棒: 95% CI】", frameon=True, facecolor="white", edgecolor="#cbd5e1", fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.5)

        ax.text(
            0.99,
            0.03,
            "※エラーバーおよび網掛け帯は 95% 信頼区間 (95% CI) を示す",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8.5,
            color="#334155",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cbd5e1"),
            zorder=5,
        )

    def _plot_ranking_bar(
        self,
        fig: plt.Figure,
        ax: plt.Axes,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        metric_override: Optional[str] = None,
        selected_angle: Optional[Any] = None,
    ):
        df_full = dataset.df.copy()
        group_col = dataset.group_col
        metric = (
            metric_override
            if metric_override and metric_override in df_full.columns
            else dataset.metrics[0]
        )

        df = df_full.copy()
        if dataset.time_col and dataset.time_col in df.columns:
            latest_time = df[dataset.time_col].max()
            df = df[df[dataset.time_col] == latest_time]

        sorted_df = df.groupby(group_col)[metric].mean().sort_values(ascending=True).reset_index()

        overall_std = (
            analysis.descriptive_stats.get(metric).std
            if metric in analysis.descriptive_stats
            else 2.0
        )

        ci_values = []
        for grp in sorted_df[group_col]:
            grp_latest = pd.to_numeric(df[df[group_col] == grp][metric], errors="coerce").dropna()
            grp_full = pd.to_numeric(df_full[df_full[group_col] == grp][metric], errors="coerce").dropna()

            if len(grp_latest) >= 2:
                std_val = float(grp_latest.std(ddof=1))
                se = (std_val if std_val > 0 else overall_std) / np.sqrt(len(grp_latest))
                t_crit = float(stats.t.ppf(0.975, df=len(grp_latest) - 1))
                ci = max(float(t_crit * se), 0.5)
            elif len(grp_full) >= 2:
                std_val = float(grp_full.std(ddof=1))
                se = (std_val if std_val > 0 else overall_std) / np.sqrt(len(grp_full))
                t_crit = float(stats.t.ppf(0.975, df=len(grp_full) - 1))
                ci = max(float(t_crit * se), 0.5)
            else:
                n_eff = max(len(sorted_df), 3)
                se = overall_std / np.sqrt(n_eff)
                ci = max(float(1.96 * se), 0.5)
            ci_values.append(ci)

        sorted_df["ci_95"] = ci_values

        colors = []
        for name in sorted_df[group_col]:
            name_str = str(name)
            if "日本" in name_str or "Japan" in name_str:
                colors.append("#e63946")  # Red
            elif "平均" in name_str or "OECD" in name_str:
                colors.append("#f4a261")  # Orange
            else:
                colors.append("#457b9d")  # Slate blue

        bars = ax.barh(
            sorted_df[group_col],
            sorted_df[metric],
            xerr=sorted_df["ci_95"],
            capsize=4.5,
            error_kw={
                "elinewidth": 1.4,
                "ecolor": "#1e293b",
                "capthick": 1.4,
                "alpha": 0.85,
            },
            color=colors,
            height=0.65,
            zorder=3,
        )

        metric_unit = resolve_metric_unit(metric, dataset.unit)
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ci = sorted_df["ci_95"].iloc[i]
            ax.annotate(
                f"{width:.1f}{metric_unit} (±{ci:.1f})",
                xy=(width + ci, bar.get_y() + bar.get_height() / 2),
                xytext=(6, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=8.5,
                fontweight="bold",
                color="#1e293b",
                zorder=4,
            )

        rq_label = "【グループ比較と95%信頼区間】"
        if getattr(selected_angle, "group_comparison_metric", None) == metric:
            rq_label = f"【RQ検証：{metric}のグループ・学校種間格差】"

        ax.set_title(f"{dataset.title}\n{rq_label}", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel(f"{metric} ({metric_unit})  [誤差棒: 95% 信頼区間 (95% CI)]", fontsize=11, labelpad=8)
        ax.set_ylabel("", fontsize=11)
        ax.grid(True, axis="x", linestyle="--", alpha=0.5)

        max_reach = (sorted_df[metric] + sorted_df["ci_95"]).max()
        ax.set_xlim(0, max_reach * 1.22)

        ax.text(
            0.99,
            0.03,
            "※エラーバーは 95% 信頼区間 (95% CI) を示す",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8.5,
            color="#334155",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cbd5e1"),
            zorder=5,
        )

    def _plot_correlation_scatter(
        self,
        fig: plt.Figure,
        ax: plt.Axes,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
    ):
        df = dataset.df.copy()
        target_x = getattr(selected_angle, "scatter_x_metric", None)
        target_y = getattr(selected_angle, "scatter_y_metric", None)

        col_x, col_y = None, None
        if target_x and target_y and target_x in df.columns and target_y in df.columns:
            if not is_collinear_or_redundant_pair(target_x, target_y):
                col_x, col_y = target_x, target_y

        # If not set or collinear, pick first non-collinear from analysis.correlations
        if not col_x or not col_y:
            for cr in analysis.correlations:
                if cr.metric_x in df.columns and cr.metric_y in df.columns:
                    if not is_collinear_or_redundant_pair(cr.metric_x, cr.metric_y):
                        col_x, col_y = cr.metric_x, cr.metric_y
                        break

        # Fallback if still none found
        if not col_x or not col_y:
            num_cols = [
                m
                for m in dataset.metrics
                if m in df.columns and pd.api.types.is_numeric_dtype(df[m])
            ]
            found = False
            for i in range(len(num_cols)):
                for j in range(i + 1, len(num_cols)):
                    if not is_collinear_or_redundant_pair(num_cols[i], num_cols[j]):
                        col_x, col_y = num_cols[i], num_cols[j]
                        found = True
                        break
                if found:
                    break
            if not found and len(num_cols) >= 2:
                col_x, col_y = num_cols[1], num_cols[0]
            elif not found and len(num_cols) == 1:
                col_x = col_y = num_cols[0]

        group_col = dataset.group_col

        sns.regplot(
            x=col_x,
            y=col_y,
            data=df,
            ax=ax,
            ci=95,  # 95% confidence interval for regression estimate
            color="#2a9d8f",
            scatter_kws={"s": 70, "alpha": 0.8, "zorder": 3},
            line_kws={"color": "#e76f51", "linewidth": 2, "zorder": 4},
        )

        if group_col and group_col in df.columns:
            for _, row in df.iterrows():
                name = str(row[group_col])
                ax.annotate(
                    name,
                    (row[col_x], row[col_y]),
                    textcoords="offset points",
                    xytext=(5, 5),
                    fontsize=8,
                    color="#264653",
                    zorder=4,
                )

        r_info = ""
        for cr in analysis.correlations:
            if (cr.metric_x == col_x and cr.metric_y == col_y) or (
                cr.metric_x == col_y and cr.metric_y == col_x
            ):
                bf_str = (
                    f", BF10 = {format_bayes_factor(cr.bf10)}"
                    if getattr(cr, "bf10", None) is not None
                    else ""
                )
                r_info = f" (相関係数 r = {cr.pearson_r}, p = {cr.p_value}{bf_str})"
                break

        x_unit = resolve_metric_unit(col_x, dataset.unit)
        y_unit = resolve_metric_unit(col_y, dataset.unit)
        rq_label = "【相関分析】"
        if (
            target_x
            and target_y
            and (col_x in (target_x, target_y))
            and (col_y in (target_x, target_y))
        ):
            rq_label = f"【RQ2検証：{col_x}と{col_y}の連動構造】"

        ax.set_title(
            f"{dataset.title}\n{rq_label}{col_x} vs {col_y}{r_info}（95%CI併記）",
            fontsize=12,
            fontweight="bold",
            pad=12,
        )
        ax.set_xlabel(f"{col_x} ({x_unit})", fontsize=11, labelpad=8)
        ax.set_ylabel(f"{col_y} ({y_unit})", fontsize=11, labelpad=8)
        ax.grid(True, linestyle="--", alpha=0.5)

        ax.text(
            0.99,
            0.03,
            "※回帰直線の帯は 95% 信頼区間 (95% CI) を示す",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8.5,
            color="#475569",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cbd5e1"),
            zorder=5,
        )

    def _plot_interaction_anova(
        self,
        fig: plt.Figure,
        ax: plt.Axes,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
    ):
        """
        Plots Factor A x Factor B Interaction Plot for Two-way ANOVA with 95% Confidence Intervals.
        """
        anova = analysis.two_way_anova
        if not anova:
            return self._plot_correlation_scatter(fig, ax, dataset, analysis, selected_angle)

        df = dataset.df.copy()
        dv = anova.dv
        fa = anova.factor_a
        fb = anova.factor_b

        # If Factor B was binned in anova
        if anova.factor_b_is_binned:
            unique_b = sorted(df[fb].unique())
            mid = len(unique_b) // 2
            first_half = set(unique_b[:mid])
            df["_fb_plot"] = df[fb].apply(lambda x: "前期" if x in first_half else "後期")
            fb_col = "_fb_plot"
        else:
            fb_col = fb

        # Clean and group
        df[dv] = pd.to_numeric(df[dv], errors="coerce")
        df[fa] = df[fa].astype(str)
        df[fb_col] = df[fb_col].astype(str)
        sub = df[[dv, fa, fb_col]].dropna()

        grouped = sub.groupby([fa, fb_col])[dv].agg(["mean", "std", "count"]).reset_index()
        t_crit = 1.96
        grouped["se"] = grouped["std"].fillna(1.0) / np.sqrt(np.maximum(grouped["count"], 1))
        grouped["ci"] = np.maximum(grouped["se"] * t_crit, 0.4)

        palette = ["#2b5c8f", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02"]
        markers = ["o", "s", "^", "D", "v", "P"]

        unique_fa = sorted(grouped[fa].unique())
        unique_fb = sorted(grouped[fb_col].unique())

        x_coords = {val: i for i, val in enumerate(unique_fb)}

        for idx, grp_a in enumerate(unique_fa):
            grp_data = grouped[grouped[fa] == grp_a].sort_values(by=fb_col)
            color = palette[idx % len(palette)]
            marker = markers[idx % len(markers)]
            xs = [x_coords[x] for x in grp_data[fb_col]]
            ys = grp_data["mean"].values
            yerr = grp_data["ci"].values

            ax.errorbar(
                xs,
                ys,
                yerr=yerr,
                label=f"{grp_a}",
                color=color,
                marker=marker,
                markersize=8,
                linewidth=2.4,
                capsize=5,
                capthick=1.5,
                alpha=0.9,
                zorder=4,
            )

        ax.set_xticks(range(len(unique_fb)))
        ax.set_xticklabels(unique_fb, fontsize=10.5, fontweight="bold")
        unit_str = f" ({dataset.unit})" if dataset.unit else ""
        ax.set_ylabel(f"{dv}{unit_str}", fontsize=11, fontweight="bold")
        ax.set_xlabel(f"{fb}（要因B）", fontsize=11, fontweight="bold")
        ax.set_title(f"二要因分散分析（Two-way ANOVA）交互作用プロット：{fa} × {fb}", fontsize=13, fontweight="bold", pad=12)
        ax.legend(title=f"【{fa}（要因A）】", frameon=True, facecolor="white", edgecolor="#cbd5e1", loc="best")
        ax.grid(True, linestyle="--", alpha=0.5)

        # Stats text box (APA 7th format)
        eff_a = anova.main_effect_a
        eff_b = anova.main_effect_b
        eff_int = anova.interaction
        p_a = format_apa_p(eff_a.p_val)
        p_b = format_apa_p(eff_b.p_val)
        p_int = format_apa_p(eff_int.p_val)
        eta_a = format_apa_stat(eff_a.eta_sq_p, bounded=True)
        eta_b = format_apa_stat(eff_b.eta_sq_p, bounded=True)
        eta_int = format_apa_stat(eff_int.eta_sq_p, bounded=True)
        bf_a = format_bayes_factor(eff_a.bf10)
        bf_b = format_bayes_factor(eff_b.bf10)
        bf_int = format_bayes_factor(eff_int.bf10)

        stats_box = (
            f"【二要因分散分析 検定結果（APA 7th & ベイズ統計）】\n"
            f"・主効果A（{fa}）: F({eff_a.df}, {anova.error_df}) = {eff_a.f_val:.2f}, p {p_a}, η_p² = {eta_a}, BF10 = {bf_a}\n"
            f"・主効果B（{fb}）: F({eff_b.df}, {anova.error_df}) = {eff_b.f_val:.2f}, p {p_b}, η_p² = {eta_b}, BF10 = {bf_b}\n"
            f"・交互作用（A×B）: F({eff_int.df}, {anova.error_df}) = {eff_int.f_val:.2f}, p {p_int}, η_p² = {eta_int}, BF10 = {bf_int}\n"
            f"※誤差棒は各水準の 95% 信頼区間 (95% CI) を示す"
        )
        ax.text(
            0.02,
            0.04,
            stats_box,
            transform=ax.transAxes,
            fontsize=8.5,
            verticalalignment="bottom",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8fafc", edgecolor="#94a3b8", alpha=0.92),
            zorder=6,
        )

    def _plot_multiple_regression(
        self,
        fig: plt.Figure,
        ax: plt.Axes,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
    ):
        """
        Plots Observed vs. Predicted Values for Multiple Linear Regression with 95% CI.
        """
        reg = analysis.multiple_regression
        if not reg:
            return self._plot_correlation_scatter(fig, ax, dataset, analysis, selected_angle)

        df = dataset.df.copy()
        y_col = reg.y_metric
        x_cols = reg.x_metrics
        cols = [y_col] + x_cols
        sub = df[cols].dropna()

        # Compute predicted values
        y_obs = pd.to_numeric(sub[y_col]).values
        try:
            import statsmodels.api as sm
            X_df = sub[x_cols].apply(pd.to_numeric)
            X_const = sm.add_constant(X_df)
            model = sm.OLS(y_obs, X_const).fit()
            y_pred = model.predict(X_const)
        except Exception:
            y_pred = y_obs

        # Plot observed vs predicted
        sns.regplot(
            x=y_pred,
            y=y_obs,
            ax=ax,
            ci=95,
            color="#1d4ed8",
            scatter_kws={"s": 65, "alpha": 0.85, "zorder": 4},
            line_kws={"color": "#dc2626", "linewidth": 2.2, "label": "回帰適合線（95% CI）", "zorder": 5},
        )

        min_val = float(min(np.min(y_pred), np.min(y_obs)))
        max_val = float(max(np.max(y_pred), np.max(y_obs)))
        padding = (max_val - min_val) * 0.05
        ax.plot(
            [min_val - padding, max_val + padding],
            [min_val - padding, max_val + padding],
            linestyle="--",
            color="#64748b",
            linewidth=1.5,
            label="完全一致基準線 (y = y_pred)",
            zorder=3,
        )

        label_col = dataset.group_col or dataset.time_col
        if label_col and label_col in df.columns and len(sub) <= 15:
            labels = df.loc[sub.index, label_col].values
            for i, txt in enumerate(labels):
                ax.annotate(
                    str(txt),
                    (y_pred[i], y_obs[i]),
                    textcoords="offset points",
                    xytext=(0, 6),
                    ha="center",
                    fontsize=8.5,
                    color="#1e293b",
                    zorder=6,
                )

        unit_str = f" ({dataset.unit})" if dataset.unit else ""
        ax.set_xlabel(f"重回帰モデル予測値 y_pred{unit_str}", fontsize=11, fontweight="bold")
        ax.set_ylabel(f"実測値 y ({y_col}){unit_str}", fontsize=11, fontweight="bold")
        ax.set_title(f"重回帰分析（Multiple Regression）実測値 vs 予測値プロット", fontsize=13, fontweight="bold", pad=12)
        ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", loc="upper left")
        ax.grid(True, linestyle="--", alpha=0.5)

        # Stats box
        r2_str = format_apa_stat(reg.r_squared, bounded=True)
        adj_r2_str = format_apa_stat(reg.adj_r_squared, bounded=True)
        p_model = format_apa_p(reg.p_val)
        bf_model = format_bayes_factor(reg.bf10)

        coeff_lines = []
        for c in reg.coefficients:
            b_str = format_apa_stat(c.beta, bounded=True)
            p_c = format_apa_p(c.p_val)
            coeff_lines.append(f"  ・{c.variable}: β = {b_str}, t = {c.t_val:.2f}, p {p_c}, VIF = {c.vif:.1f}")
        coeff_text = "\n".join(coeff_lines)

        stats_box = (
            f"【重回帰モデル評価（APA 7th & ベイズ統計）】\n"
            f"・モデル決定係数: R² = {r2_str} (adj. R² = {adj_r2_str})\n"
            f"・全体F検定: F({reg.df_model}, {reg.df_resid}) = {reg.f_val:.2f}, p {p_model}\n"
            f"・モデルベイズファクター: BF10 = {bf_model} [{reg.bf_interpretation}]\n"
            f"・各説明変数の標準化偏回帰係数:\n{coeff_text}"
        )
        ax.text(
            0.98,
            0.04,
            stats_box,
            transform=ax.transAxes,
            fontsize=8.5,
            horizontalalignment="right",
            verticalalignment="bottom",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8fafc", edgecolor="#94a3b8", alpha=0.92),
            zorder=6,
        )

    def _plot_no_correlation_scatter(
        self,
        fig: plt.Figure,
        ax: plt.Axes,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
    ):
        """
        Plots scatter plot with Null-Support Bayes Factor (BF01) evaluating lack of correlation / independence.
        """
        df = dataset.df.copy()
        no_corrs = analysis.no_correlations
        if not no_corrs:
            return self._plot_correlation_scatter(fig, ax, dataset, analysis, selected_angle)

        target_nc = no_corrs[0]
        col_x = target_nc.metric_x
        col_y = target_nc.metric_y

        sub = df[[col_x, col_y]].dropna()
        x_vals = pd.to_numeric(sub[col_x]).values
        y_vals = pd.to_numeric(sub[col_y]).values

        sns.regplot(
            x=x_vals,
            y=y_vals,
            ax=ax,
            ci=95,
            color="#0891b2",
            scatter_kws={"s": 70, "alpha": 0.85, "zorder": 4},
            line_kws={"color": "#64748b", "linestyle": "--", "linewidth": 2.0, "label": "線形トレンド（95% CI）", "zorder": 5},
        )

        label_col = dataset.group_col or dataset.time_col
        if label_col and label_col in df.columns and len(sub) <= 15:
            labels = df.loc[sub.index, label_col].values
            for i, txt in enumerate(labels):
                ax.annotate(
                    str(txt),
                    (x_vals[i], y_vals[i]),
                    textcoords="offset points",
                    xytext=(0, 6),
                    ha="center",
                    fontsize=8.5,
                    color="#334155",
                    zorder=6,
                )

        x_unit = resolve_metric_unit(col_x, dataset.unit)
        y_unit = resolve_metric_unit(col_y, dataset.unit)
        ax.set_xlabel(f"{col_x}{f' ({x_unit})' if x_unit else ''}", fontsize=11, fontweight="bold")
        ax.set_ylabel(f"{col_y}{f' ({y_unit})' if y_unit else ''}", fontsize=11, fontweight="bold")
        ax.set_title(f"無相関・独立性検証散布図（Null Hypothesis Support）：{col_x} × {col_y}", fontsize=13, fontweight="bold", pad=12)
        ax.grid(True, linestyle="--", alpha=0.5)

        r_str = format_apa_stat(target_nc.pearson_r, bounded=True)
        p_str = format_apa_p(target_nc.p_val)
        bf10_str = format_bayes_factor(target_nc.bf10)
        bf01_str = format_bayes_factor(target_nc.bf01)

        stats_box = (
            f"【無相関・独立性検定（APA 7th & ベイズ統計）】\n"
            f"・ピアソン相関係数: r = {r_str}\n"
            f"・無相関t検定: t({target_nc.df}) = {target_nc.t_val:.2f}, p {p_str}\n"
            f"・対立仮説支持: BF10 = {bf10_str}\n"
            f"・帰無仮説（真の無相関）支持: BF01 = {bf01_str}\n"
            f"・証拠判定: {target_nc.bf_interpretation}\n"
            f"※帯は 95% 信頼区間 (95% CI) を示す"
        )
        ax.text(
            0.03,
            0.04,
            stats_box,
            transform=ax.transAxes,
            fontsize=8.5,
            verticalalignment="bottom",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0fdf4" if target_nc.bf01 >= 3.0 else "#f8fafc",
                      edgecolor="#16a34a" if target_nc.bf01 >= 3.0 else "#94a3b8", alpha=0.92),
            zorder=6,
        )
        ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", loc="upper right")

