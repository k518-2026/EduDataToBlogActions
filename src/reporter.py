"""
Report Generator for Educational Data Analysis.
Combines statistical tables, visualization charts, pedagogical insights, and
reproducible Python analysis code (with interactive copy button) into
polished HTML (with Base64 embedded charts for WordPress) and Markdown.
"""
import base64
from dataclasses import dataclass
from datetime import datetime
import html
import json
import logging
from pathlib import Path
from typing import List, Optional

from src.analyzer import AnalysisResult
from src.config import Config
from src.fetchers.base import EducationDataset
from src.insights import EducationalInsights

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


class EduReportBuilder:
    """Constructs HTML and Markdown reports from analysis results."""

    def _generate_python_analysis_code(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> str:
        """Generates clean, fully self-contained reproducible Python code for the dataset analysis."""
        records = dataset.df.to_dict(orient="records")
        data_json = json.dumps(records, ensure_ascii=False, indent=2)

        # Plotting snippet tailored to recommended_chart
        if dataset.recommended_chart == "ranking_bar" and dataset.group_col:
            plot_snippet = f"""# グループ別（国・地域等）の平均値横棒グラフ
metric = "{dataset.metrics[0]}"
ranked = df.groupby("{dataset.group_col}")[metric].mean().sort_values(ascending=True)
bars = plt.barh(ranked.index, ranked.values, color="#457b9d", height=0.65)
for bar in bars:
    w = bar.get_width()
    plt.text(w + 0.3, bar.get_y() + bar.get_height() / 2, f"{{w:.1f}}{dataset.unit}", va="center", fontweight="bold", fontsize=9)
plt.xlabel(f"{{metric}} ({dataset.unit})", fontsize=11)"""
        elif dataset.recommended_chart == "correlation_scatter" and len(dataset.metrics) >= 2:
            plot_snippet = f"""# 相関散布図 & 回帰トレンドライン
col_x, col_y = "{dataset.metrics[1]}", "{dataset.metrics[0]}"
sns.regplot(x=col_x, y=col_y, data=df, color="#2a9d8f", line_kws={{"color": "#e76f51", "linewidth": 2}})
plt.xlabel(col_x, fontsize=11)
plt.ylabel(f"{{col_y}} ({dataset.unit})", fontsize=11)"""
        else:
            time_col = dataset.time_col or "年度"
            group_col = dataset.group_col
            if group_col and group_col in dataset.df.columns:
                plot_snippet = f"""# 経年変化トレンド折れ線グラフ（グループ別）
time_col = "{time_col}"
metric = "{dataset.metrics[0]}"
for grp in df["{group_col}"].unique():
    sub = df[df["{group_col}"] == grp].sort_values(by=time_col)
    plt.plot(sub[time_col], sub[metric], marker="o", linewidth=2.5, markersize=6, label=str(grp))
plt.xlabel(f"{{time_col}} (年/年度)", fontsize=11)
plt.ylabel(f"{{metric}} ({dataset.unit})", fontsize=11)
plt.legend(frameon=True, facecolor="white")"""
            else:
                plot_snippet = f"""# 経年変化トレンド折れ線グラフ（主要指標）
time_col = "{time_col}"
sub = df.sort_values(by=time_col)
for m in {dataset.metrics}:
    if m in sub.columns:
        plt.plot(sub[time_col], sub[m], marker="s", linewidth=2.5, markersize=6, label=m)
plt.xlabel(f"{{time_col}} (年/年度)", fontsize=11)
plt.ylabel(f"値 ({dataset.unit})", fontsize=11)
plt.legend(frameon=True, facecolor="white")"""

        code = f'''"""
{dataset.title}
オープンデータ統計分析・可視化再現スクリプト
データ提供元: {dataset.source_name} ({dataset.source_url})
"""
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

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
# 3. 経年変化トレンド・線形回帰分析 (決定係数 R²)
# ==============================================================================
time_col = "{dataset.time_col or ''}"
if time_col and time_col in df.columns:
    print("\\n==================================================")
    print("📈 経年トレンド線形回帰分析")
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
                start_v, end_v = y_vals.iloc[0], y_vals.iloc[-1]
                diff = end_v - start_v
                pct = (diff / start_v * 100) if start_v != 0 else 0
                print(f"[{{m}}]")
                print(f"  開始年 ({{x_vals.iloc[0]}}) -> 最新年 ({{x_vals.iloc[-1]}}): {{start_v:.2f}} -> {{end_v:.2f}}")
                print(f"  変化量: {{diff:+.2f}} {dataset.unit} (変化率: {{pct:+.1f}}%)")
                print(f"  回帰の傾き: {{res.slope:.3f}} / 決定係数 (R²): {{r_sq:.3f}} / p値: {{res.pvalue:.4f}}")

# ==============================================================================
# 4. 相関分析 (ピアソン相関係数 r)
# ==============================================================================
if len(metrics) >= 2:
    print("\\n==================================================")
    print("🔍 指標間の相関分析")
    print("==================================================")
    for i in range(len(metrics)):
        for j in range(i + 1, len(metrics)):
            col_x, col_y = metrics[i], metrics[j]
            if col_x in df.columns and col_y in df.columns:
                sub = df[[col_x, col_y]].dropna()
                if len(sub) >= 3:
                    r, p = stats.pearsonr(sub[col_x], sub[col_y])
                    print(f"{{col_x}} × {{col_y}}: 相関係数 r = {{r:.3f}}, p値 = {{p:.4f}}")

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

    def build_report(
        self,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        insights: EducationalInsights,
        chart_path: Path,
    ) -> GeneratedReport:
        today_str = datetime.now().strftime("%Y年%m月%d日")
        date_iso = datetime.now().strftime("%Y-%m-%d")

        category_label = "算数・数学教育" if dataset.category == "math" else "情報教育・プログラミング"
        title = f"【教育オープンデータ統計分析】{dataset.title} ({today_str})"

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
        escaped_python_code = html.escape(python_code)

        # 1. Build Markdown Table for Descriptive Stats
        desc_table_rows_md = [
            "| 指標名 | データ数 | 平均値 | 中央値 | 標準偏差 | 最小値 | 最大値 | 四分位範囲 (IQR) |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]
        desc_table_rows_html = []
        for m, s in analysis.descriptive_stats.items():
            desc_table_rows_md.append(
                f"| **{m}** | {s.count} | {s.mean}{dataset.unit} | {s.median}{dataset.unit} | "
                f"{s.std} | {s.min_val} | {s.max_val} | {s.iqr} |"
            )
            desc_table_rows_html.append(
                f"<tr><td><b>{m}</b></td><td style='text-align:center;'>{s.count}</td>"
                f"<td style='text-align:right;'>{s.mean}{dataset.unit}</td>"
                f"<td style='text-align:right;'>{s.median}{dataset.unit}</td>"
                f"<td style='text-align:right;'>{s.std}</td>"
                f"<td style='text-align:right;'>{s.min_val}</td>"
                f"<td style='text-align:right;'>{s.max_val}</td>"
                f"<td style='text-align:right;'>{s.iqr}</td></tr>"
            )

        # 2. Build Markdown Table for Trends (if available)
        trend_table_md = ""
        trend_table_html = ""
        if analysis.trends:
            trend_rows_md = [
                "| 指標 / グループ | 調査開始 | 初期値 | 調査最新 | 最新値 | 変化量 | 変化率 | 年平均成長率 (CAGR) | 決定係数 (R²) |",
                "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
            ]
            trend_rows_html = []
            for tr in analysis.trends:
                grp_str = f"[{tr.group_name}] " if tr.group_name else ""
                cagr_str = f"{tr.cagr:+.2f}%" if tr.cagr is not None else "-"
                trend_rows_md.append(
                    f"| {grp_str}{tr.metric} | {tr.start_time} | {tr.start_val}{dataset.unit} | "
                    f"{tr.end_time} | {tr.end_val}{dataset.unit} | {tr.diff:+.1f} | {tr.pct_change:+.1f}% | "
                    f"{cagr_str} | {tr.r_squared} |"
                )
                trend_rows_html.append(
                    f"<tr><td>{grp_str}<b>{tr.metric}</b></td>"
                    f"<td style='text-align:center;'>{tr.start_time}</td>"
                    f"<td style='text-align:right;'>{tr.start_val}{dataset.unit}</td>"
                    f"<td style='text-align:center;'>{tr.end_time}</td>"
                    f"<td style='text-align:right;'>{tr.end_val}{dataset.unit}</td>"
                    f"<td style='text-align:right; font-weight:bold; color:{'#2a9d8f' if tr.diff>=0 else '#e76f51'};'>{tr.diff:+.1f}</td>"
                    f"<td style='text-align:right;'>{tr.pct_change:+.1f}%</td>"
                    f"<td style='text-align:right;'>{cagr_str}</td>"
                    f"<td style='text-align:right;'>{tr.r_squared}</td></tr>"
                )
            trend_table_md = "### 経年変化・トレンド推移\n\n" + "\n".join(trend_rows_md) + "\n"
            trend_table_html = f"""
            <h3 style="color:#1d3557; border-bottom:2px solid #457b9d; padding-bottom:5px; margin-top:25px;">📈 経年変化・トレンド分析表</h3>
            <div style="overflow-x:auto;">
              <table style="width:100%; border-collapse:collapse; margin-bottom:20px; font-size:14px;">
                <thead>
                  <tr style="background-color:#f1faee; color:#1d3557; border-bottom:2px solid #a8dadc;">
                    <th style="padding:8px; text-align:left;">指標 / グループ</th>
                    <th style="padding:8px; text-align:center;">開始年</th>
                    <th style="padding:8px; text-align:right;">初期値</th>
                    <th style="padding:8px; text-align:center;">最新年</th>
                    <th style="padding:8px; text-align:right;">最新値</th>
                    <th style="padding:8px; text-align:right;">変化量</th>
                    <th style="padding:8px; text-align:right;">変化率</th>
                    <th style="padding:8px; text-align:right;">CAGR</th>
                    <th style="padding:8px; text-align:right;">R²</th>
                  </tr>
                </thead>
                <tbody>
                  {''.join(trend_rows_html)}
                </tbody>
              </table>
            </div>
            """

        # 3. Assemble Markdown Content (Includes raw URL chart and full Python script)
        insights_bullets_md = "\n".join([f"- {ins}" for ins in analysis.key_insights])

        markdown_content = f"""# {title}

**更新日:** {today_str} | **カテゴリ:** {category_label} | **データ対象地域:** {dataset.region.upper()}

---

## 📌 本日の分析要約（エグゼクティブサマリー）

{insights.executive_summary}

---

## 📊 オープンデータ概要・出典情報

- **データセット名:** {dataset.title}
- **情報提供元:** [{dataset.source_name}]({dataset.source_url})
- **調査対象・内容:** {dataset.description}
- **分析標本数 (行数):** {analysis.sample_size} 件

---

## 📈 統計分析データテーブル

### 主要指標の記述統計量
{chr(10).join(desc_table_rows_md)}

{trend_table_md}
### 統計から導出された主要ハイライト
{insights_bullets_md}

---

## 🖼️ データ可視化グラフ

![{dataset.title}のグラフ画像]({raw_github_img_url})

---

## 💡 教育現場・授業実践への具体的示唆

{insights.pedagogical_implications}

---

## 🚀 今後の課題と政策・国際的展望

{insights.future_challenges_and_policy}

---

## 💻 統計処理に利用した Python コード

以下のPythonコードで、本レポートの記述統計、回帰分析、相関分析、およびグラフ描画をローカル環境（Jupyter Notebook / Google Colab等）でそのまま再現できます。

```python
{python_code}
```

---
*Generated automatically by EduDataToBlogActions pipeline.*
"""

        # 4. Assemble HTML Content (With Base64 image, reproducible Python code box, and interactive Copy Button)
        wp_status = Config.WP_POST_STATUS or "publish"
        cat_str = ",".join(categories)
        tag_str = ",".join(tags)

        pedagogy_html = insights.pedagogical_implications.replace("\n", "<br/>")
        policy_html = insights.future_challenges_and_policy.replace("\n", "<br/>")
        summary_html = insights.executive_summary.replace("\n", "<br/>")
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
          <div style="background-color:#f8f9fa; border-left:5px solid #e63946; padding:18px 20px; border-radius:4px; margin-bottom:28px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <h3 style="margin-top:0; color:#1d3557; font-size:16px;">📌 本日の分析要約（エグゼクティブサマリー）</h3>
            <p style="margin-bottom:0; font-size:15px; line-height:1.7;">{summary_html}</p>
          </div>

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
          <h3 style="color:#1d3557; border-bottom:2px solid #457b9d; padding-bottom:5px; margin-top:30px;">📊 統計分析結果（記述統計量）</h3>
          <div style="overflow-x:auto;">
            <table style="width:100%; border-collapse:collapse; margin-bottom:20px; font-size:14px;">
              <thead>
                <tr style="background-color:#f1faee; color:#1d3557; border-bottom:2px solid #a8dadc;">
                  <th style="padding:8px; text-align:left;">指標名</th>
                  <th style="padding:8px; text-align:center;">標本数</th>
                  <th style="padding:8px; text-align:right;">平均値</th>
                  <th style="padding:8px; text-align:right;">中央値</th>
                  <th style="padding:8px; text-align:right;">標準偏差</th>
                  <th style="padding:8px; text-align:right;">最小</th>
                  <th style="padding:8px; text-align:right;">最大</th>
                  <th style="padding:8px; text-align:right;">IQR</th>
                </tr>
              </thead>
              <tbody>
                {''.join(desc_table_rows_html)}
              </tbody>
            </table>
          </div>

          {trend_table_html}

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

          <!-- Python Analysis Code Section with Copy Button -->
          <div style="margin-top:35px; margin-bottom:30px;">
            <h3 style="color:#1d3557; border-bottom:2px solid #457b9d; padding-bottom:5px;">💻 統計処理に利用した Python コード</h3>
            <p style="font-size:13px; color:#495057; margin-bottom:12px;">
              本レポートのデータ読み込み、基本統計量の計算、トレンド線形回帰、相関分析、およびグラフ可視化を再現できる完全なPythonスクリプトです。右上のボタンからワンクリックでコピーできます。
            </p>
            <div style="position:relative; border-radius:8px; overflow:hidden; box-shadow:0 3px 10px rgba(0,0,0,0.12); border:1px solid #334155;">
              <div style="display:flex; justify-content:space-between; align-items:center; background-color:#1e293b; color:#cbd5e1; padding:10px 16px; font-size:13px; font-family:Consolas, Monaco, monospace;">
                <span style="font-weight:bold;">🐍 Python 3 (pandas / scipy / matplotlib)</span>
                <button type="button" onclick="copyEduDataPythonCode()" id="copy-code-btn" style="background-color:#2563eb; color:#ffffff; border:none; padding:6px 14px; border-radius:4px; font-size:12px; font-weight:bold; cursor:pointer; display:inline-flex; align-items:center; gap:5px; transition:background-color 0.2s;">
                  📋 コードをコピー
                </button>
              </div>
              <pre id="edu-data-code-block" style="margin:0; padding:18px; background-color:#0f172a; color:#f8fafc; font-size:13px; line-height:1.55; overflow-x:auto; font-family:Consolas, Monaco, 'Courier New', monospace; max-height:450px;"><code>{escaped_python_code}</code></pre>
            </div>
          </div>

          <!-- Copy Button Interactive Script -->
          <script>
          function copyEduDataPythonCode() {{
            var codeEl = document.getElementById('edu-data-code-block');
            if (!codeEl) return;
            var text = codeEl.innerText || codeEl.textContent;
            var btn = document.getElementById('copy-code-btn');
            
            function onCopiedSuccess() {{
              if (btn) {{
                btn.innerText = '✅ コピー完了！';
                btn.style.backgroundColor = '#16a34a';
                setTimeout(function() {{
                  btn.innerText = '📋 コードをコピー';
                  btn.style.backgroundColor = '#2563eb';
                }}, 2500);
              }}
            }}

            if (navigator.clipboard && window.isSecureContext) {{
              navigator.clipboard.writeText(text).then(onCopiedSuccess).catch(function() {{
                fallbackClipboardCopy(text, onCopiedSuccess);
              }});
            }} else {{
              fallbackClipboardCopy(text, onCopiedSuccess);
            }}

            function fallbackClipboardCopy(str, callback) {{
              var ta = document.createElement('textarea');
              ta.value = str;
              ta.style.position = 'fixed';
              ta.style.left = '-9999px';
              document.body.appendChild(ta);
              ta.focus();
              ta.select();
              try {{
                var successful = document.execCommand('copy');
                if (successful) callback();
              }} catch (err) {{
                console.error('Copy failed:', err);
              }}
              document.body.removeChild(ta);
            }}
          }}
          </script>

          <!-- Footer -->
          <hr style="border:none; border-top:1px solid #e9ecef; margin:30px 0;" />
          <p style="font-size:12px; color:#8d99ae; text-align:center;">
            本レポートは GitHub Actions ワークフローにより、国内外の公的オープンデータを毎日自動取得・統計処理して作成されています。<br/>
            © EduDataToBlogActions Project / Open Education Statistics Pipeline
          </p>
        </div>

<!-- WordPress Post by Email Shortcodes (Must be at root level) -->
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
        )
