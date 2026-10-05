"""PISA と TIMSS のカタログ JSON を、公表元の Excel（data/source/）から作る。

    python -m tools.build_pisa_timss_catalog

入力（いずれも data/source/ にある。取得元は data/source/README.md）
  ・PISA 2025 Results (Volume I) の StatLink Excel（OECD、2026-09-08 公開）
      Table I.B1.2a.38  数学の平均得点 2003〜2025（男女計）
      Table I.B1.2c.29/30/31  女子・男子の数学の平均得点と男女差 2015〜2025
  ・TIMSS 2023 International Results の Exhibit（IEA、timss2023.org）
      1.1.10 / 1.2.10  算数・数学の平均得点の推移（小4・中2）
      1.1.11 / 1.2.11  女子・男子の平均得点の推移

手で入力した数値は 1 つもない。値が合わなければ（男子 − 女子 ≠ 男女差など）止まる。
"""
import json
import re
from pathlib import Path

from tools.xlsx_read import read_xlsx

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "source"
OUT = ROOT / "data" / "catalog"

RETRIEVED = "2026-10-05"

PISA_COUNTRIES = [  # (OECD の表の名前, 日本語名)
    ("Japan", "日本"), ("Singapore", "シンガポール"), ("Korea", "韓国"), ("Estonia", "エストニア"),
    ("Canada*", "カナダ"), ("United Kingdom", "イギリス"), ("United States*", "アメリカ"),
    ("OECD average-23", "OECD平均（全回に参加した23か国）"),
]
PISA_YEARS = [2015, 2018, 2022, 2025]


def _num(v):
    return float(v) if isinstance(v, (int, float)) else None


def _find_row(rows, name):
    for r in rows:
        if r and r[0] == name:
            return r
    raise KeyError(name)


def build_pisa():
    total = read_xlsx(SRC / "pisa2025_vol1_table_B1.2a_mrq53f.xlsx")["Table I.B1.2a.38"]
    g = read_xlsx(SRC / "pisa2025_vol1_table_B1.4_68stqn.xlsx")
    girls, boys, diff = g["Table I.B1.2c.29"], g["Table I.B1.2c.30"], g["Table I.B1.2c.31"]

    # 見出しの位置を確かめる（列の順番を決め打ちにしない）
    head = next(r for r in total if r and r[1] == "PISA 2003")
    tcol = {int(re.search(r"\d{4}", str(c)).group(0)): i for i, c in enumerate(head) if c and str(c).startswith("PISA 20") and i <= 15}
    for tbl, label in ((girls, "girls"), (boys, "boys")):
        hdr = next(r for r in tbl if r and any(c and re.fullmatch(r"PISA 2015", str(c).strip()) for c in r))
        cols = {int(str(c).split()[1]): i for i, c in enumerate(hdr) if c and re.fullmatch(r"PISA \d{4}", str(c).strip())}
        assert cols == {2015: 1, 2018: 7, 2022: 13, 2025: 19}, (label, cols)
    gcol = {2015: 1, 2018: 7, 2022: 13, 2025: 19}

    rows = []
    for year in PISA_YEARS:
        for en, ja in PISA_COUNTRIES:
            t = _num(_find_row(total, en)[tcol[year]])
            gi = _num(_find_row(girls, en)[gcol[year]])
            bo = _num(_find_row(boys, en)[gcol[year]])
            df = _num(_find_row(diff, en)[gcol[year]])
            assert None not in (t, gi, bo, df), (en, year)
            assert abs((bo - gi) - df) < 0.01, ("男子−女子が差と合わない", en, year, bo - gi, df)
            assert min(gi, bo) - 1 <= t <= max(gi, bo) + 1, ("男女計が男女の間にない", en, year)
            rows.append({"調査年": year, "国・地域": ja, "数学得点": round(t, 1), "男子得点": round(bo, 1),
                         "女子得点": round(gi, 1), "男女得点差": round(df, 1)})
    head = {
        "id": "oecd_pisa_math_ict",
        "title": "【OECD PISA】主要国の数学的リテラシー得点と男女得点差の国際比較（2015〜2025年）",
        "category": "math", "region": "global", "source_name": "OECD（経済協力開発機構）PISA 2025 Results (Volume I)",
        "source_url": "https://www.oecd.org/en/publications/pisa-2025-results-volume-i_73451bc5-en.html",
        "verification": {"status": "verified", "checked_on": RETRIEVED, "note": (
            "OECD が公表した PISA 2025 Results (Volume I) の Excel（StatLink）から、tools/build_pisa_timss_catalog.py で機械的に作成。"
            "男女計は Table I.B1.2a.38、女子・男子・男女差は Table I.B1.2c.29/30/31。男子−女子が公表の男女差と一致することを全 32 件で確認。"
            "手入力の数値はない。カナダとアメリカは OECD の表で「PISA の標本抽出基準を満たさなかった項目がある」との注意（*）つき。")},
        "description": ("OECD の PISA（15歳の生徒の学習到達度調査）の数学的リテラシーの平均得点（2015・2018・2022・2025年）。"
                        "日本・シンガポール・韓国・エストニア・カナダ・イギリス・アメリカと、2003年から全回に参加した OECD 加盟 23 か国の平均。"
                        "男女別の平均得点と男女得点差（男子−女子）を含む。カナダとアメリカは OECD の表に標本抽出基準についての注意（*）があり、"
                        "特にアメリカは注意が必要とされている。PISA 2025 の主要分野は科学で、数学は副次的な分野。"),
        "unit": "点", "time_col": "調査年", "group_col": "国・地域", "recommended_chart": "trend_line",
        "metrics": ["数学得点", "男子得点", "女子得点", "男女得点差"],
        "observation_unit": "国・地域（7か国と OECD 23か国平均）× 調査年（2015・2018・2022・2025年の4時点）の平均得点（計32観測単位）",
        "sample_population_note": "各国の15歳の生徒（学校に在籍する者）の標本調査。1回あたり1か国数千〜数万人",
        "sample_population_size": "各回 約60〜80の国・地域、約60万〜69万人（OECD の公表による概数）",
    }
    return head, rows


def _timss_year_rows(path):
    """trend-table: 国名の行のあとに 年・平均・標準誤差 の行が続く。{国名: {年: (平均, SE)}}"""
    sheet = next(iter(read_xlsx(path).values()))
    out, cur = {}, None
    for r in sheet:
        if len(r) < 6:
            continue
        label = r[2]
        if isinstance(label, str) and r[4] is None:
            cur = label.strip()
            out[cur] = {}
        elif isinstance(label, float) and cur:
            out[cur][int(label)] = (_num(r[4]), _num(r[5]))
    return out


def _timss_gender_rows(path):
    """trend-gender: {国名: {年: (女子, 男子)}}。見出しの年の位置から読む"""
    sheet = next(iter(read_xlsx(path).values()))
    hdr = next(r for r in sheet if len(r) > 2 and r[2] == "Country")
    ycols = [(i, int(c)) for i, c in enumerate(hdr) if isinstance(c, str) and re.fullmatch(r"\d{4}", c.strip())]
    sub = next(r for r in sheet if len(r) > 5 and r[4] == "Girls")
    out = {}
    for r in sheet:
        if len(r) > 5 and isinstance(r[2], str) and r[2] not in ("Country",) and r is not hdr and r is not sub:
            vals = {}
            for i, y in ycols:
                gi, bo = (r[i] if i < len(r) else None), (r[i + 2] if i + 2 < len(r) else None)
                if isinstance(gi, float) and isinstance(bo, float):
                    vals[y] = (gi, bo)
            if vals:
                out[r[2].strip()] = vals
    return out


def build_timss():
    rows = []
    for grade, label, tpath, gpath in (
        (4, "小学校4年_算数", "1-1-10_ach-g4m-trend-table.xlsx", "1-1-11_ach-g4m-trend-gender.xlsx"),
        (8, "中学校2年_数学", "1-2-10_ach-g8m-trend-table.xlsx", "1-2-11_ach-g8m-trend-gender.xlsx"),
    ):
        tr = _timss_year_rows(SRC / tpath)["Japan"]
        ge = _timss_gender_rows(SRC / gpath)["Japan"]
        for year in sorted(tr):
            avg, _se = tr[year]
            if year not in ge:
                continue
            gi, bo = ge[year]
            # 女子・男子の平均（整数で公表）の中間に男女計が来る
            assert min(gi, bo) - 1.5 <= avg <= max(gi, bo) + 1.5, ("男女計が男女の間にない", grade, year, avg, gi, bo)
            rows.append({"調査年": year, "学年・教科": label, "平均得点": int(avg), "男子平均得点": int(bo),
                         "女子平均得点": int(gi), "男女得点差": int(bo - gi)})
    head = {
        "id": "japan_timss_math_science",
        "title": "【TIMSS】日本の小学校4年算数・中学校2年数学の平均得点と男女差の推移（1995〜2023年）",
        "category": "math", "region": "japan",
        "source_name": "IEA（国際教育到達度評価学会）TIMSS 2023 International Results in Mathematics and Science",
        "source_url": "https://timss2023.org/results/math-achievement/",
        "verification": {"status": "verified", "checked_on": RETRIEVED, "note": (
            "IEA の TIMSS 2023 International Results の Exhibit 1.1.10/1.1.11（小4）と 1.2.10/1.2.11（中2）の Excel から、"
            "tools/build_pisa_timss_catalog.py で機械的に作成。男女計の平均が女子・男子の平均の間にあることを全件で確認。手入力の数値はない。"
            "以前の「勉強が楽しい・得意・将来役立つ」の肯定率は、出典の経年表がなく確認できなかったため含めない。")},
        "description": ("TIMSS（国際数学・理科教育動向調査）で、日本の小学校4年生の算数と中学校2年生の数学の平均得点（1995〜2023年）と、"
                        "女子・男子別の平均得点。得点は公表値（整数）。1999年（中2）は男女別の公表がないため含めない。年は調査実施年（小4は1995・2003・2007・2011・2015・2019・2023年、"
                        "中2は1995・2003・2007・2011・2015・2019・2023年）。男女得点差は男子−女子。"),
        "unit": "点", "time_col": "調査年", "group_col": "学年・教科", "recommended_chart": "trend_line",
        "metrics": ["平均得点", "男子平均得点", "女子平均得点", "男女得点差"],
        "observation_unit": "学年・教科（小学校4年算数・中学校2年数学）× 調査年（小4・中2とも7時点）の平均得点（計14観測単位）",
        "sample_population_note": "日本の公立・私立の小学校4年生・中学校2年生の標本調査（学校を抽出し学級単位で調査）。各回 約4,000〜5,000人",
        "sample_population_size": "各学年 約4,000〜5,000人（回により異なる）",
    }
    return head, rows


def dump(path, head, rows):
    lines = ["{"]
    for k, v in head.items():
        lines.append(f'  {json.dumps(k, ensure_ascii=False)}: ' + json.dumps(v, ensure_ascii=False, indent=2).replace("\n", "\n  ") + ",")
    lines.append('  "data": [')
    lines.append(",\n".join("    " + json.dumps(r, ensure_ascii=False) for r in rows))
    lines.append("  ]")
    lines.append("}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    for build, name in ((build_pisa, "oecd_pisa_math_ict"), (build_timss, "japan_timss_math_science")):
        head, rows = build()
        dump(OUT / f"{name}.json", head, rows)
        print(f"{name}: {len(rows)} 行")


if __name__ == "__main__":
    main()
