"""通級による指導を受けている児童生徒数の推移から data/catalog/japan_special_needs_education.json を作る。

出典: 文部科学省「令和4年度通級による指導実施状況調査結果」（2024-11-07 公表）4ページの表
      『通級による指導を受けている児童生徒数の推移【学校種別・国公私立計】』
      data/source/mext/tokkyu_r4.pdf（取得元は data/source/README.md）

表の数値は PDF のテキスト層から取り出し、ページを画像にして表の行の見出し（小学校・中学校・高等学校・計）と突き合わせた。
検査: 小学校＋中学校＋高等学校＝計（全22時点）、令和4年度の計198,343人と前年度比＋14,464人（同ページの本文）。
高等学校は平成30年度から値がある（それ以前は「—」）。

実行: python -m tools.build_tokkyu_catalog
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "catalog" / "japan_special_needs_education.json"

# 年度（西暦。4月に始まる年度）: 平成5・10・15〜30年度、令和元〜4年度
YEARS = [1993, 1998, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017,
         2018, 2019, 2020, 2021, 2022]
ELEMENTARY = [11963, 23629, 32722, 34717, 37134, 39764, 43078, 46956, 50569, 56254, 60164, 65456, 70924, 75364,
              80768, 87928, 96996, 108306, 116633, 140255, 154559, 164735]
JUNIOR_HIGH = [296, 713, 930, 1040, 1604, 1684, 2162, 2729, 3452, 4383, 5196, 6063, 6958, 8386, 9337, 10383, 11950,
               14281, 16765, 23142, 27649, 31553]
HIGH = [None] * 17 + [508, 787, 1300, 1671, 2055]
TOTAL = [12259, 24342, 33652, 35757, 38738, 41448, 45240, 49685, 54021, 60637, 65360, 71519, 77882, 83750, 90105,
         98311, 108946, 123095, 134185, 164697, 183879, 198343]

M_E = "小学校の通級指導児童生徒数"
M_J = "中学校の通級指導児童生徒数"
M_H = "高等学校の通級指導児童生徒数"
M_T = "全体の通級指導児童生徒数（総数）"


def build():
    n = len(YEARS)
    assert all(len(a) == n for a in (ELEMENTARY, JUNIOR_HIGH, HIGH, TOTAL))
    for i in range(n):
        if ELEMENTARY[i] + JUNIOR_HIGH[i] + (HIGH[i] or 0) != TOTAL[i]:
            raise SystemExit(f"{YEARS[i]}: 小{ELEMENTARY[i]}+中{JUNIOR_HIGH[i]}+高{HIGH[i]} != 計{TOTAL[i]}")
    if TOTAL[-1] != 198343 or TOTAL[-1] - TOTAL[-2] != 14464:
        raise SystemExit("令和4年度の計または前年度比が本文（198,343人、+14,464人）と合わない")
    rows = []
    for i, y in enumerate(YEARS):
        rows.append({"年度": y, M_E: ELEMENTARY[i], M_J: JUNIOR_HIGH[i], M_H: HIGH[i], M_T: TOTAL[i]})
    return rows


def main():
    rows = build()
    doc = {
        "id": "japan_special_needs_education",
        "title": "【特別支援教育】通級による指導を受けている児童生徒数の推移（平成5〜令和4年度，学校種別）",
        "category": "info",
        "region": "japan",
        "source_name": "文部科学省「令和4年度通級による指導実施状況調査結果」",
        "source_url": "https://www.mext.go.jp/a_menu/shotou/tokubetu/1402845_00010.htm",
        "verification": {
            "status": "verified",
            "checked_on": "2026-10-05",
            "note": "文部科学省『令和4年度通級による指導実施状況調査結果』（2024-11-07 公表）4ページの表をPDFのテキスト層から取り、画像で行の見出しと突き合わせた（tools/build_tokkyu_catalog.py）。小学校＋中学校＋高等学校＝計を全22時点で検査、令和4年度の計198,343人・前年度比＋14,464人も本文と一致。高等学校は平成30年度から値がある。",
        },
        "description": "文部科学省の通級による指導実施状況調査による、通級による指導を受けている児童生徒の人数（国公私立計、各年度5月1日現在）。平成5年度、10年度、15〜30年度、令和元〜4年度（22時点、間隔は不均一）。小学校・中学校・高等学校別と総数。高等学校の値は平成30年度から。令和6年の能登半島沖地震の影響で、令和4年度の調査では石川県の公立・私立学校に調査を実施していない。通級による指導は、通常の学級に在籍しながら、障害に応じた特別の指導を受ける制度。",
        "unit": "人",
        "time_col": "年度",
        "recommended_chart": "trend_line",
        "metrics": [M_E, M_J, M_H, M_T],
        "observation_unit": "年度（平成5・10・15〜30年度、令和元〜4年度の22時点）の全国集計値（国公私立計）",
        "sample_population_note": "通級による指導を受けている小学校・中学校・高等学校の児童生徒（全国、悉皆調査）。令和4年度は石川県の公立・私立学校を除く",
        "sample_population_size": "198,343人（令和4年度）",
        "data": rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT, len(rows), "rows")


if __name__ == "__main__":
    main()
