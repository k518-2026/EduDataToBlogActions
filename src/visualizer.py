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
import seaborn as sns

from src.analyzer import AnalysisResult
from src.config import TEMP_DIR
from src.fetchers.base import EducationDataset

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

    def _plot_trend_lines(
        self, fig: plt.Figure, ax: plt.Axes, dataset: EducationDataset, analysis: AnalysisResult
    ):
        df = dataset.df.copy()
        time_col = dataset.time_col
        group_col = dataset.group_col
        primary_metric = dataset.metrics[0]

        palette = sns.color_palette("tab10")

        if group_col and group_col in df.columns:
            groups = df[group_col].unique()
            for idx, grp in enumerate(groups):
                sub = df[df[group_col] == grp].sort_values(by=time_col)
                color = palette[idx % len(palette)]
                line = ax.plot(
                    sub[time_col],
                    sub[primary_metric],
                    marker="o",
                    linewidth=2.5,
                    markersize=6,
                    label=str(grp),
                    color=color,
                )
                if len(sub) > 0:
                    last_x = sub[time_col].iloc[-1]
                    last_y = sub[primary_metric].iloc[-1]
                    ax.annotate(
                        f"{last_y}{dataset.unit}",
                        (last_x, last_y),
                        textcoords="offset points",
                        xytext=(8, -3),
                        fontsize=9,
                        fontweight="bold",
                        color=color,
                    )
        else:
            for idx, m in enumerate(dataset.metrics):
                if m in df.columns:
                    sub = df.sort_values(by=time_col)
                    color = palette[idx % len(palette)]
                    ax.plot(
                        sub[time_col],
                        sub[m],
                        marker="s",
                        linewidth=2.5,
                        markersize=6,
                        label=m,
                        color=color,
                    )
                    last_x = sub[time_col].iloc[-1]
                    last_y = sub[m].iloc[-1]
                    ax.annotate(
                        f"{last_y}{dataset.unit}",
                        (last_x, last_y),
                        textcoords="offset points",
                        xytext=(8, -3),
                        fontsize=9,
                        fontweight="bold",
                        color=color,
                    )

        ax.set_title(dataset.title, fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel(f"{time_col} (年/年度)", fontsize=11, labelpad=8)
        ax.set_ylabel(f"値 ({dataset.unit})", fontsize=11, labelpad=8)
        ax.legend(title="", frameon=True, facecolor="white", edgecolor="none")
        ax.grid(True, linestyle="--", alpha=0.5)

    def _plot_ranking_bar(
        self, fig: plt.Figure, ax: plt.Axes, dataset: EducationDataset, analysis: AnalysisResult
    ):
        df = dataset.df.copy()
        group_col = dataset.group_col
        metric = dataset.metrics[0]

        if dataset.time_col and dataset.time_col in df.columns:
            latest_time = df[dataset.time_col].max()
            df = df[df[dataset.time_col] == latest_time]

        sorted_df = df.groupby(group_col)[metric].mean().sort_values(ascending=True).reset_index()

        colors = []
        for name in sorted_df[group_col]:
            name_str = str(name)
            if "日本" in name_str or "Japan" in name_str:
                colors.append("#e63946")  # Red
            elif "平均" in name_str or "OECD" in name_str:
                colors.append("#f4a261")  # Orange
            else:
                colors.append("#457b9d")  # Slate blue

        bars = ax.barh(sorted_df[group_col], sorted_df[metric], color=colors, height=0.65)

        for bar in bars:
            width = bar.get_width()
            ax.annotate(
                f"{width:.1f}{dataset.unit}",
                xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(6, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=9,
                fontweight="bold",
                color="#333333",
            )

        ax.set_title(dataset.title, fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel(f"{metric} ({dataset.unit})", fontsize=11, labelpad=8)
        ax.set_ylabel("", fontsize=11)
        ax.grid(True, axis="x", linestyle="--", alpha=0.5)

        max_val = sorted_df[metric].max()
        ax.set_xlim(0, max_val * 1.15)

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
            color="#2a9d8f",
            scatter_kws={"s": 70, "alpha": 0.8},
            line_kws={"color": "#e76f51", "linewidth": 2},
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
                )

        r_info = ""
        for cr in analysis.correlations:
            if (cr.metric_x == col_x and cr.metric_y == col_y) or (
                cr.metric_x == col_y and cr.metric_y == col_x
            ):
                r_info = f" (相関係数 r = {cr.pearson_r}, p = {cr.p_value})"
                break

        ax.set_title(f"{dataset.title}\n【相関分析】{col_x} vs {col_y}{r_info}", fontsize=12, fontweight="bold", pad=12)
        ax.set_xlabel(f"{col_x}", fontsize=11, labelpad=8)
        ax.set_ylabel(f"{col_y} ({dataset.unit})", fontsize=11, labelpad=8)
        ax.grid(True, linestyle="--", alpha=0.5)
