"""TIMSS 2023 の、算数・数学に対する意識（好き・自信・価値）の国別データから
data/catalog/timss2023_student_attitudes.json を作る。

出典: IEA『TIMSS 2023 International Results in Mathematics and Science』の Exhibit
      6.2.2 / 6.2.3（Students Like Learning Mathematics、小4・中2）
      6.2.5 / 6.2.6（Students Confident in Mathematics、小4・中2）
      6.2.8（Students Value Mathematics、中2のみ）
      1.1.1 / 1.2.1（数学の平均得点、小4・中2）
      data/source/timss2023_*.xlsx（取得元は data/source/README.md）

各 Exhibit は、国ごとに「とても肯定」「やや肯定」「肯定しない」の 3 群の児童生徒の割合と、群ごとの平均得点を載せる。
ここでは「とても肯定」と「肯定しない」の割合、2 群の平均得点の差（とても肯定−肯定しない、得点の差は公表値の引き算）、
国の平均得点を使う。国際平均の行とベンチマーク参加（州・首長国）の行は除く。
検算: とても肯定＋やや肯定＋肯定しない が 100±2.5（四捨五入のため）。国際平均（小4の「好き」は 44%・32%・24%）の行も同じ表にある。

実行: python -m tools.build_timss_attitudes_catalog
"""
import json
import re
from pathlib import Path

from tools.xlsx_read import read_xlsx

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "source"
OUT = ROOT / "data" / "catalog" / "timss2023_student_attitudes.json"

# (指標名の元になる語, ファイル, G4 のシート, G8 のシート)
SCALES = {
    "好き": ("timss2023_6-2-1-3_con-stu-slm.xlsx", "6.2.2 G4 MAT", "6.2.3 G8 MAT"),
    "自信": ("timss2023_6-2-4-6_con-stu-scm.xlsx", "6.2.5 G4 MAT", "6.2.6 G8 MAT"),
    "価値": ("timss2023_6-2-7-8_con-stu-svm.xlsx", None, "6.2.8 G8 MAT"),
}
LABEL = {  # 尺度 -> (とても肯定の割合, 肯定しない割合, 2群の平均得点の差)。学年の接頭辞「小4・」「中2・」を付けて列名にする
    "好き": ("とても好き(%)", "好きでない(%)", "好き層と好きでない層の得点差"),
    "自信": ("とても自信あり(%)", "自信なし(%)", "自信あり層と自信なし層の得点差"),
    "価値": ("とても価値ありと考える(%)", "価値を感じない(%)", "価値あり層と価値なし層の得点差"),
}
M_MEAN = "平均得点"
# 列の位置（Exhibit のシート共通）: 国名 2、割合 5/11/17、平均得点 8/14/20
C_NAME, C_P1, C_P2, C_P3, C_A1, C_A2, C_A3 = 2, 5, 11, 17, 8, 14, 20

JA = {
    "Albania": "アルバニア", "Armenia": "アルメニア", "Australia": "オーストラリア", "Austria": "オーストリア",
    "Azerbaijan": "アゼルバイジャン", "Bahrain": "バーレーン", "Belgium (Flemish)": "ベルギー（フランドル語圏）",
    "Belgium (French)": "ベルギー（フランス語圏）", "Bosnia & Herzegovina": "ボスニア・ヘルツェゴビナ",
    "Brazil": "ブラジル", "Bulgaria": "ブルガリア", "Canada": "カナダ", "Chile": "チリ",
    "Chinese Taipei": "台湾", "Cote d'Ivoire": "コートジボワール", "Cyprus": "キプロス",
    "Czech Republic": "チェコ", "Denmark": "デンマーク", "England": "イングランド", "Finland": "フィンランド",
    "France": "フランス", "Georgia": "ジョージア", "Germany": "ドイツ", "Hong Kong SAR": "香港",
    "Hungary": "ハンガリー", "Iran, Islamic Rep. of": "イラン", "Ireland": "アイルランド", "Israel": "イスラエル",
    "Italy": "イタリア", "Japan": "日本", "Jordan": "ヨルダン", "Kazakhstan": "カザフスタン",
    "Korea, Rep. of": "韓国", "Kosovo": "コソボ", "Kuwait": "クウェート", "Latvia": "ラトビア",
    "Lithuania": "リトアニア", "Macao SAR": "マカオ", "Malaysia": "マレーシア", "Malta": "マルタ",
    "Montenegro": "モンテネグロ", "Morocco": "モロッコ", "Netherlands": "オランダ", "New Zealand": "ニュージーランド",
    "North Macedonia": "北マケドニア", "Norway": "ノルウェー", "Oman": "オマーン", "Palestinian Nat'l Auth.": "パレスチナ",
    "Poland": "ポーランド", "Portugal": "ポルトガル", "Qatar": "カタール", "Romania": "ルーマニア",
    "Saudi Arabia": "サウジアラビア", "Serbia": "セルビア", "Singapore": "シンガポール",
    "Slovak Republic": "スロバキア", "Slovenia": "スロベニア", "South Africa": "南アフリカ", "Spain": "スペイン",
    "Sweden": "スウェーデン", "Türkiye": "トルコ", "United Arab Emirates": "アラブ首長国連邦",
    "United States": "アメリカ", "Uzbekistan": "ウズベキスタン",
}
GRADE = {4: "小4", 8: "中2"}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _clean(name):
    return re.sub(r"\s*\(\d+\)\s*$", "", str(name).strip())


def _is_entity(name):
    return name.startswith("International") or ", UAE" in name or name in ("Ontario, Canada", "Quebec, Canada")


def read_attitude(fname, sheet):
    """{国名: (割合 3, 平均得点 3)}"""
    out = {}
    for r in read_xlsx(SRC / fname)[sheet]:
        if len(r) <= C_A3 or not isinstance(r[C_NAME], str):
            continue
        name = _clean(r[C_NAME])
        if name == "Country" or _is_entity(name):
            continue
        p = [_num(r[c]) for c in (C_P1, C_P2, C_P3)]
        a = [_num(r[c]) for c in (C_A1, C_A2, C_A3)]
        if p[0] is None or p[2] is None:
            continue
        out[name] = (p, a)
    return out


def read_means(fname):
    out = {}
    for r in next(iter(read_xlsx(SRC / fname).values())):
        if len(r) > 5 and isinstance(r[2], str) and _num(r[4]) is not None:
            name = _clean(r[2])
            if not _is_entity(name):
                out[name] = _num(r[4])
    return out


def col(grade, base):
    return f"{GRADE[grade]}・{base}"


def build():
    means = {4: read_means("timss2023_1-1-1_ach-g4m-dist.xlsx"), 8: read_means("timss2023_1-2-1_ach-g8m-dist.xlsx")}
    table = {}  # 国名 -> {列名: 値}
    for scale, (fname, s4, s8) in SCALES.items():
        hi, no, gap = LABEL[scale]
        for grade, sheet in ((4, s4), (8, s8)):
            if sheet is None:
                continue
            for name, (p, a) in read_attitude(fname, sheet).items():
                if abs(sum(p) - 100) > 2.5 + 1e-9:
                    raise SystemExit(f"{scale} G{grade} {name}: 割合の合計 {sum(p)}")
                if name not in means[grade]:
                    continue
                rec = table.setdefault(name, {})
                rec[col(grade, hi)], rec[col(grade, no)] = p[0], p[2]
                rec[col(grade, gap)] = None if a[0] is None or a[2] is None else round(a[0] - a[2], 1)
                rec[col(grade, M_MEAN)] = means[grade][name]
    metrics = metric_names()
    rows = []
    for name in sorted(table, key=lambda n: list(JA).index(n) if n in JA else 999):
        if name not in JA:
            raise SystemExit(f"日本語名がない: {name}")
        row = {"国・地域": JA[name]}
        for m in metrics:
            row[m] = table[name].get(m)
        rows.append(row)
    jp = next(r for r in rows if r["国・地域"] == "日本")
    if (jp[col(4, LABEL["好き"][0])], jp[col(4, LABEL["好き"][1])], jp[col(4, M_MEAN)], jp[col(8, M_MEAN)]) != (22.0, 42.0, 591.0, 595.0):
        raise SystemExit("日本の値が想定と違う")
    return rows


def metric_names():
    out = []
    for grade in (4, 8):
        for scale in SCALES:
            if scale == "価値" and grade == 4:
                continue
            out += [col(grade, m) for m in LABEL[scale]]
        out.append(col(grade, M_MEAN))
    return out


def main():
    rows = build()
    metrics = metric_names()
    n4 = sum(r[col(4, M_MEAN)] is not None for r in rows)
    n8 = sum(r[col(8, M_MEAN)] is not None for r in rows)
    doc = {
        "id": "timss2023_student_attitudes",
        "title": "【TIMSS 2023】算数・数学の「好き」「自信」「価値」と得点の国際比較（小4・中2）",
        "category": "math",
        "region": "global",
        "source_name": "IEA「TIMSS 2023 International Results in Mathematics and Science」(Exhibit 6.2.2〜6.2.8, 1.1.1, 1.2.1)",
        "source_url": "https://timss2023.org/results/",
        "verification": {
            "status": "verified",
            "checked_on": "2026-10-06",
            "note": "IEAがTIMSS 2023の報告書で公開したExhibitのExcelから機械的に取り込んだ（tools/build_timss_attitudes_catalog.py。手入力の数値はない）。各国で3群の割合の合計が100±2.5であることを検査。日本の小4（好き22%・42%、平均591）を確認。",
        },
        "description": ("TIMSS 2023で、児童生徒が算数・数学について答えた質問から作られた3つの尺度（好き・自信・価値。価値は中2のみ）について、"
                        "『とても』肯定する児童生徒の割合、『肯定しない』児童生徒の割合、その2群の平均得点の差（とても肯定−肯定しない）と、国・地域の算数・数学の平均得点。"
                        f"小4は{n4}、中2は{n8}の国・地域。国際平均とベンチマーク参加（州・首長国）は除いた。"
                        "列名の「小4・」「中2・」は学年。学年ごとに別の列にしたのは、小4と中2を同じ列に混ぜると、国の違いと学年の違いが混ざるため。得点の差は、公表された2群の平均得点の引き算で求めた。尺度は回答者が自分の気持ちを答えたもので、国によって回答の傾向が異なる。"),
        "unit": "%",
        "group_col": "国・地域",
        "recommended_chart": "ranking_bar",
        "metrics": metrics,
        "observation_unit": f"国・地域（{len(rows)}。小4のデータがあるのは{n4}、中2は{n8}）。学年ごとに別の列にした",
        "sample_population_note": "TIMSS 2023に参加した国・地域の小学校4年生・中学校2年生の標本調査（学校と学級を抽出）。2023年実施。回答は自己申告",
        "sample_population_size": f"{len(rows)}の国・地域（小4 {n4}、中2 {n8}）",
        "data": rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT, len(rows), "rows,", len(metrics), "metrics")


if __name__ == "__main__":
    main()
