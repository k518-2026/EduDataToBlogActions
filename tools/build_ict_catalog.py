"""学校の ICT 環境の整備状況（全国・全学校種）の推移から data/catalog/japan_mext_ict_informatization.json を作る。

出典: 文部科学省「令和5年度 学校における教育の情報化の実態等に関する調査結果（概要）【確定値】」（2024-10-31 公表）
      4〜7ページの推移のグラフ（調査基準日は各年3月1日。H31.3.1〜R6.3.1 の6時点）
      data/source/mext/ict_r5_gaiyo.pdf（取得元は data/source/README.md）

PDF のグラフには値が書き込まれている。ページを画像にして目で読み、下の SERIES に転記した。
令和6年3月1日の値は、同じ PDF の8ページ「学校種別」の表の全学校種の列と一致することを検査する（CHECK_R6）。
グラフに値が出ていない時点（調査項目がなかった年）は None（欠測）にしてある。

実行: python -m tools.build_ict_catalog
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "catalog" / "japan_mext_ict_informatization.json"

YEARS = [2019, 2020, 2021, 2022, 2023, 2024]  # 各年の3月1日現在（平成31年・令和2〜6年）

SERIES = {
    "学習者用コンピュータ台数": [1781027, 1911890, 7648983, 11378549, 11763122, 11847856],
    "児童生徒数": [11673644, 11587653, 11452154, 11319053, 11183595, 11033041],
    "児童生徒1人あたり学習者用コンピュータ台数": [0.2, 0.2, 0.7, 1.0, 1.1, 1.1],
    "普通教室の無線LAN整備率": [41.0, 48.9, 78.9, 94.8, 95.7, 96.2],
    "無線LANまたはLTE等で接続できる普通教室の割合": [None, None, 80.3, 96.7, 97.8, 98.3],
    "インターネット接続率（1Gbps以上）": [None, 15.0, 40.0, 59.8, 66.3, 81.0],
    "普通教室の大型提示装置整備率": [52.2, 60.0, 71.6, 83.6, 88.6, 89.6],
    "教員の校務用コンピュータ整備率": [120.5, 122.8, 122.7, 125.4, 126.7, 127.7],
    "教員の指導用コンピュータ整備率": [44.0, 50.7, 78.3, 111.4, 129.0, 133.4],
    "統合型校務支援システム整備率": [57.5, 64.8, 73.5, 81.0, 86.8, 91.4],
    "指導者用デジタル教科書整備率": [52.6, 56.7, 67.4, 81.4, 87.4, 89.6],
    "学習者用デジタル教科書整備率": [None, 7.9, 6.2, 36.1, 87.9, 88.2],
}

# 8ページ「学校種別 学校における主なICT環境の整備状況等」の全学校種の列（令和6年3月1日現在）
CHECK_R6 = {
    "学習者用コンピュータ台数": 11847856,
    "児童生徒数": 11033041,
    "児童生徒1人あたり学習者用コンピュータ台数": 1.1,
    "普通教室の無線LAN整備率": 96.2,
    "無線LANまたはLTE等で接続できる普通教室の割合": 98.3,
    "インターネット接続率（1Gbps以上）": 81.0,
    "普通教室の大型提示装置整備率": 89.6,
    "教員の校務用コンピュータ整備率": 127.7,
    "教員の指導用コンピュータ整備率": 133.4,
    "統合型校務支援システム整備率": 91.4,
    "指導者用デジタル教科書整備率": 89.6,
    "学習者用デジタル教科書整備率": 88.2,
}


def build():
    rows = []
    for i, year in enumerate(YEARS):
        row = {"調査年（3月1日現在）": year}
        for name, values in SERIES.items():
            row[name] = values[i]
        rows.append(row)
    for name, expected in CHECK_R6.items():
        got = SERIES[name][-1]
        if got != expected:
            raise SystemExit(f"令和6年3月1日の値が8ページの表と合わない: {name}: {got} != {expected}")
    for name, values in SERIES.items():
        if len(values) != len(YEARS):
            raise SystemExit(f"{name}: 時点の数が違う")
    # 台数 ÷ 児童生徒数 が、公表されている「1人あたり台数」（小数第1位）に丸めて一致する
    for i in range(len(YEARS)):
        ratio = SERIES["学習者用コンピュータ台数"][i] / SERIES["児童生徒数"][i]
        if round(ratio, 1) != SERIES["児童生徒1人あたり学習者用コンピュータ台数"][i]:
            raise SystemExit(f"{YEARS[i]}: 台数÷児童生徒数={ratio:.3f} が公表の1人あたり台数と合わない")
    return rows


def main():
    rows = build()
    # 台数と児童生徒数は1人あたり台数の元の値で、無線LAN/LTEの列は無線LAN整備率とほぼ同じ内容のため、
    # 分析の指標（metrics）には入れない（データの列には残す）。論文の4ページ制限に収めるためでもある。
    metrics = [m for m in SERIES if m not in ("学習者用コンピュータ台数", "児童生徒数", "無線LANまたはLTE等で接続できる普通教室の割合")]
    doc = {
        "id": "japan_mext_ict_informatization",
        "title": "【教育の情報化調査】学校のICT環境の整備状況の推移（平成31年3月〜令和6年3月，全国）",
        "category": "info",
        "region": "japan",
        "source_name": "文部科学省「学校における教育の情報化の実態等に関する調査」（令和5年度結果【確定値】の概要）",
        "source_url": "https://www.mext.go.jp/a_menu/shotou/zyouhou/detail/mext_00062.html",
        "verification": {
            "status": "verified",
            "checked_on": "2026-10-05",
            "note": "文部科学省『令和5年度 学校における教育の情報化の実態等に関する調査結果（概要）【確定値】』（2024-10-31 公表）の4〜7ページの推移のグラフに書き込まれた値を、PDFを画像にして読み取り転記した（tools/build_ict_catalog.py）。令和6年3月1日の値は同PDF 8ページの学校種別の表（全学校種）と全12指標で一致、学習者用コンピュータ台数÷児童生徒数が公表の1人あたり台数に丸めて一致することを全6時点で検査済み。グラフに値がない時点（調査項目がなかった年）は欠測。",
        },
        "description": "文部科学省の「学校における教育の情報化の実態等に関する調査」（毎年3月1日現在、公立の小・中・高・中等教育・特別支援学校の全国集計）による、学習者用コンピュータ、校内ネットワーク、大型提示装置、教員用コンピュータ、校務支援システム、デジタル教科書の整備状況の推移（平成31年3月〜令和6年3月）。台数と児童生徒数は人・台、他は%（1人あたり台数は台/人）。指標によって調査を始めた年が違うため欠測がある。",
        "unit": "%",
        "time_col": "調査年（3月1日現在）",
        "recommended_chart": "trend_line",
        "metrics": metrics,
        "observation_unit": "調査時点（平成31年・令和2〜6年の各3月1日現在、6時点）の全国集計値（全学校種）",
        "sample_population_note": "公立の小学校・中学校・義務教育学校・高等学校・中等教育学校・特別支援学校（悉皆調査）。令和6年3月1日現在で32,238校、児童生徒数11,033,041人",
        "sample_population_size": "32,238校（令和6年3月1日現在）",
        "data": rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT, len(rows), "rows,", len(metrics), "metrics")


if __name__ == "__main__":
    main()
