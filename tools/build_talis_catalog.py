"""TALIS 2024 の公表表から data/catalog/oecd_talis_teacher_survey.json を作る。

出典: OECD『Results from TALIS 2024: The State of Teaching』（2025-10-07 公開）Annex C 第1章の表（Excel、StatLink）
      data/source/talis2024_vol1_statlink_n0x63b.xlsx（取得元は data/source/README.md）
      Table 1.31（指導実践）、Table 1.49（デジタル資源の使い方）、Table 1.58（デジタル資源の自己効力感）、Table 1.59（AIの利用）
対象は前期中等教育（ISCED 2、日本は中学校）の教員。国・地域ごとの割合（%）。

検算: 日本の「AIを使った」17.4%（OECD平均 36.3%）は、OECD の日本の国別ノート（data/source/talis2024_country_note_japan.pdf）の
「17% … OECD平均 36%」と、シンガポール 74.9% は同ノートの「75%」と一致する。
実行: python -m tools.build_talis_catalog
"""
import json
from pathlib import Path

from tools.xlsx_read import read_xlsx

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "source" / "talis2024_vol1_statlink_n0x63b.xlsx"
OUT = ROOT / "data" / "catalog" / "oecd_talis_teacher_survey.json"

# (指標名, 表, 見出しの書き出し)。割合（%）は見出しのセルの列、標準誤差（S.E.）は次の列
METRICS = [
    ("批判的思考を要する課題を出す教員の割合", "Table 1.31", "Give tasks that require students to think critically"),
    ("明確な解のない課題を出す教員の割合", "Table 1.31", "Present tasks for which there is no obvious solution"),
    ("少人数グループで共同の解決を求める教員の割合", "Table 1.31", "Have students work in small groups"),
    ("学習の計画・管理にデジタル資源を使わせる教員の割合", "Table 1.49", "Allow students to plan and monitor"),
    ("デジタル資源で生徒どうしの協働を支える教員の割合", "Table 1.49", "Support collaboration among students"),
    ("デジタル資源で学習を支えられる自信のある教員の割合", "Table 1.58", "Support student learning through the use of digital"),
    ("AIを仕事で使った教員の割合", "Table 1.59", "Percentage of teachers who report having"),
]

JA = {
    "Albania": "アルバニア", "Australia": "オーストラリア", "Austria": "オーストリア", "Azerbaijan": "アゼルバイジャン",
    "Bahrain": "バーレーン", "Flemish Comm. (Belgium)": "ベルギー（フランドル語圏）",
    "French Comm. (Belgium)": "ベルギー（フランス語圏）", "Brazil": "ブラジル", "Bulgaria": "ブルガリア",
    "Chile": "チリ", "Colombia": "コロンビア", "Costa Rica": "コスタリカ", "Croatia": "クロアチア",
    "Cyprus": "キプロス", "Czechia": "チェコ", "Denmark": "デンマーク", "Estonia": "エストニア",
    "Finland": "フィンランド", "France": "フランス", "Hungary": "ハンガリー", "Iceland": "アイスランド",
    "Israel": "イスラエル", "Italy": "イタリア", "Japan": "日本", "Kazakhstan": "カザフスタン", "Korea": "韓国",
    "Kosovo": "コソボ", "Latvia": "ラトビア", "Lithuania": "リトアニア", "Malta": "マルタ",
    "Montenegro": "モンテネグロ", "Morocco": "モロッコ", "North Macedonia": "北マケドニア", "Poland": "ポーランド",
    "Portugal": "ポルトガル", "Romania": "ルーマニア", "Saudi Arabia": "サウジアラビア", "Serbia": "セルビア",
    "Shanghai (China)": "上海（中国）", "Singapore": "シンガポール", "Slovak Republic": "スロバキア",
    "Slovenia": "スロベニア", "South Africa": "南アフリカ", "Spain": "スペイン", "Sweden": "スウェーデン",
    "Türkiye": "トルコ", "United Arab Emirates": "アラブ首長国連邦", "United States": "アメリカ",
    "Uzbekistan": "ウズベキスタン", "Viet Nam": "ベトナム", "Alberta (Canada)*": "アルバータ州（カナダ）",
    "Netherlands*": "オランダ", "New Zealand*": "ニュージーランド", "Norway*": "ノルウェー",
}
# 平均の行と、構成する地域と重なる「Belgium」（フランドル語圏・フランス語圏を別に載せている）は国・地域の行に含めない
SKIP = {"OECD average-27", "EU total-22", "TALIS average-49", "Belgium"}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _find(rows, prefix):
    for ri, r in enumerate(rows[:14]):
        for ci, c in enumerate(r):
            if c and str(c).startswith(prefix):
                return ci
    raise SystemExit(f"見出しが見つからない: {prefix}")


def _isced2_rows(rows):
    return [r for r in rows if len(r) > 3 and r[0] and r[1] and str(r[1]).startswith("2")]


def build():
    wb = read_xlsx(SRC)
    table = {}  # 国・地域 -> {指標: 値}
    average = {}
    for metric, tname, prefix in METRICS:
        rows = wb[tname]
        ci = _find(rows, prefix)
        for r in _isced2_rows(rows):
            name = str(r[0])
            val = _num(r[ci])
            if name == "OECD average-27":
                average[metric] = val
            if name in SKIP:
                continue
            table.setdefault(name, {})[metric] = val
    unknown = [n for n in table if n not in JA]
    if unknown:
        raise SystemExit(f"日本語名がない: {unknown}")
    rows_out = []
    for name, vals in table.items():
        got = [vals.get(m) for m, _, _ in METRICS]
        if sum(v is not None for v in got) < 5:
            continue
        row = {"国・地域": JA[name]}
        for (m, _, _), v in zip(METRICS, got):
            row[m] = None if v is None else round(v, 1)
        rows_out.append(row)
    # 検算
    by = {r["国・地域"]: r for r in rows_out}
    jp, sg = by["日本"], by["シンガポール"]
    if round(jp["AIを仕事で使った教員の割合"]) != 17 or round(sg["AIを仕事で使った教員の割合"]) != 75:
        raise SystemExit("国別ノートの値（日本17%、シンガポール75%）と合わない")
    if round(average["AIを仕事で使った教員の割合"]) != 36:
        raise SystemExit("国別ノートのOECD平均（36%）と合わない")
    for r in rows_out:
        for m, _, _ in METRICS:
            v = r[m]
            if v is not None and not (0 <= v <= 100):
                raise SystemExit(f"{r['国・地域']} {m}: {v}")
    return rows_out, average


def main():
    rows, average = build()
    metrics = [m for m, _, _ in METRICS]
    avg_text = "、".join(f"{m}={average[m]:.1f}%" for m in metrics)
    doc = {
        "id": "oecd_talis_teacher_survey",
        "title": "【OECD TALIS 2024】中学校（前期中等教育）の教員の指導実践・デジタル資源・AI利用の国際比較",
        "category": "math",  # 記事を info と math で交互に出すための区分（内容を表さない。元の設定のまま）
        "region": "global",
        "source_name": "OECD「Results from TALIS 2024: The State of Teaching」（2025年10月公開）",
        "source_url": "https://www.oecd.org/en/publications/results-from-talis-2024_90df6235-en.html",
        "verification": {
            "status": "verified",
            "checked_on": "2026-10-05",
            "note": "OECDが公開したTALIS 2024の統計表（Annex C 第1章、StatLink: https://stat.link/n0x63b、2025-12更新）の Table 1.31・1.49・1.58・1.59 から前期中等教育（ISCED 2）の国・地域の値を機械的に取り込んだ（tools/build_talis_catalog.py）。手入力の数値はない。日本のAI利用17%・OECD平均36%・シンガポール75%は、OECDの日本の国別ノート（PDF）の記述と一致。",
        },
        "description": ("OECDの国際教員指導環境調査（TALIS）2024による、前期中等教育（日本は中学校）の教員の回答の割合（%）。"
                        "指導実践（「頻繁に」または「いつも」行う）：批判的思考を要する課題を出す、明確な解のない課題を出す、少人数グループで共同の解決を求める。"
                        "デジタル資源（「頻繁に」または「いつも」使う）：生徒が自分の学習を計画・管理するため、生徒どうしの協働を支えるため。"
                        "デジタル資源の自己効力感（「かなり」または「とても」できると感じる）：デジタル資源・ツールで生徒の学習を支える。"
                        "AI：調査前の12か月に仕事でAIを使った。"
                        "OECD平均（27か国）は、" + avg_text + "。"
                        f"対象は{len(rows)}の国・地域（ベルギーはフランドル語圏とフランス語圏を別に載せ、ベルギー全体の行は除いた）。"
                        "自己申告の調査で、国際比較は慎重に解釈する必要がある（OECDの注意）。オランダ・ニュージーランド・ノルウェー・アルバータ州（カナダ）は、"
                        "無回答による偏りの危険が高いとOECDが注意している推定値を含む。"),
        "unit": "%",
        "group_col": "国・地域",
        "recommended_chart": "ranking_bar",
        "metrics": metrics,
        "observation_unit": f"国・地域（TALIS 2024に参加した前期中等教育の{len(rows)}の国・地域）",
        "sample_population_note": "各国・地域の前期中等教育（日本は中学校）の教員の標本調査（学校を抽出し、教員を無作為抽出）。2024年実施。自己申告",
        "sample_population_size": f"{len(rows)}の国・地域（日本を含む）",
        "data": rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT, len(rows), "rows,", len(metrics), "metrics")


if __name__ == "__main__":
    main()
