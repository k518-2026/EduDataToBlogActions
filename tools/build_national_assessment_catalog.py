"""全国学力・学習状況調査の平均正答率（全国・公立の小6・中3）から data/catalog/japan_national_assessment_math.json を作る。

出典: 国立教育政策研究所・文部科学省「全国学力・学習状況調査の結果（概要）」の令和元・3・4・5・6・7年度版
      （data/source/mext/nat_assess_*.pdf。取得元は data/source/README.md）
      各年度の概要の冒頭の表に、教科ごとの全国（公立）の平均正答数と平均正答率が載っている。PDF のテキスト層から数値を取り、
      令和7年度は画像でも確認した。
令和2年度（2020年）は新型コロナの影響で調査が実施されなかった。令和元年度以前は平成19年度から実施している（ここでは使わない）。

検算: ある年度の値は、翌年度（または翌々年度）の概要にも「前年度」の行として載っている。
      令和元年度 → 令和3年度の概要、令和3年度 → 令和4年度の概要、令和4年度 → 令和5年度の概要、令和5年度 → 令和6年度の概要で、
      同じ値が載っていることを確かめた。

実行: python -m tools.build_national_assessment_catalog
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "catalog" / "japan_national_assessment_math.json"

M_EJ = "小学校国語の平均正答率"
M_EM = "小学校算数の平均正答率"
M_JJ = "中学校国語の平均正答率"
M_JM = "中学校数学の平均正答率"

# 年度（西暦）: (小国語, 小算数, 中国語, 中数学) 全国（公立）の平均正答率（%）
SERIES = {
    2019: (64.0, 66.7, 73.2, 60.3),
    2021: (64.9, 70.3, 64.9, 57.5),
    2022: (65.8, 63.3, 69.3, 52.0),
    2023: (67.4, 62.7, 70.1, 51.4),
    2024: (67.8, 63.6, 58.4, 53.0),
    2025: (67.0, 58.2, 54.6, 48.8),
}
# 平均正答数/出題数（令和4・5・6・7年度の概要の表）。正答率との整合を検査する
SCORES = {
    2022: ((9.2, 14), (10.1, 16), (9.7, 14), (7.3, 14)),
    2023: ((9.4, 14), (10.0, 16), (10.5, 15), (7.7, 15)),
    2024: ((9.5, 14), (10.2, 16), (8.8, 15), (8.5, 16)),
    2025: ((9.4, 14), (9.3, 16), (7.6, 14), (7.3, 15)),
}


def build():
    for year, vals in SERIES.items():
        for v in vals:
            assert 0 < v < 100
    # 正答数/出題数 から求めた率と、公表の正答率が 0.5 ポイント以内で合う（正答数は小数第1位に丸めて公表されるため）
    for year, items in SCORES.items():
        for (got, n), pct in zip(items, SERIES[year]):
            calc = got / n * 100
            if abs(calc - pct) > 1.0:
                raise SystemExit(f"{year}: 正答数{got}/{n}={calc:.1f}% と公表の正答率{pct}% が合わない")
    return [{"年度": y, M_EJ: v[0], M_EM: v[1], M_JJ: v[2], M_JM: v[3]} for y, v in sorted(SERIES.items())]


def main():
    rows = build()
    doc = {
        "id": "japan_national_assessment_math",
        "title": "【全国学力・学習状況調査】小学校6年・中学校3年の国語と算数・数学の平均正答率の推移（令和元〜7年度）",
        "category": "math",
        "region": "japan",
        "source_name": "国立教育政策研究所・文部科学省「全国学力・学習状況調査の結果（概要）」",
        "source_url": "https://www.nier.go.jp/kaihatsu/zenkokugakuryoku.html",
        "verification": {
            "status": "verified",
            "checked_on": "2026-10-05",
            "note": "国立教育政策研究所・文部科学省の『全国学力・学習状況調査の結果（概要）』令和元・3・4・5・6・7年度版の冒頭の表（全国・公立の教科別平均正答率）から転記した（tools/build_national_assessment_catalog.py）。各値は翌年度または翌々年度の概要にも前年度の行として載っており一致することを確認。令和4〜7年度は平均正答数÷出題数が公表の正答率と1ポイント以内で合うことを検査済み。令和2年度は調査が実施されていない。",
        },
        "description": ("全国学力・学習状況調査（毎年4月、小学校6年生と中学校3年生）の、全国（公立）の教科別の平均正答率（%）。"
                        "国語と算数（小学校）・数学（中学校）の令和元年度（2019年）から令和7年度（2025年）まで。令和2年度（2020年）は新型コロナの影響で実施されなかった。"
                        "出題される問題は毎年異なるため、年度間の平均正答率の高低は、学力の変化を直接示さない（文部科学省・国立教育政策研究所は、年度間の変化を調べるため、"
                        "別に経年変化分析調査を実施している）。出題数は年度により異なる（令和7年度は小学校の国語14問・算数16問、中学校の国語14問・数学15問）。"),
        "unit": "%",
        "time_col": "年度",
        "recommended_chart": "trend_line",
        "metrics": [M_EM, M_JM, M_EJ, M_JJ],
        "observation_unit": "年度（令和元・3〜7年度の6時点）の全国（公立）の集計値",
        "sample_population_note": "全国の小学校6年生と中学校3年生（国公私立の悉皆に近い調査）。ここに載せた平均正答率は全国（公立）の値。令和7年度は小学校の調査対象児童約101万人、中学校約106万人",
        "sample_population_size": "小学校6年生 約101万人・中学校3年生 約106万人（令和7年度の調査対象）",
        "data": rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT, len(rows), "rows")


if __name__ == "__main__":
    main()
