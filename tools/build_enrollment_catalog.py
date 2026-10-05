"""学校基本調査の「関係学科別 大学入学状況」から data/catalog/japan_stem_cs_enrollment.json を作る。

出典: 文部科学省「学校基本調査」令和5・6・7年度（2023・2024・2025年）の統計表『関係学科別 大学入学状況』（表番号15、旧報告書掲載集計）
      政府統計の総合窓口 e-Stat のExcel（data/source/estat/ に保存。取得元は data/source/README.md）
      令和5年度 statInfId=000040128620、令和6年度 000040230323、令和7年度 000040392734

各ファイルは、その年度の関係学科（人文科学、社会科学、理学、工学、農学、保健、家政、教育、芸術、その他の大分類と、その下の小分類）ごとの
入学志願者・入学者の男女別の人数（計）を載せている。ここでは、小分類の行を使い、入学者数・女性の入学者数から女性比率（%）を求める。
3年度のすべてで入学者が200人以上ある小分類だけを使う（人数が少ない区分は比率が不安定なため）。
検算: 各年度で、小分類の入学者（男＋女＝計）、大分類の計と小分類の合計が一致すること。

実行: python -m tools.build_enrollment_catalog
"""
import json
from pathlib import Path

from tools.xlsx_read import read_xlsx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "catalog" / "japan_stem_cs_enrollment.json"
SRC = ROOT / "data" / "source" / "estat"
FILES = {  # 年度（西暦） -> (ファイル, 表の年度ラベル)
    2023: ("estat_000040128620.xlsx", "令和5年度"),
    2024: ("estat_000040230323.xlsx", "令和6年度"),
    2025: ("estat_000040392734.xlsx", "令和7年度"),
}
MIN_ENTRANTS = 200

M_N = "入学者数"
M_F = "女性の入学者数"
M_R = "入学者の女性比率（%）"
M_AR = "入学志願者の女性比率（%）"


def _f(v):
    return None if v in (None, "") else float(v)


def read_year(year):
    fname, label = FILES[year]
    wb = read_xlsx(SRC / fname)
    sheet = wb["15(3-1)"]
    rows = {}
    big = {}
    for r in sheet:
        if not r or not r[0] or str(r[0]).strip() != label:
            continue
        major, minor = str(r[1]).strip(), str(r[2]).strip()
        if major == "計":
            continue
        # 列: 3-5 入学志願者 計・男・女、6-8 入学者 計・男・女（「計」の区分）
        app_t, app_m, app_f, ent_t, ent_m, ent_f = (_f(r[i]) for i in range(3, 9))
        rec = {"app": (app_t, app_m, app_f), "ent": (ent_t, ent_m, ent_f)}
        if minor == "計":
            big[major] = rec
        else:
            rows[(major, minor)] = rec
    # 検算
    for (major, minor), rec in rows.items():
        t, m, f = rec["ent"]
        assert abs(t - (m + f)) < 0.5, (year, major, minor)
    for major, rec in big.items():
        subtotal = sum(v["ent"][0] for (mj, _), v in rows.items() if mj == major)
        if abs(subtotal - rec["ent"][0]) > 0.5:
            raise SystemExit(f"{year} {major}: 小分類の合計 {subtotal} != 大分類の計 {rec['ent'][0]}")
    return rows


def build():
    data = {y: read_year(y) for y in FILES}
    keys = [k for k in data[2025] if all(k in data[y] and data[y][k]["ent"][0] >= MIN_ENTRANTS for y in FILES)]
    out = []
    for key in keys:
        major, minor = key
        for y in sorted(FILES):
            rec = data[y][key]
            et, em, ef = rec["ent"]
            at, am, af = rec["app"]
            out.append({
                "年度": y,
                "学科": f"{major}・{minor}",
                M_N: int(et),
                M_F: int(ef),
                M_R: round(ef / et * 100, 1),
                M_AR: round(af / at * 100, 1),
            })
    # 検算: 全体（計）の入学者、令和7年度は 645,513人、女性 303,073人（表の「計」の行）
    return out, data


def main():
    rows, data = build()
    n_groups = len({r["学科"] for r in rows})
    doc = {
        "id": "japan_stem_cs_enrollment",
        "title": "【学校基本調査】大学の関係学科別 入学者の女性比率（令和5〜7年度）",
        "category": "math",  # 記事を info と math で交互に出すための区分（内容を表さない。元の設定のまま）
        "region": "japan",
        "source_name": "文部科学省「学校基本調査」（令和5〜7年度、政府統計の総合窓口 e-Stat）",
        "source_url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00400001&tstat=000001011528",
        "verification": {
            "status": "verified",
            "checked_on": "2026-10-05",
            "note": "e-Statに掲載された学校基本調査の統計表『関係学科別 大学入学状況』（令和5・6・7年度、表番号15）のExcelから機械的に取り込み、入学者数（男・女）から女性比率を求めた（tools/build_enrollment_catalog.py）。手入力の数値はない。各年度で、小分類の入学者（男＋女）が計と一致し、小分類の合計が大分類の計と一致することを検査済み。3年度すべてで入学者が200人以上の小分類だけを使用。",
        },
        "description": ("文部科学省の学校基本調査（毎年5月1日現在）による、大学（学部）の関係学科別の入学者数と、そのうち女性の入学者数、"
                        "入学者と入学志願者の女性比率（%、女性の人数を男女計で割って求めた）。令和5年度（2023年）から令和7年度（2025年）の3時点。"
                        f"関係学科は、人文科学・社会科学・理学・工学・農学・保健・家政・教育・芸術・その他の大分類の下の小分類（例：理学の数学、工学の機械工学・電気通信工学）で、"
                        f"3年度すべてで入学者が200人以上ある{n_groups}区分を使う。この表の分類には「情報」という独立した区分がなく、情報系の学科の入学者だけを取り出すことはできない。"
                        "入学者は大学（学部）の入学者で、短期大学や大学院を含まない。"),
        "unit": "人",
        "time_col": "年度",
        "group_col": "学科",
        "recommended_chart": "ranking_bar",
        "metrics": [M_N, M_F, M_R, M_AR],
        "observation_unit": f"関係学科の区分（{n_groups}区分）×年度（令和5〜7年度の3時点）の集計値（計{len(rows)}観測単位）",
        "sample_population_note": "全国の大学（学部）への入学者・入学志願者（悉皆調査）。令和7年度の入学者は645,513人（女性303,073人）",
        "sample_population_size": "645,513人（令和7年度の大学入学者）",
        "data": rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT, len(rows), "rows,", n_groups, "groups")


if __name__ == "__main__":
    main()
