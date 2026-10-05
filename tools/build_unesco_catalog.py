"""UNESCO統計研究所（UIS）のSDG 4.4.1データ（ICTスキル）から data/catalog/unesco_world_ict_skills.json を作る。

出典: UNESCO Institute for Statistics, Data API（https://api.uis.unesco.org/、データ版 20260507-91260335、2026年2月のデータ公開）
      指標 ICTSKILLPCPR（プログラミング・コーディングをした）、ICTSKILLARSP（表計算ソフトで基本的な算術式を使った）、
      ICTSKILLEPRS（プレゼンテーション資料を作成した）と、それぞれの女性（.F）・男性（.M）別。
      元の統計は ITU が各国の世帯調査などから集めたもの。
      data/source/uis_ictskill_2021.json に、2021年の API の応答を保存してある。

2021年は、3つの総計の指標がそろう国・地域が47で、日本を含み、調査年がそろう中で最も多い（2019年は日本がない）。
実行: python -m tools.build_unesco_catalog          （保存済みの応答から作る）
      python -m tools.build_unesco_catalog --fetch  （API から取り直して保存する）
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "source" / "uis_ictskill_2021.json"
OUT = ROOT / "data" / "catalog" / "unesco_world_ict_skills.json"
VERSION = "20260507-91260335"
YEAR = 2021
CODES = ["ICTSKILLPCPR", "ICTSKILLPCPR.F", "ICTSKILLPCPR.M", "ICTSKILLARSP", "ICTSKILLARSP.F", "ICTSKILLARSP.M",
         "ICTSKILLEPRS", "ICTSKILLEPRS.F", "ICTSKILLEPRS.M"]
TOTAL_CODES = ["ICTSKILLPCPR", "ICTSKILLARSP", "ICTSKILLEPRS"]

NAMES = {  # コード(code) -> (指標名)
    "ICTSKILLPCPR": "プログラミングをした人の割合",
    "ICTSKILLARSP": "表計算ソフトで基本的な算術式を使った人の割合",
    "ICTSKILLEPRS": "プレゼンテーション資料を作成した人の割合",
    "ICTSKILLPCPR.F": "プログラミングをした女性の割合",
    "ICTSKILLPCPR.M": "プログラミングをした男性の割合",
    "ICTSKILLARSP.F": "表計算で算術式を使った女性の割合",
    "ICTSKILLARSP.M": "表計算で算術式を使った男性の割合",
    "ICTSKILLEPRS.F": "プレゼン資料を作成した女性の割合",
    "ICTSKILLEPRS.M": "プレゼン資料を作成した男性の割合",
}
D_ARSP = "表計算の男女差（男性−女性，%ポイント）"
D_EPRS = "プレゼン資料作成の男女差（男性−女性，%ポイント）"
JA = {
    "ARE": "アラブ首長国連邦", "BEL": "ベルギー", "BGD": "バングラデシュ", "BIH": "ボスニア・ヘルツェゴビナ",
    "BLR": "ベラルーシ", "BRA": "ブラジル", "BTN": "ブータン", "CHE": "スイス", "COL": "コロンビア",
    "CZE": "チェコ", "DEU": "ドイツ", "DNK": "デンマーク", "ESP": "スペイン", "EST": "エストニア",
    "FIN": "フィンランド", "GEO": "ジョージア", "GRC": "ギリシャ", "HKG": "香港", "HRV": "クロアチア",
    "IRN": "イラン", "ISL": "アイスランド", "JAM": "ジャマイカ", "JPN": "日本", "KAZ": "カザフスタン",
    "KOR": "韓国", "KWT": "クウェート", "LTU": "リトアニア", "LUX": "ルクセンブルク", "MAC": "マカオ",
    "MAR": "モロッコ", "MEX": "メキシコ", "MLT": "マルタ", "MNE": "モンテネグロ", "MNG": "モンゴル",
    "MYS": "マレーシア", "NOR": "ノルウェー", "POL": "ポーランド", "PRT": "ポルトガル", "RUS": "ロシア",
    "SAU": "サウジアラビア", "SGP": "シンガポール", "SVK": "スロバキア", "SVN": "スロベニア", "TUR": "トルコ",
    "UKR": "ウクライナ", "UZB": "ウズベキスタン", "VNM": "ベトナム",
}


def fetch():
    q = "&".join("indicator=" + c for c in CODES)
    url = (f"https://api.uis.unesco.org/api/public/data/indicators?{q}&start={YEAR}&end={YEAR}"
           f"&version={VERSION}&format=json")
    raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
    d = json.loads(raw)
    SRC.write_text(json.dumps({"url": url, "version": VERSION, "year": YEAR, "records": d["records"]},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("saved", SRC, len(d["records"]), "records")


def build():
    src = json.loads(SRC.read_text(encoding="utf-8"))
    by = {}
    for r in src["records"]:
        if r["year"] != YEAR or r["value"] is None or r.get("qualifier"):
            continue
        by.setdefault(r["geoUnit"], {})[r["indicatorId"]] = r["value"]
    units = sorted(g for g, v in by.items() if all(c in v for c in TOTAL_CODES))
    unknown = [g for g in units if g not in JA]
    if unknown:
        raise SystemExit(f"日本語名がない: {unknown}")
    rows = []
    for g in sorted(units, key=lambda x: list(JA).index(x)):
        row = {"国・地域": JA[g]}
        for c in CODES:
            row[NAMES[c]] = by[g].get(c)
        # 公表された女性・男性の値の差（男性−女性、%ポイント）。両方ある国・地域だけ
        for base, label in (("ICTSKILLARSP", D_ARSP), ("ICTSKILLEPRS", D_EPRS)):
            f, m = by[g].get(base + ".F"), by[g].get(base + ".M")
            row[label] = None if f is None or m is None else round(m - f, 1)
        rows.append(row)
    for r in rows:
        for k, v in r.items():
            if k != "国・地域" and v is not None and not (-100 <= v <= 100 if "男女差" in k else 0 <= v <= 100):
                raise SystemExit(f"{r['国・地域']} {k}: {v}")
    jp = next(r for r in rows if r["国・地域"] == "日本")
    # UIS の日本の値（2021年）: プログラミング5.6、表計算50.9、プレゼン33.5
    assert (jp[NAMES["ICTSKILLPCPR"]], jp[NAMES["ICTSKILLARSP"]], jp[NAMES["ICTSKILLEPRS"]]) == (5.6, 50.9, 33.5)
    return rows


def main():
    if "--fetch" in sys.argv:
        fetch()
    rows = build()
    metrics = [NAMES[c] for c in CODES] + [D_ARSP, D_EPRS]
    doc = {
        "id": "unesco_world_ict_skills",
        "title": "【UNESCO統計研究所】成人のICTスキル（プログラミング・表計算・プレゼン資料作成）の国際比較（2021年）",
        "category": "info",
        "region": "global",
        "source_name": "UNESCO統計研究所（UIS）SDG 4.4.1 データ（元の統計はITU）",
        "source_url": "https://data.uis.unesco.org/",
        "verification": {
            "status": "verified",
            "checked_on": "2026-10-05",
            "note": f"UNESCO統計研究所のData API（api.uis.unesco.org、データ版 {VERSION}、2026年2月公開）から、指標 ICTSKILLPCPR・ICTSKILLARSP・ICTSKILLEPRS（と女性・男性別）の2021年の値を機械的に取り込んだ（tools/build_unesco_catalog.py。API の応答は data/source/uis_ictskill_2021.json に保存）。手入力の数値はない。日本の2021年の値（プログラミング5.6%、表計算50.9%、プレゼン33.5%）を確認。",
        },
        "description": ("UNESCO統計研究所（UIS）が公表するSDG 4.4.1（ICTスキルをもつ若者・成人の割合）の指標のうち、調査前の期間に、"
                        "「プログラミングやコーディングをした」「表計算ソフトで基本的な算術式を使った」「プレゼンテーション資料を作成した」と答えた人の割合（%）と、"
                        "その女性・男性別（2021年）。元の統計はITUが各国の世帯調査などから集めたもので、国によって調査の設計や対象年齢の範囲が異なる。"
                        "3つの総計の指標がそろう47の国・地域（日本を含む。欧州・中東・中南米・アジアの国・地域で、アフリカやオセアニアの国は少ない）。"
                        "プログラミングの男女別は日本の値がなく、データのある国・地域に限る。男女差は、公表された男性の割合から女性の割合を引いた値（%ポイント）で、両方の値がある国・地域だけ求めた。"),
        "unit": "%",
        "group_col": "国・地域",
        "recommended_chart": "ranking_bar",
        "metrics": metrics,
        "observation_unit": f"国・地域（2021年の3つの総計の指標がそろう{len(rows)}の国・地域）",
        "sample_population_note": "各国・地域の世帯調査などによる個人のICT利用の統計（ITUが収集）。対象は若者・成人（国により年齢の範囲が異なる）で、自己申告",
        "sample_population_size": f"{len(rows)}の国・地域（日本を含む）",
        "data": rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT, len(rows), "rows,", len(metrics), "metrics")


if __name__ == "__main__":
    main()
