"""論文を書く前に、検証済みデータから「使ってよい数値」の一覧（事実ファイル）を作る。

    python -m tools.make_facts <dataset_id> <angle_id>      → temp/facts_<dataset_id>.json

論文の執筆者（人でもモデルでも）は、ここにある数値だけを本文に書く。
tools/check_numbers.py が、本文の数値がこのファイルにあるかを検査する。
"""
import json
import math
import sys
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats

from src.academic_contexts import get_all_angles_for_dataset
from src.analyzer import compute_bayes_factor_correlation, is_collinear_or_redundant_pair
from src.config import CATALOG_DIR, TEMP_DIR


def _r(x, nd=2):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), nd)


def _fisher_ci(r, n):
    if n <= 3 or abs(r) >= 1:
        return None
    z, se = math.atanh(r), 1 / math.sqrt(n - 3)
    return [round(math.tanh(z - 1.96 * se), 2), round(math.tanh(z + 1.96 * se), 2)]


def describe(s):
    s = pd.to_numeric(s, errors="coerce").dropna()
    q1, q3 = s.quantile(.25), s.quantile(.75)
    return {"n": int(len(s)), "mean": _r(s.mean()), "median": _r(s.median()), "sd": _r(s.std(ddof=1)),
            "min": _r(s.min()), "max": _r(s.max()), "iqr": _r(q3 - q1)}


def pair_stats(df, a, b):
    sub = df[[a, b]].apply(pd.to_numeric, errors="coerce").dropna()
    n = len(sub)
    if n < 5:
        return None
    r, p = stats.pearsonr(sub[a], sub[b])
    rho = stats.spearmanr(sub[a], sub[b])[0]
    bf10 = compute_bayes_factor_correlation(float(r), n)[0]
    return {"x": a, "y": b, "n": n, "r": _r(r), "ci95": _fisher_ci(float(r), n), "rho": _r(rho),
            "p": ("<.001" if p < .001 else _r(p, 3)), "bf10": (">1000" if bf10 > 1000 else _r(bf10, 2))}


def _stem_derived(df, cross):
    """大分類（学科名の「・」の前）ごとの集計，志願→入学の差，年度間の変化。"""
    g, ratio, apply_ = "学科", "入学者の女性比率（%）", "入学志願者の女性比率（%）"
    c = cross.copy()
    c["分野"] = c[g].str.split("・").str[0]
    out = {"year": int(c["年度"].iloc[0]), "n_departments": int(len(c))}
    cats = {}
    for k, sub in c.groupby("分野"):
        tot, fem = sub["入学者数"].sum(), sub["女性の入学者数"].sum()
        cats[k] = {"n": int(len(sub)), "enrollees": int(tot), "female_ratio_weighted": _r(fem / tot * 100, 1),
                   "female_ratio_min": _r(sub[ratio].min(), 1), "female_ratio_max": _r(sub[ratio].max(), 1)}
    out["by_field"] = cats
    tot, fem = c["入学者数"].sum(), c["女性の入学者数"].sum()
    out["all_58_weighted_female_ratio"] = _r(fem / tot * 100, 1)
    out["n_below_20"] = int((c[ratio] < 20).sum()); out["n_below_30"] = int((c[ratio] < 30).sum())
    out["n_above_70"] = int((c[ratio] > 70).sum())
    out["n_between_40_60"] = int(((c[ratio] >= 40) & (c[ratio] <= 60)).sum())
    cg = c.set_index(g)
    d = (cg[ratio] - cg[apply_]).dropna()
    out["admit_minus_applicant_ratio_points"] = {"mean": _r(d.mean()), "median": _r(d.median()), "sd": _r(d.std(ddof=1)),
                                                 "n_positive": int((d > 0).sum()), "n_negative": int((d < 0).sum()),
                                                 "n_within_1pt": int((d.abs() <= 1).sum()),
                                                 "largest_positive": [[k, _r(v, 1)] for k, v in d.sort_values().tail(3)[::-1].items()],
                                                 "largest_negative": [[k, _r(v, 1)] for k, v in d.sort_values().head(3).items()]}
    y0, y1 = df["年度"].min(), df["年度"].max()
    a_, b_ = df[df["年度"] == y0].set_index(g), df[df["年度"] == y1].set_index(g)
    dd = (b_[ratio] - a_[ratio]).dropna()
    out["change_ratio"] = {"from": int(y0), "to": int(y1), "mean": _r(dd.mean()), "median": _r(dd.median()), "n_up": int((dd > 0).sum()),
                           "n_down": int((dd < 0).sum()), "n_abs_ge_2": int((dd.abs() >= 2).sum()),
                           "largest_up": [[k, _r(v, 1)] for k, v in dd.sort_values().tail(3)[::-1].items()],
                           "largest_down": [[k, _r(v, 1)] for k, v in dd.sort_values().head(3).items()]}
    for k in ("工学・機械工学", "工学・電気通信工学", "理学・物理学", "理学・数学"):
        if k in c[g].values:
            row = c[c[g] == k].iloc[0]
            out.setdefault("named", {})[k] = {"enrollees": int(row["入学者数"]), "female": int(row["女性の入学者数"]),
                                              "ratio": _r(row[ratio], 1), "applicant_ratio": _r(row[apply_], 1)}
    return out


def make(dataset_id, angle_id):
    doc = json.loads((CATALOG_DIR / f"{dataset_id}.json").read_text(encoding="utf-8"))
    df = pd.DataFrame(doc["data"])
    angle = [a for a in get_all_angles_for_dataset(dataset_id) if a.angle_id == angle_id][0]
    group, time, metrics = doc.get("group_col"), doc.get("time_col"), [m for m in doc["metrics"] if m in df.columns]
    facts = {"dataset_id": dataset_id, "angle_id": angle_id, "title": doc["title"], "source": doc["source_name"],
             "source_url": doc.get("source_url"), "description": doc["description"], "unit": doc.get("unit"),
             "verification_note": doc["verification"]["note"], "rows": len(df), "metrics": metrics,
             "angle": {"theme": angle.title_theme, "rq1": angle.rq1, "rq2": angle.rq2, "focus_metrics": angle.focus_metrics,
                       "scatter": [angle.scatter_x_metric, angle.scatter_y_metric]}}
    cross = df
    if time and time in df.columns:
        latest = df[time].max()
        cross = df[df[time] == latest]
        facts["cross_section_year"] = int(latest) if str(latest).isdigit() else str(latest)
    facts["descriptives"] = {m: describe(cross[m]) for m in metrics}
    if time and group and time in df.columns:  # first-to-last change per group
        first, last = df[time].min(), df[time].max()
        a_, b_ = df[df[time] == first].set_index(group), df[df[time] == last].set_index(group)
        ch = {}
        for m in angle.focus_metrics[:2]:
            if m in df.columns:
                d = (b_[m] - a_[m]).dropna().sort_values()
                ch[m] = {"from": str(first), "to": str(last), "n_groups": int(len(d)), "n_up": int((d > 0).sum()),
                         "n_down": int((d < 0).sum()), "mean_change": _r(d.mean()),
                         "largest_up": [[k, _r(v)] for k, v in d.tail(5)[::-1].items()],
                         "largest_down": [[k, _r(v)] for k, v in d.head(5).items()]}
        facts["change_first_to_last"] = ch
    if group and group in cross.columns:
        facts["rankings"] = {}
        for m in angle.focus_metrics[:4]:
            if m in cross.columns:
                s = cross.set_index(group)[m].apply(pd.to_numeric, errors="coerce").dropna().sort_values(ascending=False)
                entry = {"n": int(len(s)), "top5": [[k, _r(v, 1)] for k, v in s.head(5).items()],
                         "bottom5": [[k, _r(v, 1)] for k, v in s.tail(5).items()]}
                for jp in ("日本",):
                    if jp in s.index:
                        entry["japan"] = {"value": _r(s[jp], 1), "rank_from_top": int(list(s.index).index(jp) + 1)}
                facts["rankings"][m] = entry
    if dataset_id == "japan_stem_cs_enrollment":
        facts["derived"] = _stem_derived(df, cross)
    pairs = []
    for a, b in combinations(metrics, 2):
        if not is_collinear_or_redundant_pair(a, b):
            ps = pair_stats(cross, a, b)
            if ps:
                pairs.append(ps)
    facts["correlations_all_pairs"] = pairs
    facts["note"] = ("これは全ペアの探索結果。論文では研究課題にもとづくペアだけを書き，全ペアを探索したことと，多重比較の影響を明記する。"
                     "『計・部分・増減・割合』のように計算でつながったペアは，相関を結果として書かない。")
    out = TEMP_DIR / f"facts_{dataset_id}.json"
    out.write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    return out, facts


if __name__ == "__main__":
    path, f = make(*sys.argv[1:3])
    print("wrote", path, "| pairs", len(f["correlations_all_pairs"]))
