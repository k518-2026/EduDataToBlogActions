"""PISA 2025 の数学の男女得点差（全参加国・地域）のカタログ JSON を、公表元の Excel から作る。

    python -m tools.build_pisa2025_gender_catalog

入力（data/source/ にある。取得元は data/source/README.md）
  ・Table I.B1.2a.38  数学の平均得点 2003〜2025（男女計）→ 2025 の列
  ・Table I.B1.2c.29 / 30 / 31  女子・男子の数学の平均得点と男女差（男子−女子）、標準誤差

手で入力した数値は 1 つもない。値が合わなければ（男子−女子 ≠ 公表の男女差、男女計が男女の間にない）止まる。
"""
import json
import re
from pathlib import Path

from tools.xlsx_read import read_xlsx

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "source"
OUT = ROOT / "data" / "catalog" / "oecd_pisa2025_gender_gap.json"

JA = {
    "Albania*": "アルバニア", "Argentina": "アルゼンチン", "Armenia": "アルメニア", "Australia": "オーストラリア",
    "Austria": "オーストリア", "Azerbaijan": "アゼルバイジャン", "Belgium": "ベルギー", "Brazil": "ブラジル",
    "Brunei Darussalam": "ブルネイ", "B-S-J-Z (China)": "北京・上海・江蘇・浙江（中国）", "Bulgaria": "ブルガリア",
    "Cambodia": "カンボジア", "Canada*": "カナダ", "Chile": "チリ", "Colombia": "コロンビア", "Costa Rica": "コスタリカ",
    "Croatia": "クロアチア", "Cyprus": "キプロス", "Czechia": "チェコ", "Denmark": "デンマーク",
    "Dominican Republic": "ドミニカ共和国", "Dushanbe (Tajikistan)": "ドゥシャンベ（タジキスタン）", "Ecuador": "エクアドル",
    "El Salvador": "エルサルバドル", "Estonia": "エストニア", "Finland": "フィンランド", "France": "フランス",
    "Georgia": "ジョージア", "Germany": "ドイツ", "Greece": "ギリシャ", "Guatemala": "グアテマラ",
    "Hong Kong (China)": "香港", "Hungary": "ハンガリー", "Iceland": "アイスランド", "Indonesia": "インドネシア",
    "Ireland": "アイルランド", "Israel": "イスラエル", "Italy": "イタリア", "Japan": "日本", "Jordan": "ヨルダン",
    "Kazakhstan": "カザフスタン", "Kenya": "ケニア", "Korea": "韓国", "Kosovo": "コソボ",
    "Kurdistan Region (Iraq)": "クルディスタン地域（イラク）", "Kyrgyzstan": "キルギス", "Latvia": "ラトビア",
    "Lebanon": "レバノン", "Lithuania": "リトアニア", "Luxembourg": "ルクセンブルク", "Macao (China)": "マカオ",
    "Malaysia": "マレーシア", "Malta": "マルタ", "Mauritius": "モーリシャス", "Mexico": "メキシコ", "Moldova": "モルドバ",
    "Mongolia": "モンゴル", "Montenegro": "モンテネグロ", "Morocco": "モロッコ", "Netherlands*": "オランダ",
    "New Zealand*": "ニュージーランド", "North Macedonia": "北マケドニア", "Norway*": "ノルウェー",
    "Palestinian Authority": "パレスチナ", "Paraguay": "パラグアイ", "Peru": "ペルー", "Philippines": "フィリピン",
    "Poland": "ポーランド", "Portugal": "ポルトガル", "Qatar": "カタール", "Romania": "ルーマニア", "Rwanda": "ルワンダ",
    "Saudi Arabia": "サウジアラビア", "Serbia": "セルビア", "Singapore": "シンガポール", "Slovak Republic": "スロバキア",
    "Slovenia": "スロベニア", "Spain": "スペイン", "Sweden": "スウェーデン", "Switzerland": "スイス",
    "Chinese Taipei": "台湾", "Thailand": "タイ", "Türkiye": "トルコ", "Ukrainian regions (17 of 27)": "ウクライナの17地域",
    "United Arab Emirates": "アラブ首長国連邦", "United Kingdom": "イギリス", "United States*": "アメリカ",
    "Uruguay": "ウルグアイ", "Uzbekistan": "ウズベキスタン", "Viet Nam": "ベトナム", "Zambia": "ザンビア",
}
# OECD の表で「標本抽出基準を満たさなかった項目がある」との注意（*）がある国
SAMPLING_NOTE = {"Albania*", "Canada*", "Netherlands*", "New Zealand*", "Norway*", "United States*"}


def _num(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def main():
    total = read_xlsx(SRC / "pisa2025_vol1_table_B1.2a_mrq53f.xlsx")["Table I.B1.2a.38"]
    g = read_xlsx(SRC / "pisa2025_vol1_table_B1.4_68stqn.xlsx")
    girls, boys, diff = g["Table I.B1.2c.29"], g["Table I.B1.2c.30"], g["Table I.B1.2c.31"]

    head = next(r for r in total if r and r[1] == "PISA 2003")
    tcol = next(i for i, c in enumerate(head) if c == "PISA 2025")
    gcol = None
    for tbl in (girls, boys, diff):
        hdr = next(r for r in tbl if r and any(c and re.match(r"PISA 2025", str(c).strip()) for c in r))
        col = next(i for i, c in enumerate(hdr) if c and re.match(r"PISA 2025", str(c).strip()))
        assert gcol in (None, col), "列の位置が表で違う"
        gcol = col
    assert (tcol, gcol) == (15, 19), (tcol, gcol)

    def table_rows(tbl):
        return {r[0]: r for r in tbl if r and isinstance(r[0], str)}

    rt, rg, rb, rd = (table_rows(t) for t in (total, girls, boys, diff))
    rows, skipped = [], []
    for en, ja in JA.items():
        try:
            t, gi, bo, df, se = (_num(rt[en][tcol]), _num(rg[en][gcol]), _num(rb[en][gcol]),
                                 _num(rd[en][gcol]), _num(rd[en][gcol + 1]))
        except KeyError:
            skipped.append((en, "表にない"))
            continue
        if None in (t, gi, bo, df, se):
            skipped.append((en, "欠測"))
            continue
        assert abs((bo - gi) - df) < 0.01, ("男子−女子が差と合わない", en, bo - gi, df)
        assert min(gi, bo) - 1 <= t <= max(gi, bo) + 1, ("男女計が男女の間にない", en)
        rows.append({
            "国・地域": ja,
            "数学得点": round(t, 1), "男子得点": round(bo, 1), "女子得点": round(gi, 1),
            "男女得点差": round(df, 1), "男女得点差の標準誤差": round(se, 1),
        })
    assert rows, "行がない"
    names_in_tables = {r[0] for r in diff if r and isinstance(r[0], str)}
    for en in JA:
        assert en in names_in_tables or any(en == s[0] for s in skipped), en
    jp = next(r for r in rows if r["国・地域"] == "日本")
    assert (jp["数学得点"], jp["男女得点差"]) == (525.4, 16.3), jp

    n_sig = sum(abs(r["男女得点差"]) > 1.96 * r["男女得点差の標準誤差"] for r in rows)
    n_boys = sum(r["男女得点差"] > 0 for r in rows)
    doc = {
        "id": "oecd_pisa2025_gender_gap",
        "title": "【OECD PISA 2025】数学的リテラシーの男女得点差（全参加国・地域）",
        "category": "math", "region": "global",
        "source_name": "OECD（経済協力開発機構）PISA 2025 Results (Volume I)",
        "source_url": "https://www.oecd.org/en/publications/pisa-2025-results-volume-i_73451bc5-en.html",
        "verification": {"status": "verified", "checked_on": "2026-10-06", "note": (
            "OECD が公表した PISA 2025 Results (Volume I) の Excel（StatLink）から、tools/build_pisa2025_gender_catalog.py で機械的に作成。"
            "男女計は Table I.B1.2a.38、女子・男子・男女差とその標準誤差は Table I.B1.2c.29/30/31。"
            f"男子−女子が公表の男女差と一致し、男女計が男女の間にあることを{len(rows)}件すべてで確認。手入力の数値はない。"
            "標本抽出基準についての注意（*）がOECDの表にある国（" + "・".join(JA[k] for k in sorted(SAMPLING_NOTE)) + "）も含めている。"
            + (("欠測のため除いた: " + "、".join(f"{JA[a]}（{b}）" for a, b in skipped) + "。") if skipped else ""))},
        "description": (
            f"PISA 2025（15歳の生徒の学習到達度調査）の数学的リテラシーについて、{len(rows)}の国・地域ごとの平均得点（男女計）、男子・女子の平均得点、"
            "男女得点差（男子−女子）、男女得点差の標準誤差。OECD平均は除いた。"
            f"男女差の正負は、男子のほうが高い国・地域が{n_boys}、女子のほうが高いところが{len(rows) - n_boys}。"
            f"男女差が標準誤差の1.96倍を超える（おおよそ5%水準で有意）のは{n_sig}。"
            "PISA 2025の主要分野は科学で、数学は副次的な分野。標本抽出基準の注意（*）がある国・地域を含む。"),
        "unit": "点", "group_col": "国・地域", "recommended_chart": "ranking_bar",
        "metrics": ["数学得点", "男子得点", "女子得点", "男女得点差"],
        "observation_unit": f"国・地域（{len(rows)}）。2025年調査の1時点",
        "sample_population_note": "各国・地域の15歳の生徒（学校に在籍する者）の標本調査。2025年実施",
        "sample_population_size": f"{len(rows)}の国・地域（OECDの公表による）",
        "data": rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT, len(rows), "rows; skipped", skipped, "| sig", n_sig, "boys higher", n_boys)


if __name__ == "__main__":
    main()
