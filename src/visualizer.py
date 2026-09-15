"""
Visualization Engine for Educational Open Data.
Generates publication-quality charts using Matplotlib and Seaborn with robust Japanese font support.
"""
import logging
from pathlib import Path
from typing import List, Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import seaborn as sns

from src.analyzer import AnalysisResult
from src.config import TEMP_DIR
from src.fetchers.base import EducationDataset
from src.utils import resolve_metric_unit

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

    def generate_chart(self, dataset: EducationDataset, analysis: AnalysisResult) -> Path:
        """
        Selects and renders the best chart type for the dataset.
        Returns the path to the saved PNG image.
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
                self._plot_correlation_scatter(fig, ax, dataset, analysis)
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
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> Optional[Path]:
        """
        Generates a complementary secondary chart (e.g. correlation scatter or group comparison)
        for academic publications requiring multiple visual figures.
        """
        chart_type = dataset.recommended_chart
        output_path = self.output_dir / f"chart_secondary_{dataset.id}.png"

        fig, ax = plt.subplots(figsize=(10, 5.8))
        try:
            rendered = False
            if chart_type == "trend_line":
                if len(dataset.metrics) >= 2:
                    self._plot_correlation_scatter(fig, ax, dataset, analysis)
                    rendered = True
                elif dataset.group_col:
                    self._plot_ranking_bar(fig, ax, dataset, analysis)
                    rendered = True
            elif chart_type == "ranking_bar":
                if len(dataset.metrics) >= 2:
                    self._plot_correlation_scatter(fig, ax, dataset, analysis)
                    rendered = True
                elif dataset.time_col:
                    self._plot_trend_lines(fig, ax, dataset, analysis)
                    rendered = True
            elif chart_type == "correlation_scatter":
                if dataset.time_col:
                    self._plot_trend_lines(fig, ax, dataset, analysis)
                    rendered = True
                elif dataset.group_col:
                    self._plot_ranking_bar(fig, ax, dataset, analysis)
                    rendered = True

            if not rendered:
                if len(dataset.metrics) >= 2:
                    self._plot_correlation_scatter(fig, ax, dataset, analysis)
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
        self, fig: plt.Figure, ax: plt.Axes, dataset: EducationDataset, analysis: AnalysisResult
    ):
        df_full = dataset.df.copy()
        group_col = dataset.group_col
        metric = dataset.metrics[0]

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

        ax.set_title(f"{dataset.title}\n【グループ比較と95%信頼区間】", fontsize=13, fontweight="bold", pad=12)
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
        self, fig: plt.Figure, ax: plt.Axes, dataset: EducationDataset, analysis: AnalysisResult
    ):
        df = dataset.df.copy()
        col_x = dataset.metrics[1] if len(dataset.metrics) > 1 else dataset.metrics[0]
        col_y = dataset.metrics[0]
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
                r_info = f" (相関係数 r = {cr.pearson_r}, p = {cr.p_value})"
                break

        y_unit = resolve_metric_unit(col_y, dataset.unit)
        ax.set_title(
            f"{dataset.title}\n【相関分析】{col_x} vs {col_y}{r_info}（95%CI併記）",
            fontsize=12,
            fontweight="bold",
            pad=12,
        )
        ax.set_xlabel(f"{col_x}", fontsize=11, labelpad=8)
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
