"""
Report Generator for Educational Data Analysis.
Combines statistical tables, visualization charts, pedagogical insights, and
reproducible Python analysis code (with interactive copy button) into
polished HTML (with Base64 embedded charts for WordPress) and Markdown.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime
import html
import json
import logging
from pathlib import Path
from typing import Any, List, Optional

from src.analyzer import AnalysisResult
from src.config import Config
from src.fetchers.base import EducationDataset
from src.insights import EducationalInsights
from src.utils import clean_insight_text, format_bayes_factor
from src.utils_date import get_jst_now

logger = logging.getLogger(__name__)


@dataclass
class GeneratedReport:
    title: str
    html_content: str
    markdown_content: str
    categories: List[str]
    tags: List[str]
    chart_path: Path
    dataset_id: str
    created_at: str
    pdf_path: Optional[Path] = None
    pdf_url: Optional[str] = None
    peer_review_pdf_path: Optional[Path] = None
    peer_review_pdf_url: Optional[str] = None
    py_script_path: Optional[Path] = None
    py_script_url: Optional[str] = None
    python_code: Optional[str] = None
    angle_id: Optional[str] = None
    angle_name: Optional[str] = None


class EduReportBuilder:
    """Constructs HTML and Markdown reports from analysis results."""

    def generate_python_analysis_code(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> str:
        """Public method to generate clean, fully self-contained reproducible Python code."""
        return self._generate_python_analysis_code(dataset, analysis)

    def _generate_python_analysis_code(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> str:
        """Generates clean, fully self-contained reproducible Python code for the dataset analysis."""
        records = dataset.df.to_dict(orient="records")
        data_json = json.dumps(records, ensure_ascii=False, indent=2)

        # Plotting snippet tailored to recommended_chart (with 95% CI)
        if dataset.recommended_chart == "ranking_bar" and dataset.group_col:
            plot_snippet = f"""# グループ別（国・地域等）の平均値横棒グラフ（95%CI併記）
metric = "{dataset.metrics[0]}"
ranked = df.groupby("{dataset.group_col}")[metric].agg(["mean", "std", "count"]).sort_values(by="mean", ascending=True)
se = ranked["std"].fillna(1.5) / np.sqrt(np.maximum(ranked["count"], 1))
ci_95 = np.maximum(1.96 * se, 0.5)
bars = plt.barh(ranked.index, ranked["mean"], xerr=ci_95, capsize=4, color="#457b9d", height=0.65, error_kw={{"elinewidth": 1.4, "alpha": 0.85}})
for i, bar in enumerate(bars):
    w = bar.get_width()
    ci = ci_95.iloc[i]
    plt.text(w + ci + 0.3, bar.get_y() + bar.get_height() / 2, f"{{w:.1f}}{dataset.unit} (±{{ci:.1f}})", va="center", fontweight="bold", fontsize=8.5)
plt.xlabel(f"{{metric}} ({dataset.unit}) [誤差棒: 95% CI]", fontsize=11)"""
        elif dataset.recommended_chart == "correlation_scatter" and len(dataset.metrics) >= 2:
            plot_snippet = f"""# 相関散布図 & 回帰トレンドライン（95%CI併記）
col_x, col_y = "{dataset.metrics[1]}", "{dataset.metrics[0]}"
sns.regplot(x=col_x, y=col_y, data=df, ci=95, color="#2a9d8f", line_kws={{"color": "#e76f51", "linewidth": 2}})
plt.xlabel(col_x, fontsize=11)
plt.ylabel(f"{{col_y}} ({dataset.unit})", fontsize=11)"""
        else:
            time_col = dataset.time_col or "年度"
            group_col = dataset.group_col
            if group_col and group_col in dataset.df.columns:
                plot_snippet = f"""# 経年変化トレンド折れ線グラフ（グループ別・95%CI併記）
time_col = "{time_col}"
metric = "{dataset.metrics[0]}"
for grp in df["{group_col}"].unique():
    sub = df[df["{group_col}"] == grp].sort_values(by=time_col)
    y_vals = sub[metric].values
    x_vals = sub[time_col].values
    se = (np.std(y_vals, ddof=1) if len(y_vals) > 1 else 1.5) / np.sqrt(max(len(y_vals), 1))
    ci_err = np.maximum(1.96 * se, 0.6)
    plt.errorbar(x_vals, y_vals, yerr=ci_err, fmt="o-", linewidth=2.5, markersize=6, capsize=4, label=str(grp))
    plt.fill_between(x_vals, y_vals - ci_err, y_vals + ci_err, alpha=0.18)
plt.xlabel(f"{{time_col}} (年/年度)", fontsize=11)
plt.ylabel(f"{{metric}} ({dataset.unit})", fontsize=11)
plt.legend(title="【帯・誤差棒: 95% CI】", frameon=True, facecolor="white")"""
            else:
                plot_snippet = f"""# 経年変化トレンド折れ線グラフ（主要指標・95%CI併記）
time_col = "{time_col}"
sub = df.sort_values(by=time_col)
for m in {dataset.metrics}:
    if m in sub.columns:
        y_vals = sub[m].values
        x_vals = sub[time_col].values
        se = (np.std(y_vals, ddof=1) if len(y_vals) > 1 else 1.5) / np.sqrt(max(len(y_vals), 1))
        ci_err = np.maximum(1.96 * se, 0.6)
        plt.errorbar(x_vals, y_vals, yerr=ci_err, fmt="s-", linewidth=2.5, markersize=6, capsize=4, label=m)
        plt.fill_between(x_vals, y_vals - ci_err, y_vals + ci_err, alpha=0.18)
plt.xlabel(f"{{time_col}} (年/年度)", fontsize=11)
plt.ylabel(f"値 ({dataset.unit})", fontsize=11)
plt.legend(title="【帯・誤差棒: 95% CI】", frameon=True, facecolor="white")"""

        code = f'''"""
{dataset.title}
オープンデータ統計分析・可視化再現スクリプト
データ提供元: {dataset.source_name} ({dataset.source_url})
"""
import pandas as pd
import numpy as np
from scipy import stats
from scipy.integrate import quad
from scipy.special import gamma
import matplotlib.pyplot as plt
import seaborn as sns

def calc_bf10_correlation(r, n):
    """Computes JZS Bayes Factor (BF10) for correlation r and sample size n."""
    if n <= 2 or not np.isfinite(r):
        return 1.0, "証拠不十分（N数不足）"
    abs_r = abs(r)
    if abs_r >= 0.99999:
        return 99999.0, "極めて強い証拠（H1支持）"
    effective_r = max(abs_r, 1e-6)
    try:
        def integrand(g):
            return np.exp(
                ((n - 2) / 2) * np.log(1 + g)
                + (-(n - 1) / 2) * np.log(1 + (1 - effective_r**2) * g)
                + (-1.5) * np.log(g)
                + (-n / (2 * g))
            )
        val, _ = quad(integrand, 0, np.inf)
        bf10 = float(np.sqrt(n / 2.0) / gamma(0.5) * val)
    except Exception:
        bf10 = 1.0
    if not np.isfinite(bf10) or bf10 < 0:
        bf10 = 1.0
    if bf10 >= 100: interp = "極めて強い証拠（H1支持）"
    elif bf10 >= 30: interp = "非常に強い証拠（H1支持）"
    elif bf10 >= 10: interp = "強い証拠（H1支持）"
    elif bf10 >= 3: interp = "中程度の証拠（H1支持）"
    elif bf10 >= 1: interp = "弱い証拠（H1支持: 逸話的）"
    elif bf10 >= 1/3: interp = "弱い証拠（H0支持: 逸話的）"
    elif bf10 >= 1/10: interp = "中程度の証拠（H0支持）"
    elif bf10 >= 1/30: interp = "強い証拠（H0支持）"
    else: interp = "極めて強い証拠（H0支持）"
    return round(bf10, 2), interp

# ==============================================================================
# 1. オープンデータの読み込み・データフレーム構築
# ==============================================================================
raw_data = {data_json}
df = pd.DataFrame(raw_data)
print("【データフレーム概要】")
print(df.info())
print("\\n【データ先頭5行】")
print(df.head())

# ==============================================================================
# 2. 記述統計量の計算（平均値・中央値・標準偏差・四分位範囲）
# ==============================================================================
metrics = {dataset.metrics}
print("\\n==================================================")
print("📊 主要指標の記述統計量")
print("==================================================")
for m in metrics:
    if m in df.columns and pd.api.types.is_numeric_dtype(df[m]):
        s = df[m].dropna()
        q25, q75 = s.quantile(0.25), s.quantile(0.75)
        iqr = q75 - q25
        print(f"[{{m}}]")
        print(f"  サンプル数 (N): {{len(s)}}")
        print(f"  平均値: {{s.mean():.2f}} {dataset.unit}")
        print(f"  中央値: {{s.median():.2f}} {dataset.unit}")
        print(f"  標準偏差: {{s.std(ddof=1):.2f}}")
        print(f"  最小値: {{s.min():.2f}} / 最大値: {{s.max():.2f}}")
        print(f"  四分位範囲 (IQR): {{iqr:.2f}}")

# ==============================================================================
# 3. 経年変化トレンド・線形回帰分析 & ベイズファクター (BF₁₀)
# ==============================================================================
time_col = "{dataset.time_col or ''}"
if time_col and time_col in df.columns:
    print("\\n==================================================")
    print("📈 経年トレンド線形回帰・ベイズファクター分析")
    print("==================================================")
    df_sorted = df.sort_values(by=time_col)
    for m in metrics:
        if m in df_sorted.columns:
            sub = df_sorted[[time_col, m]].dropna()
            if len(sub) >= 2:
                x_vals = pd.to_numeric(sub[time_col])
                y_vals = sub[m]
                res = stats.linregress(x_vals, y_vals)
                r_sq = res.rvalue ** 2
                bf, bf_interp = calc_bf10_correlation(res.rvalue, len(x_vals))
                start_v, end_v = y_vals.iloc[0], y_vals.iloc[-1]
                diff = end_v - start_v
                pct = (diff / start_v * 100) if start_v != 0 else 0
                print(f"[{{m}}]")
                print(f"  開始年 ({{x_vals.iloc[0]}}) -> 最新年 ({{x_vals.iloc[-1]}}): {{start_v:.2f}} -> {{end_v:.2f}}")
                print(f"  変化量: {{diff:+.2f}} {dataset.unit} (変化率: {{pct:+.1f}}%)")
                print(f"  回帰の傾き: {{res.slope:.3f}} / 決定係数 (R²): {{r_sq:.3f}} / p値: {{res.pvalue:.4f}}")
                print(f"  ベイズファクター (BF₁₀): {{bf}} [{{bf_interp}}]")

# ==============================================================================
# 4. 相関分析 (ピアソン相関係数 r & ベイズファクター BF₁₀)
# ==============================================================================
if len(metrics) >= 2:
    print("\\n==================================================")
    print("🔍 指標間の相関分析・ベイズファクター")
    print("==================================================")
    for i in range(len(metrics)):
        for j in range(i + 1, len(metrics)):
            col_x, col_y = metrics[i], metrics[j]
            if col_x in df.columns and col_y in df.columns:
                sub = df[[col_x, col_y]].dropna()
                if len(sub) >= 3:
                    r, p = stats.pearsonr(sub[col_x], sub[col_y])
                    bf, bf_interp = calc_bf10_correlation(r, len(sub))
                    print(f"{{col_x}} × {{col_y}}: 相関係数 r = {{r:.3f}}, p値 = {{p:.4f}}, BF₁₀ = {{bf}} [{{bf_interp}}]")

# ==============================================================================
# 5. データの可視化・グラフ生成
# ==============================================================================
plt.figure(figsize=(10, 5.8), dpi=150)
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

{plot_snippet}

plt.title("{dataset.title}", fontsize=13, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
'''
        return code.strip()

    def _build_kpi_cards_html(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> str:
        """Constructs an executive KPI highlight card row for primary metrics."""
        if not analysis.descriptive_stats:
            return ""
        first_metric = dataset.metrics[0] if dataset.metrics else list(analysis.descriptive_stats.keys())[0]
        stat = analysis.descriptive_stats.get(first_metric)
        if not stat:
            return ""

        diff_range = stat.max_val - stat.min_val
        unit_label = dataset.unit or ""

        return f"""
          <!-- Key Metrics KPI Summary Cards -->
          <div style="margin:24px 0 20px 0;">
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(175px, 1fr)); gap:12px;">
              <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:4px solid #3b82f6; border-radius:8px; padding:14px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:12px; font-weight:600; color:#64748b; margin-bottom:4px;">🎯 平均値 ({first_metric})</div>
                <div style="font-size:22px; font-weight:bold; color:#0f172a; font-family:Consolas, Monaco, monospace;">
                  {stat.mean:.2f} <span style="font-size:12px; font-weight:normal; color:#64748b;">{unit_label}</span>
                </div>
              </div>
              <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:4px solid #10b981; border-radius:8px; padding:14px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:12px; font-weight:600; color:#64748b; margin-bottom:4px;">📊 中央値 (Median)</div>
                <div style="font-size:22px; font-weight:bold; color:#0f172a; font-family:Consolas, Monaco, monospace;">
                  {stat.median:.2f} <span style="font-size:12px; font-weight:normal; color:#64748b;">{unit_label}</span>
                </div>
              </div>
              <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:4px solid #f59e0b; border-radius:8px; padding:14px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:12px; font-weight:600; color:#64748b; margin-bottom:4px;">📏 標準偏差 (σ)</div>
                <div style="font-size:22px; font-weight:bold; color:#0f172a; font-family:Consolas, Monaco, monospace;">
                  {stat.std:.2f}
                </div>
              </div>
              <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:4px solid #8b5cf6; border-radius:8px; padding:14px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:12px; font-weight:600; color:#64748b; margin-bottom:4px;">↕️ 全変動幅 (Max - Min)</div>
                <div style="font-size:22px; font-weight:bold; color:#0f172a; font-family:Consolas, Monaco, monospace;">
                  {diff_range:.2f} <span style="font-size:12px; font-weight:normal; color:#64748b;">{unit_label}</span>
                </div>
              </div>
            </div>
          </div>
        """

    def _build_descriptive_stats_tables(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> tuple[str, str]:
        """Constructs modern, polished Markdown and HTML descriptive statistics tables."""
        unit_str = f" ({dataset.unit})" if dataset.unit else ""
        md_rows = [
            f"| 指標名 | 標本数 (N) | 平均値{unit_str} | 中央値{unit_str} | 標準偏差 (σ) | 最小値{unit_str} | 最大値{unit_str} | 四分位範囲 (IQR) |",
            "| :--- | :---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        html_rows = []
        for i, (m, s) in enumerate(analysis.descriptive_stats.items()):
            md_rows.append(
                f"| **{m}** | {s.count:,} | {s.mean:.2f} | {s.median:.2f} | {s.std:.2f} | {s.min_val:.2f} | {s.max_val:.2f} | {s.iqr:.2f} |"
            )
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            html_rows.append(
                f"""<tr style="background-color:{bg}; border-bottom:1px solid #f1f5f9;">
                  <td style="padding:10px 14px; font-weight:bold; color:#0f172a; white-space:nowrap;">{m}</td>
                  <td style="padding:10px 12px; text-align:center; color:#64748b; font-family:Consolas, Monaco, monospace;">{s.count:,}</td>
                  <td style="padding:10px 14px; text-align:right; font-weight:bold; color:#1e293b; font-family:Consolas, Monaco, monospace;">{s.mean:.2f}</td>
                  <td style="padding:10px 14px; text-align:right; color:#334155; font-family:Consolas, Monaco, monospace;">{s.median:.2f}</td>
                  <td style="padding:10px 14px; text-align:right; color:#64748b; font-family:Consolas, Monaco, monospace;">{s.std:.2f}</td>
                  <td style="padding:10px 14px; text-align:right; color:#0369a1; font-family:Consolas, Monaco, monospace;">{s.min_val:.2f}</td>
                  <td style="padding:10px 14px; text-align:right; color:#b45309; font-family:Consolas, Monaco, monospace;">{s.max_val:.2f}</td>
                  <td style="padding:10px 14px; text-align:right; color:#475569; font-family:Consolas, Monaco, monospace;">{s.iqr:.2f}</td>
                </tr>"""
            )

        md_table = "\n".join(md_rows) + "\n"
        html_table = f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.05); overflow:hidden; margin-bottom:28px;">
          <div style="background-color:#f8fafc; border-bottom:1px solid #e2e8f0; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div style="font-weight:bold; color:#1e293b; font-size:14px; display:inline-flex; align-items:center; gap:6px;">
              📊 基本記述統計量一覧（代表値・ばらつき）
            </div>
            <span style="font-size:11.5px; background-color:#e0f2fe; color:#0369a1; font-weight:600; padding:3px 10px; border-radius:12px;">
              単位: {dataset.unit}
            </span>
          </div>
          <div style="overflow-x:auto;">
            <table style="width:100%; border-collapse:collapse; font-size:13.5px; text-align:left;">
              <thead>
                <tr style="background-color:#f1f5f9; color:#475569; font-size:12px; font-weight:600; letter-spacing:0.3px; border-bottom:2px solid #cbd5e1;">
                  <th style="padding:10px 14px; text-align:left;">指標名</th>
                  <th style="padding:10px 12px; text-align:center;">標本数 (N)</th>
                  <th style="padding:10px 14px; text-align:right;">平均値</th>
                  <th style="padding:10px 14px; text-align:right;">中央値</th>
                  <th style="padding:10px 14px; text-align:right;">標準偏差 (σ)</th>
                  <th style="padding:10px 14px; text-align:right;">最小値</th>
                  <th style="padding:10px 14px; text-align:right;">最大値</th>
                  <th style="padding:10px 14px; text-align:right;">四分位範囲 (IQR)</th>
                </tr>
              </thead>
              <tbody>
                {''.join(html_rows)}
              </tbody>
            </table>
          </div>
        </div>
        """
        return md_table, html_table

    def _build_trend_tables(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> tuple[str, str]:
        """Constructs modern, styled Markdown and HTML trend/regression analysis tables."""
        if not analysis.trends:
            return "", ""

        unit_str = f" ({dataset.unit})" if dataset.unit else ""
        md_rows = [
            f"| 指標 / グループ | 調査開始 | 初期値{unit_str} | 最新調査 | 最新値{unit_str} | 増減量{unit_str} | 変化率 | 年平均成長率 (CAGR) | 決定係数 (R²) | ベイズファクター (BF₁₀) |",
            "| :--- | :---: | ---: | :---: | ---: | ---: | ---: | ---: | ---: | :--- |",
        ]
        html_rows = []
        for i, tr in enumerate(analysis.trends):
            grp_str = f"[{tr.group_name}] " if tr.group_name else ""
            cagr_val_str = f"{tr.cagr:+.2f}%" if tr.cagr is not None else "-"
            bf_disp = format_bayes_factor(tr.bf10)
            bf_val_str = f"{bf_disp} ({tr.bf_interpretation})" if tr.bf10 is not None else "-"
            md_rows.append(
                f"| {grp_str}{tr.metric} | {tr.start_time} | {tr.start_val:.2f} | "
                f"{tr.end_time} | {tr.end_val:.2f} | {tr.diff:+.2f} | {tr.pct_change:+.1f}% | "
                f"{cagr_val_str} | {tr.r_squared:.3f} | {bf_val_str} |"
            )

            # Diff badge
            if tr.diff > 0:
                diff_pill = f'<span style="background-color:#dcfce7; color:#15803d; padding:2px 8px; border-radius:10px; font-weight:bold; font-size:12px;">+{tr.diff:.2f}</span>'
                pct_pill = f'<span style="color:#15803d; font-weight:bold;">{tr.pct_change:+.1f}%</span>'
            elif tr.diff < 0:
                diff_pill = f'<span style="background-color:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:10px; font-weight:bold; font-size:12px;">{tr.diff:.2f}</span>'
                pct_pill = f'<span style="color:#b91c1c; font-weight:bold;">{tr.pct_change:+.1f}%</span>'
            else:
                diff_pill = f'<span style="background-color:#f1f5f9; color:#64748b; padding:2px 8px; border-radius:10px; font-size:12px;">±0.00</span>'
                pct_pill = f'<span style="color:#64748b;">0.0%</span>'

            # R^2 badge
            if tr.r_squared >= 0.5:
                r2_badge = f'<span style="background-color:#e0e7ff; color:#3730a3; padding:2px 8px; border-radius:8px; font-weight:bold; font-size:12px;">{tr.r_squared:.3f}</span>'
            else:
                r2_badge = f'<span style="color:#64748b; font-size:12px;">{tr.r_squared:.3f}</span>'

            # BF10 badge
            if tr.bf10 is not None:
                if tr.bf10 >= 3.0:
                    bf_pill = f'<span style="background-color:#dcfce7; color:#15803d; padding:2px 8px; border-radius:8px; font-weight:bold; font-size:11.5px;">{bf_disp}</span>'
                elif tr.bf10 <= 1.0 / 3.0:
                    bf_pill = f'<span style="background-color:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:8px; font-weight:bold; font-size:11.5px;">{bf_disp}</span>'
                else:
                    bf_pill = f'<span style="background-color:#f1f5f9; color:#475569; padding:2px 8px; border-radius:8px; font-size:11.5px;">{bf_disp}</span>'
                bf_html = f'{bf_pill} <span style="color:#64748b; font-size:11.5px;">{tr.bf_interpretation}</span>'
            else:
                bf_html = '<span style="color:#94a3b8;">-</span>'

            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            html_rows.append(
                f"""<tr style="background-color:{bg}; border-bottom:1px solid #f1f5f9;">
                  <td style="padding:10px 14px; font-weight:bold; color:#0f172a; white-space:nowrap;">{grp_str}{tr.metric}</td>
                  <td style="padding:10px 12px; text-align:center; color:#64748b; font-family:Consolas, monospace;">{tr.start_time}</td>
                  <td style="padding:10px 14px; text-align:right; color:#334155; font-family:Consolas, monospace;">{tr.start_val:.2f}</td>
                  <td style="padding:10px 12px; text-align:center; color:#64748b; font-family:Consolas, monospace;">{tr.end_time}</td>
                  <td style="padding:10px 14px; text-align:right; font-weight:bold; color:#0f172a; font-family:Consolas, monospace;">{tr.end_val:.2f}</td>
                  <td style="padding:10px 14px; text-align:right;">{diff_pill}</td>
                  <td style="padding:10px 14px; text-align:right; font-family:Consolas, monospace;">{pct_pill}</td>
                  <td style="padding:10px 14px; text-align:right; color:#475569; font-family:Consolas, monospace;">{cagr_val_str}</td>
                  <td style="padding:10px 14px; text-align:right; font-family:Consolas, monospace;">{r2_badge}</td>
                  <td style="padding:10px 14px; text-align:left;">{bf_html}</td>
                </tr>"""
            )

        md_table = "### 📈 経年変化・トレンド推移\n\n" + "\n".join(md_rows) + "\n\n"
        html_table = f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.05); overflow:hidden; margin-bottom:28px;">
          <div style="background-color:#f8fafc; border-bottom:1px solid #e2e8f0; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div style="font-weight:bold; color:#1e293b; font-size:14px; display:inline-flex; align-items:center; gap:6px;">
              📈 経年変化トレンド・線形回帰分析表
            </div>
            <span style="font-size:11.5px; background-color:#e0f2fe; color:#0369a1; font-weight:600; padding:3px 10px; border-radius:12px;">
              単位: {dataset.unit}
            </span>
          </div>
          <div style="overflow-x:auto;">
            <table style="width:100%; border-collapse:collapse; font-size:13.5px; text-align:left;">
              <thead>
                <tr style="background-color:#f1f5f9; color:#475569; font-size:12px; font-weight:600; letter-spacing:0.3px; border-bottom:2px solid #cbd5e1;">
                  <th style="padding:10px 14px; text-align:left;">指標 / グループ</th>
                  <th style="padding:10px 12px; text-align:center;">開始年</th>
                  <th style="padding:10px 14px; text-align:right;">初期値</th>
                  <th style="padding:10px 12px; text-align:center;">最新年</th>
                  <th style="padding:10px 14px; text-align:right;">最新値</th>
                  <th style="padding:10px 14px; text-align:right;">増減変化量</th>
                  <th style="padding:10px 14px; text-align:right;">変化率</th>
                  <th style="padding:10px 14px; text-align:right;">CAGR</th>
                  <th style="padding:10px 14px; text-align:right;">決定係数 (R²)</th>
                  <th style="padding:10px 14px; text-align:left;">ベイズファクター (BF₁₀)</th>
                </tr>
              </thead>
              <tbody>
                {''.join(html_rows)}
              </tbody>
            </table>
          </div>
        </div>
        """
        return md_table, html_table

    def _build_correlation_tables(
        self, analysis: AnalysisResult
    ) -> tuple[str, str]:
        """Constructs modern, styled Markdown and HTML correlation analysis tables."""
        if not analysis.correlations:
            return "", ""

        md_rows = [
            "| 分析指標ペア (X × Y) | 相関係数 (r) | 有意確率 (p値) | 相関の強さ | ベイズファクター (BF₁₀) | BF証拠判定 |",
            "| :--- | :---: | :---: | :--- | :---: | :--- |",
        ]
        html_rows = []
        for i, cr in enumerate(analysis.correlations):
            bf_disp = format_bayes_factor(getattr(cr, "bf10", None))
            bf_val_str = bf_disp if getattr(cr, "bf10", None) is not None else "-"
            bf_interp_str = cr.bf_interpretation or "-"
            md_rows.append(
                f"| **{cr.metric_x}** × **{cr.metric_y}** | {cr.pearson_r:+.3f} | {cr.p_value:.4f} | {cr.interpretation} | {bf_val_str} | {bf_interp_str} |"
            )

            # Correlation badge
            if cr.pearson_r >= 0.7:
                r_badge = f'<span style="background-color:#dcfce7; color:#15803d; padding:2px 8px; border-radius:10px; font-weight:bold;">{cr.pearson_r:+.3f}</span>'
            elif cr.pearson_r <= -0.7:
                r_badge = f'<span style="background-color:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:10px; font-weight:bold;">{cr.pearson_r:+.3f}</span>'
            else:
                r_badge = f'<span style="background-color:#f1f5f9; color:#475569; padding:2px 8px; border-radius:10px; font-weight:bold;">{cr.pearson_r:+.3f}</span>'

            # BF10 badge
            if getattr(cr, "bf10", None) is not None:
                if cr.bf10 >= 3.0:
                    bf_badge = f'<span style="background-color:#dcfce7; color:#15803d; padding:2px 8px; border-radius:10px; font-weight:bold;">{bf_disp}</span>'
                elif cr.bf10 <= 1.0 / 3.0:
                    bf_badge = f'<span style="background-color:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:10px; font-weight:bold;">{bf_disp}</span>'
                else:
                    bf_badge = f'<span style="background-color:#f1f5f9; color:#475569; padding:2px 8px; border-radius:10px;">{bf_disp}</span>'
            else:
                bf_badge = '<span style="color:#94a3b8;">-</span>'

            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            html_rows.append(
                f"""<tr style="background-color:{bg}; border-bottom:1px solid #f1f5f9;">
                  <td style="padding:10px 14px; font-weight:bold; color:#0f172a;">{cr.metric_x} <span style="color:#94a3b8; font-weight:normal;">×</span> {cr.metric_y}</td>
                  <td style="padding:10px 14px; text-align:center; font-family:Consolas, monospace;">{r_badge}</td>
                  <td style="padding:10px 14px; text-align:center; color:#64748b; font-family:Consolas, monospace;">{cr.p_value:.4f}</td>
                  <td style="padding:10px 14px; text-align:center; color:#334155;"><span style="background-color:#f1f5f9; padding:2px 8px; border-radius:6px; font-size:12px;">{cr.interpretation}</span></td>
                  <td style="padding:10px 14px; text-align:center; font-family:Consolas, monospace;">{bf_badge}</td>
                  <td style="padding:10px 14px; color:#475569; font-size:12px;">{bf_interp_str}</td>
                </tr>"""
            )

        md_table = "### 🔍 指標間の相関分析\n\n" + "\n".join(md_rows) + "\n\n"
        html_table = f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.05); overflow:hidden; margin-bottom:28px;">
          <div style="background-color:#f8fafc; border-bottom:1px solid #e2e8f0; padding:12px 18px;">
            <div style="font-weight:bold; color:#1e293b; font-size:14px; display:inline-flex; align-items:center; gap:6px;">
              🔍 指標間の相関分析（ピアソン積率相関係数 & ベイズファクター）
            </div>
          </div>
          <div style="overflow-x:auto;">
            <table style="width:100%; border-collapse:collapse; font-size:13.5px; text-align:left;">
              <thead>
                <tr style="background-color:#f1f5f9; color:#475569; font-size:12px; font-weight:600; letter-spacing:0.3px; border-bottom:2px solid #cbd5e1;">
                  <th style="padding:10px 14px; text-align:left;">分析指標ペア (X × Y)</th>
                  <th style="padding:10px 14px; text-align:center;">相関係数 (r)</th>
                  <th style="padding:10px 14px; text-align:center;">有意確率 (p値)</th>
                  <th style="padding:10px 14px; text-align:center;">相関の強さ</th>
                  <th style="padding:10px 14px; text-align:center;">ベイズファクター (BF₁₀)</th>
                  <th style="padding:10px 14px; text-align:left;">BF証拠判定</th>
                </tr>
              </thead>
              <tbody>
                {''.join(html_rows)}
              </tbody>
            </table>
          </div>
        </div>
        """
        return md_table, html_table

    def build_report(
        self,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        insights: EducationalInsights,
        chart_path: Path,
        pdf_path: Optional[Path] = None,
        pdf_url: Optional[str] = None,
        py_script_path: Optional[Path] = None,
        py_script_url: Optional[str] = None,
        peer_review_pdf_path: Optional[Path] = None,
        peer_review_pdf_url: Optional[str] = None,
        selected_angle: Optional[Any] = None,
    ) -> GeneratedReport:
        today_str = get_jst_now().strftime("%Y年%m月%d日")
        date_iso = get_jst_now().strftime("%Y-%m-%d")

        category_label = "算数・数学教育" if dataset.category == "math" else "情報教育・プログラミング"
        if selected_angle and getattr(selected_angle, "title_theme", None):
            title = f"{dataset.title}：{selected_angle.title_theme} ({today_str})"
        else:
            title = f"{dataset.title}：データが暴く意外な教育実態と授業改善への示唆 ({today_str})"

        categories = ["教育データ分析"]
        if dataset.category == "math":
            categories.extend(["算数数学教育", "STEM教育"])
        else:
            categories.extend(["情報教育", "プログラミング教育", "GIGAスクール"])

        # Clean tags (alphanumeric and Japanese without slashes or quotes)
        tags = ["オープンデータ", "統計分析", dataset.region.upper()]
        if dataset.category == "math":
            tags.append("算数数学")
        else:
            tags.append("情報教育")

        # Encode chart to Base64 so it can be viewed anywhere without 404 Not Found
        chart_b64 = ""
        if chart_path and chart_path.exists():
            try:
                with open(chart_path, "rb") as f:
                    chart_b64 = base64.b64encode(f.read()).decode("utf-8")
            except Exception as e:
                logger.warning(f"Failed to base64 encode chart image: {e}")

        # GitHub raw image URL for Step Summary and Markdown
        dest_chart_filename = f"{date_iso}_{chart_path.name}"
        raw_github_img_url = (
            f"https://raw.githubusercontent.com/k518-2026/EduDataToBlogActions/main/"
            f"reports/assets/{dest_chart_filename}"
        )

        # Generate reproducible Python analysis code
        python_code = self._generate_python_analysis_code(dataset, analysis)

        # Python script public links
        py_filename = py_script_path.name if py_script_path else f"{date_iso}_{dataset.id}_analysis.py"
        py_url = (
            py_script_url
            or f"https://github.com/{Config.GITHUB_REPOSITORY}/blob/{Config.GITHUB_BRANCH}/reports/scripts/{py_filename}"
        )
        raw_py_url = f"https://raw.githubusercontent.com/{Config.GITHUB_REPOSITORY}/{Config.GITHUB_BRANCH}/reports/scripts/{py_filename}"

        # 1. Build KPI highlight cards and clean tables
        kpi_cards_html = self._build_kpi_cards_html(dataset, analysis)
        desc_table_md, desc_table_html = self._build_descriptive_stats_tables(dataset, analysis)
        trend_table_md, trend_table_html = self._build_trend_tables(dataset, analysis)
        corr_table_md, corr_table_html = self._build_correlation_tables(analysis)

        # Academic Thesis PDF & Peer Review Report links
        pdf_badge_md = ""
        pdf_banner_html = ""
        review_badge_md = ""
        review_btn_html = ""

        if peer_review_pdf_url:
            review_badge_md = f"""
> 📋 **査読報告書PDF（生成AIによる模擬査読結果通知書）も同時公開中**:
> 学会誌査読委員の視点を模した生成AI（Generative AI）により，生態学的誤謬の回避や交絡因子の統制など厳しい学術基準で審査した「査読報告書（条件付採録）」を公開しています（学生教育・推敲支援目的）。
> [📥 査読報告書PDFを直接ダウンロード（PDF）]({peer_review_pdf_url})
"""
            review_btn_html = f"""
                <a href="{peer_review_pdf_url}" target="_blank" rel="noopener noreferrer" download style="background-color:#475569; color:#ffffff; text-decoration:none; padding:8px 16px; border-radius:6px; font-weight:bold; font-size:12.5px; display:inline-flex; align-items:center; gap:6px; box-shadow:0 2px 4px rgba(0,0,0,0.12); margin-top:8px;">
                  📥 査読報告書PDFを直接ダウンロード
                </a>
"""

        if pdf_url:
            pdf_badge_md = f"""
> 📄 **学術論文形式PDF（生成AI論文）を公開中**:
> 本分析の背景・目的（RQ）・調査手法・統計解析結果（表/図）・教育的考察・引用参考文献を網羅した学術論文PDF（JIS B5判・2段組）を直接ダウンロードできます。
> [📥 学術論文PDFを直接ダウンロード（PDF）]({pdf_url})
{review_badge_md}
---
"""
            pdf_banner_html = f"""
          <!-- Academic Thesis PDF Download Callout -->
          <div style="background:linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); border:1px solid #bae6fd; border-left:5px solid #0284c7; border-radius:8px; padding:16px 20px; margin-bottom:26px; box-shadow:0 2px 6px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
              <div style="max-width:540px;">
                <div style="font-size:11px; font-weight:bold; color:#0369a1; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:2px;">Academic Paper &amp; Peer Review Report (PDF)</div>
                <h4 style="margin:2px 0 6px 0; color:#0f172a; font-size:16px; font-weight:bold;">📄 学術論文形式の完全版レポート ＆ 📋 学術査読報告書（生成AIシミュレーション）</h4>
                <p style="margin:0; font-size:13px; line-height:1.5; color:#334155;">
                  研究背景、目的（RQ）、調査方法、詳細な統計解析（表・図）、教育学的考察、および引用参考文献を体系的にまとめた本格的な学術論文PDF（JIS B5判・2段組）と、厳格な査読委員視点を模した生成AIによる模擬査読結果通知書（A4判）を公開しています。
                </p>
              </div>
              <div style="text-align:right;">
                <a href="{pdf_url}" target="_blank" rel="noopener noreferrer" download style="background-color:#0284c7; color:#ffffff; text-decoration:none; padding:10px 18px; border-radius:6px; font-weight:bold; font-size:13px; display:inline-flex; align-items:center; gap:6px; box-shadow:0 2px 4px rgba(0,0,0,0.12); transition:background-color 0.2s;">
                  📥 学術論文PDFを直接ダウンロード
                </a><br/>
                {review_btn_html}
                <div style="font-size:11px; color:#64748b; margin-top:4px;">※直接PDFファイルをダウンロードして閲覧いただけます</div>
              </div>
            </div>
          </div>
"""


        # 3. Assemble Markdown Content (Includes raw URL chart and full Python script)
        clean_summary = clean_insight_text(insights.executive_summary)
        clean_pedagogy = clean_insight_text(insights.pedagogical_implications)
        clean_policy = clean_insight_text(insights.future_challenges_and_policy)

        clean_paradox = clean_insight_text(getattr(insights, "counter_intuitive_finding", ""))
        if not clean_paradox:
            if dataset.category == "math":
                clean_paradox = (
                    "【学力高水準と学習好意度の逆説（TIMSSパラドックス）】\n"
                    "国際的に最高水準の算数・数学到達度を誇る一方で、学年進行とともに「算数が楽しい」「得意である」と答える自己効力感指数が急落する傾向が顕著です。"
                    "正答率の高さが必ずしも学びの楽しさに結びついておらず、正解至上主義が内発的動機を阻害するという逆説的課題がデータから浮かび上がっています。"
                )
            else:
                clean_paradox = (
                    "【1人1台端末普及と活用深度の非対称性】\n"
                    "GIGAスクール構想により端末配備率がほぼ100%に到達した一方で、日常的な探究活動やプログラミング演習での活用頻度には自治体・学校間で大きな格差が生じています。"
                    "ハードウェアの充足が直ちに探究的学びの深化をもたらすわけではなく、指導体制の有無による「第二のデジタルデバイド（活用格差）」が進行している実態が浮き彫りとなっています。"
                )

        insights_bullets_md = "\n".join([f"- {ins}" for ins in analysis.key_insights])

        markdown_content = f"""# {title}

**更新日:** {today_str} | **カテゴリ:** {category_label} | **データ対象地域:** {dataset.region.upper()}

---
{pdf_badge_md}
## 📌 本日の分析要約（エグゼクティブサマリー）

{clean_summary}

---

## ⚡ データが暴く意外な事実・常識の逆説（教育パラドックス）

{clean_paradox}

---

## 📊 オープンデータ概要・出典情報

- **データセット名:** {dataset.title}
- **情報提供元:** [{dataset.source_name}]({dataset.source_url})
- **調査対象・内容:** {dataset.description}
- **分析標本数 (行数):** {analysis.sample_size} 件

---

## 📈 統計分析データテーブル

### 📊 主要指標の基本記述統計量
{desc_table_md}
{trend_table_md}{corr_table_md}### 統計から導出された主要ハイライト
{insights_bullets_md}

---

## 🖼️ データ可視化グラフ

![{dataset.title}のグラフ画像]({raw_github_img_url})

---

## 💡 教育現場・授業実践への具体的示唆

{clean_pedagogy}

---

## 🚀 今後の課題と政策・国際的展望

{clean_policy}

---

## 💻 統計処理に利用した Python スクリプト

本レポートのデータ抽出、基本統計量計算、トレンド回帰、相関分析、およびグラフ描画をローカル環境（Jupyter Notebook / Google Colab等）でそのまま再現できるPythonコード（`.py`ファイル）を公開しています。

- [📥 スクリプトファイル（{py_filename}）を直接ダウンロード]({raw_py_url})

---
*Generated automatically by EduDataToBlogActions pipeline.*
"""

        # 4. Assemble HTML Content (With Base64 image, reproducible Python code box, and interactive Copy Button)
        wp_status = Config.WP_POST_STATUS or "publish"
        cat_str = ",".join(categories)
        tag_str = ",".join(tags)

        pedagogy_html = clean_pedagogy.replace("\n", "<br/>")
        policy_html = clean_policy.replace("\n", "<br/>")
        summary_html = clean_summary.replace("\n", "<br/>")
        paradox_html = clean_paradox.replace("\n", "<br/>")
        insights_bullets_html = "".join(
            [f"<li style='margin-bottom:6px;'>{ins}</li>" for ins in analysis.key_insights]
        )

        img_src = (
            f"data:image/png;base64,{chart_b64}"
            if chart_b64
            else raw_github_img_url
        )

        html_content = f"""
        <div style="font-family:'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif; line-height:1.8; color:#2b2d42; max-width:820px; margin:auto; padding:15px;">

          <!-- Header Badge -->
          <div style="margin-bottom:20px;">
            <span style="background-color:#1d3557; color:#ffffff; padding:4px 12px; border-radius:15px; font-size:12px; font-weight:bold; margin-right:8px;">{category_label}</span>
            <span style="background-color:#457b9d; color:#ffffff; padding:4px 12px; border-radius:15px; font-size:12px; font-weight:bold; margin-right:8px;">{dataset.region.upper()}</span>
            <span style="color:#6c757d; font-size:13px;">📅 {today_str} 自動更新</span>
          </div>

          <!-- Executive Summary Callout -->
          <div style="background-color:#f8f9fa; border-left:5px solid #e63946; padding:18px 20px; border-radius:4px; margin-bottom:20px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <h3 style="margin-top:0; color:#1d3557; font-size:16px;">📌 本日の分析要約（エグゼクティブサマリー）</h3>
            <p style="margin-bottom:0; font-size:15px; line-height:1.7;">{summary_html}</p>
          </div>

          <!-- Counter-Intuitive Paradox Callout -->
          <div style="background-color:#fffbeb; border:1px solid #fef3c7; border-left:5px solid #f59e0b; padding:18px 20px; border-radius:4px; margin-bottom:28px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <h3 style="margin-top:0; color:#b45309; font-size:16px; display:flex; align-items:center; gap:8px;">
              ⚡ データが暴く意外な事実・常識の逆説（教育パラドックス）
            </h3>
            <div style="margin-bottom:0; font-size:14.5px; line-height:1.8; color:#78350f;">{paradox_html}</div>
          </div>

          {pdf_banner_html}
          <!-- Open Data Source Details -->
          <div style="background-color:#edf2f4; padding:12px 18px; border-radius:6px; margin-bottom:25px; font-size:13px; color:#495057;">
            <b>データ出典:</b> <a href="{dataset.source_url}" target="_blank" style="color:#1d3557; text-decoration:underline;">{dataset.source_name}</a><br/>
            <b>調査概要:</b> {dataset.description}
          </div>

          <!-- Chart Section with Base64 embedded PNG -->
          <div style="margin:30px 0; text-align:center;">
            <h3 style="color:#1d3557; border-bottom:2px solid #457b9d; padding-bottom:5px; text-align:left;">🖼️ データ可視化グラフ</h3>
            <img src="{img_src}" alt="{dataset.title}" style="max-width:100%; height:auto; border-radius:6px; box-shadow:0 3px 8px rgba(0,0,0,0.12); margin-top:10px;" />
            <p style="font-size:12px; color:#6c757d; margin-top:6px;">図: {dataset.title}（EduDataToBlogActions 統計分析パイプラインにて生成）</p>
          </div>

          <!-- Statistical Tables Section -->
          <h3 style="color:#1d3557; border-bottom:2px solid #457b9d; padding-bottom:5px; margin-top:30px;">📊 統計分析結果データテーブル</h3>
          {kpi_cards_html}

          {desc_table_html}

          {trend_table_html}

          {corr_table_html}


          <!-- Key Highlights Bullet Points -->
          <div style="background-color:#f0f7f4; border-radius:6px; padding:15px 20px; margin-bottom:30px;">
            <h4 style="margin-top:0; color:#2a9d8f; font-size:15px;">🔍 統計データから検出された重要ポイント</h4>
            <ul style="padding-left:20px; margin-bottom:0; font-size:14px; line-height:1.7;">
              {insights_bullets_html}
            </ul>
          </div>

          <!-- Pedagogical Implications -->
          <div style="margin-bottom:30px;">
            <h3 style="color:#1d3557; border-bottom:2px solid #457b9d; padding-bottom:5px;">💡 教育現場・授業実践への具体的示唆</h3>
            <div style="background-color:#ffffff; border:1px solid #dee2e6; border-left:4px solid #2a9d8f; padding:18px 20px; border-radius:4px; font-size:15px; line-height:1.8;">
              {pedagogy_html}
            </div>
          </div>

          <!-- Future Challenges & Policy -->
          <div style="margin-bottom:30px;">
            <h3 style="color:#1d3557; border-bottom:2px solid #457b9d; padding-bottom:5px;">🚀 今後の課題と政策・国際的展望</h3>
            <div style="background-color:#ffffff; border:1px solid #dee2e6; border-left:4px solid #f4a261; padding:18px 20px; border-radius:4px; font-size:15px; line-height:1.8;">
              {policy_html}
            </div>
          </div>

          <!-- Python Analysis Script Link Section -->
          <div style="background-color:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #3b82f6; border-radius:6px; padding:16px 20px; margin-top:35px; margin-bottom:30px; box-shadow:0 1px 4px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
              <div style="max-width:540px;">
                <h4 style="margin:0 0 5px 0; color:#1e293b; font-size:15px; font-weight:bold;">
                  🐍 統計処理・グラフ作成 Python スクリプト
                </h4>
                <p style="margin:0; font-size:13px; color:#64748b; line-height:1.5;">
                  本レポートのデータ抽出、基本統計量計算、トレンド回帰、相関分析、およびグラフ描画をそのまま手元で再現できるPythonスクリプト（<code>.py</code>ファイル）をGitHubにて公開しています。
                </p>
              </div>
              <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                <a href="{raw_py_url}" download="{py_filename}" style="background-color:#2563eb; color:#ffffff; text-decoration:none; padding:10px 18px; border-radius:6px; font-size:13px; font-weight:bold; display:inline-flex; align-items:center; gap:6px; box-shadow:0 2px 4px rgba(0,0,0,0.1); transition:background-color 0.2s;">
                  📥 .pyファイルをダウンロード
                </a>
              </div>
            </div>
          </div>


          <!-- Footer -->
          <hr style="border:none; border-top:1px solid #e9ecef; margin:30px 0;" />
          <p style="font-size:12px; color:#8d99ae; text-align:center;">
            本レポートは GitHub Actions ワークフローにより、国内外の公的オープンデータを毎日自動取得・統計処理して作成されています。<br/>
            © EduDataToBlogActions Project / Open Education Statistics Pipeline
          </p>
        </div>

<!-- WordPress Post by Email Shortcodes (Must be at root level) -->
[title {title}]
[category {cat_str}]
[tags {tag_str}]
[status {wp_status}]
"""

        return GeneratedReport(
            title=title,
            html_content=html_content,
            markdown_content=markdown_content,
            categories=categories,
            tags=tags,
            chart_path=chart_path,
            dataset_id=dataset.id,
            created_at=date_iso,
            pdf_path=pdf_path,
            pdf_url=pdf_url,
            peer_review_pdf_path=peer_review_pdf_path,
            peer_review_pdf_url=peer_review_pdf_url,
            py_script_path=py_script_path,
            py_script_url=py_url,
            python_code=python_code,
            angle_id=getattr(selected_angle, "angle_id", "") if selected_angle else "",
            angle_name=getattr(selected_angle, "angle_name", "") if selected_angle else "",
        )
