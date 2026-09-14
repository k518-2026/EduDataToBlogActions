"""
Report Generator for Educational Data Analysis.
Combines statistical tables, visualization charts, and pedagogical insights into
polished HTML (with Base64 embedded charts for WordPress) and Markdown.
"""
import base64
from dataclasses import dataclass
from datetime import datetime
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

        # 3. Assemble Markdown Content (Uses GitHub raw URL so it displays properly in GitHub Step Summary)
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
*Generated automatically by EduDataToBlogActions pipeline.*
"""

        # 4. Assemble HTML Content (Uses Base64 image + direct shortcodes at bottom for WordPress)
        wp_status = Config.WP_POST_STATUS or "publish"
        cat_str = ",".join(categories)
        tag_str = ",".join(tags)

        pedagogy_html = insights.pedagogical_implications.replace("\n", "<br/>")
        policy_html = insights.future_challenges_and_policy.replace("\n", "<br/>")
        summary_html = insights.executive_summary.replace("\n", "<br/>")
        insights_bullets_html = "".join(
            [f"<li style='margin-bottom:6px;'>{ins}</li>" for ins in analysis.key_insights]
        )

        # Base64 image tag for web rendering in WordPress
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
