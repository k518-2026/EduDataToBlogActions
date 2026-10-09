"""重回帰分析・パス解析・SEM（潜在変数を含む構造方程式モデリング）と、そのパス図（TikZ）。

国・地域などの集計値に当てはめる探索的な分析で、因果の検証ではない（係数は「関連」。「効果」「媒介」とは書かない）。
- 重回帰: statsmodels の OLS。標準化偏回帰係数、ロバスト標準誤差（HC3）、VIF、R²、調整済みR²、ブートストラップの信頼区間。
- パス解析: 観測変数だけの再帰モデル。標準化したパス係数、決定係数、直接・間接・総合の関連（ブートストラップの信頼区間）。
  適合度（χ²、CFI、RMSEA など）は、semopy が使えるときだけ。観測数が少ないモデルの適合度は目安。
- SEM: 潜在変数（測定モデル `=~`）を含むモデルは semopy で推定する。
semopy は E:\\ClaudeCode\\assets\\pylib に入れてある。
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_LIB = Path(__file__).resolve().parents[4] / "assets" / "pylib"  # E:\ClaudeCode\assets\pylib
if _LIB.exists() and str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))


def _r(x, nd=3):
    return None if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))) else round(float(x), nd)


def _stars(p):
    return "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""


# ---------------------------------------------------------------- 重回帰
def fit_regression(df: pd.DataFrame, y: str, xs: list[str], n_boot: int = 2000, seed: int = 20261009) -> dict:
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    d = df[[y] + xs].apply(pd.to_numeric, errors="coerce").dropna()
    n = len(d)
    z = (d - d.mean()) / d.std(ddof=1)
    X = sm.add_constant(d[xs])
    ols = sm.OLS(d[y], X).fit()
    rob = ols.get_robustcov_results(cov_type="HC3")
    zols = sm.OLS(z[y], sm.add_constant(z[xs])).fit()
    vif = {x: float(variance_inflation_factor(X.values, i + 1)) for i, x in enumerate(xs)}
    rng = np.random.default_rng(seed)
    boots = []
    zv, yv = z[xs].values, z[y].values
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        A = np.column_stack([np.ones(n), zv[idx]])
        try:
            boots.append(np.linalg.lstsq(A, yv[idx], rcond=None)[0][1:])
        except np.linalg.LinAlgError:
            continue
    boots = np.array(boots)
    lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
    coefs = []
    for i, x in enumerate(xs):
        coefs.append({"x": x, "B": _r(ols.params[x], 3), "SE_hc3": _r(rob.bse[i + 1], 3), "beta": _r(zols.params[x], 3),
                      "beta_ci95_boot": [_r(lo[i], 2), _r(hi[i], 2)], "t": _r(ols.tvalues[x], 2), "p": _r(ols.pvalues[x], 4),
                      "p_hc3": _r(rob.pvalues[i + 1], 4), "VIF": _r(vif[x], 2)})
    return {"type": "multiple_regression", "y": y, "n": n, "R2": _r(ols.rsquared), "adj_R2": _r(ols.rsquared_adj),
            "F": _r(ols.fvalue, 2), "df": [int(ols.df_model), int(ols.df_resid)], "F_p": _r(ols.f_pvalue, 5),
            "max_VIF": _r(max(vif.values()), 2), "coefficients": coefs, "n_boot": len(boots)}


# ---------------------------------------------------------------- パス解析
def _parse(equations: list[str]):
    eqs = []
    for e in equations:
        lhs, rhs = e.split("~")
        eqs.append((lhs.strip(), [t.strip() for t in rhs.split("+") if t.strip()]))
    return eqs


def _order(eqs):
    """変数を、外生（左）から内生（右）への層に分ける。"""
    ys = {y for y, _ in eqs}
    allv = []
    for y, xs in eqs:
        for v in xs + [y]:
            if v not in allv:
                allv.append(v)
    layer = {v: 0 for v in allv if v not in ys}
    pending = dict(eqs)
    while pending:
        progressed = False
        for y, xs in list(pending.items()):
            if all(x in layer for x in xs):
                layer[y] = max(layer[x] for x in xs) + 1
                pending.pop(y)
                progressed = True
        if not progressed:
            raise ValueError("再帰モデルではありません（循環があります）")
    return allv, layer


def _beta_matrix(z: pd.DataFrame, eqs, allv):
    idx = {v: i for i, v in enumerate(allv)}
    M = np.zeros((len(allv), len(allv)))
    r2 = {}
    for y, xs in eqs:
        A = z[xs].values
        b, *_ = np.linalg.lstsq(A, z[y].values, rcond=None)
        for x, bi in zip(xs, b):
            M[idx[y], idx[x]] = bi
        r2[y] = 1 - float(np.var(z[y].values - A @ b, ddof=0) / np.var(z[y].values, ddof=0))
    return M, r2


def _paths(eqs, src, dst):
    pre = {y: xs for y, xs in eqs}
    succ = {}
    for y, xs in eqs:
        for x in xs:
            succ.setdefault(x, []).append(y)
    out = []

    def walk(node, trail):
        if node == dst:
            out.append(trail)
            return
        for nx in succ.get(node, []):
            walk(nx, trail + [nx])

    walk(src, [src])
    return out


def fit_path_model(df: pd.DataFrame, equations: list[str], focus: list[list[str]] | None = None, n_boot: int = 2000,
                   seed: int = 20261009) -> dict:
    import statsmodels.api as sm

    eqs = _parse(equations)
    allv, layer = _order(eqs)
    d = df[allv].apply(pd.to_numeric, errors="coerce").dropna()
    n = len(d)
    z = (d - d.mean()) / d.std(ddof=1)
    idx = {v: i for i, v in enumerate(allv)}
    M, r2 = _beta_matrix(z, eqs, allv)
    I = np.eye(len(allv))
    T = np.linalg.inv(I - M) - I
    paths = []
    for y, xs in eqs:
        fit = sm.OLS(z[y], z[xs]).fit()
        for x in xs:
            paths.append({"from": x, "to": y, "beta": _r(fit.params[x], 3), "se": _r(fit.bse[x], 3), "p": _r(fit.pvalues[x], 4)})
    # ブートストラップ
    rng = np.random.default_rng(seed)
    acc = {"direct": {}, "indirect": {}, "total": {}}
    foc = [tuple(f) for f in (focus or [])]
    store = {f: {"direct": [], "indirect": [], "total": [], "paths": {}} for f in foc}
    for f in foc:
        for pth in _paths(eqs, *f):
            store[f]["paths"][" → ".join(pth)] = []
    for _ in range(n_boot):
        ib = rng.integers(0, n, n)
        zb = d.iloc[ib]
        sd = zb.std(ddof=1)
        if (sd == 0).any():
            continue
        zb = (zb - zb.mean()) / sd
        Mb, _ = _beta_matrix(zb, eqs, allv)
        Tb = np.linalg.inv(I - Mb) - I
        for f in foc:
            s, t = idx[f[0]], idx[f[1]]
            store[f]["direct"].append(Mb[t, s])
            store[f]["total"].append(Tb[t, s])
            store[f]["indirect"].append(Tb[t, s] - Mb[t, s])
            for name in store[f]["paths"]:
                nodes = name.split(" → ")
                store[f]["paths"][name].append(float(np.prod([Mb[idx[b], idx[a]] for a, b in zip(nodes[:-1], nodes[1:])])))
    effects = []
    for f in foc:
        s, t = idx[f[0]], idx[f[1]]
        ci = lambda arr: [_r(np.percentile(arr, 2.5), 2), _r(np.percentile(arr, 97.5), 2)]
        entry = {"from": f[0], "to": f[1], "direct": _r(M[t, s]), "direct_ci95_boot": ci(store[f]["direct"]),
                 "indirect": _r(T[t, s] - M[t, s]), "indirect_ci95_boot": ci(store[f]["indirect"]),
                 "total": _r(T[t, s]), "total_ci95_boot": ci(store[f]["total"]), "specific_indirect": []}
        for name, arr in store[f]["paths"].items():
            nodes = name.split(" → ")
            if len(nodes) > 2:
                entry["specific_indirect"].append({"path": name, "value": _r(float(np.prod([M[idx[b], idx[a]] for a, b in zip(nodes[:-1], nodes[1:])]))), "ci95_boot": ci(arr)})
        effects.append(entry)
    # 外生変数どうしの相関
    exo = [v for v in allv if layer[v] == 0]
    corr = {f"{a}|{b}": _r(float(np.corrcoef(d[a], d[b])[0, 1]), 2) for i, a in enumerate(exo) for b in exo[i + 1:]}
    res = {"type": "path_analysis", "n": n, "equations": equations, "variables": allv, "layers": layer, "paths": paths,
           "R2": {k: _r(v) for k, v in r2.items()}, "effects": effects, "exogenous_correlations": corr, "n_boot": len(store[foc[0]]["direct"]) if foc else 0}
    res["fit"] = _semopy_fit(d, equations)
    return res


def _semopy_fit(d: pd.DataFrame, equations: list[str], extra_lines: list[str] | None = None) -> dict | None:
    try:
        import semopy
    except Exception as e:  # noqa: BLE001
        return {"available": False, "reason": f"{type(e).__name__}"}
    names = {c: f"v{i}" for i, c in enumerate(d.columns)}
    desc = []
    for e in equations + (extra_lines or []):
        for c, nme in sorted(names.items(), key=lambda kv: -len(kv[0])):
            e = e.replace(c, nme)
        desc.append(e)
    try:
        mod = semopy.Model("\n".join(desc))
        mod.fit(d.rename(columns=names))
        st = semopy.calc_stats(mod).iloc[0]
        keep = {k: _r(float(st[k]), 3) for k in ("chi2", "DoF", "chi2 p-value", "CFI", "TLI", "RMSEA", "AIC", "BIC") if k in st.index}
        return {"available": True, **keep, "note": "観測数が少ないモデルの適合度は目安。自由度0に近いモデルでは意味が薄い。"}
    except Exception as e:  # noqa: BLE001
        return {"available": False, "reason": f"{type(e).__name__}: {e}"[:160]}


# ---------------------------------------------------------------- SEM（潜在変数）
def fit_sem(df: pd.DataFrame, latent: dict[str, list[str]], structural: list[str], rename: dict | None = None) -> dict:
    """latent: {"潜在変数名": [指標の列名, ...]}, structural: ["潜在変数A ~ 潜在変数B + 観測変数"]。"""
    import semopy

    cols = sorted({c for ind in latent.values() for c in ind} | {t.strip() for e in structural for t in re.split(r"[~+]", e) if t.strip() and t.strip() not in latent})
    cols = [c for c in cols if c in df.columns]
    d = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    names = {c: f"v{i}" for i, c in enumerate(cols)}
    lat_names = {k: f"L{j}" for j, k in enumerate(latent)}
    lines = []
    for k, ind in latent.items():
        lines.append(f"{lat_names[k]} =~ " + " + ".join(names[c] for c in ind))
    for e in structural:
        for k, nme in lat_names.items():
            e = e.replace(k, nme)
        for c, nme in sorted(names.items(), key=lambda kv: -len(kv[0])):
            e = e.replace(c, nme)
        lines.append(e)
    mod = semopy.Model("\n".join(lines))
    mod.fit(d.rename(columns=names))
    ins = mod.inspect(std_est=True)
    inv = {v: k for k, v in names.items()} | {v: k for k, v in lat_names.items()}
    rows = []
    for _, r in ins.iterrows():
        if r["op"] in ("~", "=~"):
            rows.append({"lval": inv.get(r["lval"], r["lval"]), "op": r["op"], "rval": inv.get(r["rval"], r["rval"]),
                         "est": _r(r["Estimate"]), "std": _r(r["Est. Std"]), "p": None if str(r["p-value"]) in ("-", "nan") else _r(float(r["p-value"]), 4)})
    st = semopy.calc_stats(mod).iloc[0]
    fit = {k: _r(float(st[k]), 3) for k in ("chi2", "DoF", "chi2 p-value", "CFI", "TLI", "RMSEA", "AIC", "BIC") if k in st.index}
    return {"type": "sem", "n": len(d), "model": "\n".join(lines), "estimates": rows, "fit": fit}


# ---------------------------------------------------------------- パス図（TikZ）
def path_diagram_tikz(result: dict, labels: dict[str, str] | None = None, latent: set[str] | None = None, width_cm: float = 16.5) -> str:
    """fit_path_model の結果から、TikZ のパス図（tikzpicture）を作る。係数は標準化したパス係数。破線は p≧.05。"""
    labels = labels or {}
    latent = latent or set()
    layers = result["layers"]
    nl = max(layers.values()) + 1
    cols = {i: [v for v in result["variables"] if layers[v] == i] for i in range(nl)}
    dx = width_cm / max(nl, 1) - 0.3
    pos = {}
    for i, vs in cols.items():
        h = (len(vs) - 1) * 2.0
        for j, v in enumerate(vs):
            pos[v] = (i * dx + 1.4, h / 2 - j * 2.0)
    out = [r"\begin{tikzpicture}[>=stealth,node distance=1cm,", r"  obs/.style={draw,rounded corners=2pt,minimum height=1.0cm,text width=%.1fcm,align=center,font=\footnotesize}," % (dx * 0.78),
           r"  lat/.style={draw,ellipse,minimum height=1.0cm,text width=%.1fcm,align=center,font=\footnotesize}," % (dx * 0.7),
           r"  lab/.style={font=\scriptsize,fill=white,inner sep=1pt}]"]
    for v, (x, y) in pos.items():
        style = "lat" if v in latent else "obs"
        extra = ""
        if v in result["R2"]:
            extra = r"\\{\scriptsize $R^2$=" + f"{result['R2'][v]:.2f}".lstrip("0") + "}"
        out.append(rf"  \node[{style}] ({_nid(v)}) at ({x:.2f},{y:.2f}) {{{_tx(labels.get(v, v))}{extra}}};")
    for pth in result["paths"]:
        p = pth["p"]
        sty = "->" if p < .05 else "->,dashed"
        val = f"{pth['beta']:.2f}".replace("0.", ".").replace("-.", "−.") + _stars(p)
        out.append(rf"  \draw[{sty}] ({_nid(pth['from'])}) -- node[lab,pos=0.5] {{{val}}} ({_nid(pth['to'])});")
    out.append(r"\end{tikzpicture}")
    return "\n".join(out)


def _nid(v: str) -> str:
    import zlib

    return "n" + str(zlib.crc32(v.encode("utf-8")))


def _tx(s: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"), ("$", r"\$"), ("{", r"\{"), ("}", r"\}")):
        s = s.replace(a, b)
    return s


def sem_diagram_tikz(result: dict, latent: dict[str, list[str]], labels: dict[str, str] | None = None, width_cm: float = 16.5) -> str:
    """fit_sem の結果から、潜在変数（楕円）と指標（四角）を含む TikZ のパス図を作る。係数は標準化推定値。破線は p≧.05。

    指標を横一列（スロット）に並べ、潜在変数はその指標グループの真上に置く。観測変数の結果は、1スロットを使う。
    """
    labels = labels or {}
    indicators = {c for ind in latent.values() for c in ind}
    rows = result["estimates"]
    struct = [r for r in rows if r["lval"] not in indicators]
    loads = [r for r in rows if r["lval"] in indicators]
    ys = {r["lval"] for r in struct}
    nodes = []
    for r in struct:
        for v in (r["rval"], r["lval"]):
            if v not in nodes:
                nodes.append(v)
    layer = {v: 0 for v in nodes if v not in ys}
    pending = {y: [r["rval"] for r in struct if r["lval"] == y] for y in ys}
    while pending:
        for y, xs in list(pending.items()):
            if all(x in layer for x in xs):
                layer[y] = max(layer[x] for x in xs) + 1
                pending.pop(y)
    order = sorted(nodes, key=lambda v: (layer[v], nodes.index(v)))
    nslots = sum(len(latent[v]) if v in latent else 2 for v in order)
    sw = width_cm / nslots                      # 1スロットの幅
    box = max(sw - 0.25, 1.6)
    slot, nxt = {}, 0
    for v in order:
        k = len(latent[v]) if v in latent else 2   # 観測変数は2スロット分の幅
        slot[v] = [nxt + j for j in range(k)]
        nxt += k
    xs_ = lambda j: (j + 0.5) * sw
    out = [r"\begin{tikzpicture}[>=stealth,",
           r"  obs/.style={draw,rounded corners=2pt,minimum height=0.9cm,text width=%.2fcm,align=center,font=\tiny,inner sep=2pt}," % box,
           r"  lat/.style={draw,ellipse,minimum height=1.2cm,text width=%.2fcm,align=center,font=\footnotesize,inner sep=1pt}," % (min(box * 1.4, 3.4)),
           r"  lab/.style={font=\scriptsize,fill=white,inner sep=1pt}]"]
    ypos = {}
    for v in order:
        x = sum(xs_(j) for j in slot[v]) / len(slot[v])
        ypos[v] = 0.0
        extra = "" if v in latent else ",text width=%.2fcm,font=\\scriptsize" % (2 * sw - 0.35)
        out.append(r"  \node[%s%s] (%s) at (%.2f,0) {%s};" % ("lat" if v in latent else "obs", extra, _nid(v), x, _tx(labels.get(v, v))))
    for lv, inds in latent.items():
        if lv not in slot:
            continue
        for j, c in zip(slot[lv], inds):
            out.append(r"  \node[obs] (%s) at (%.2f,-3.0) {%s};" % (_nid(c), xs_(j), _tx(labels.get(c, c))))
            ld = next((r for r in loads if r["lval"] == c and r["rval"] == lv), None)
            if ld:
                val = ("%.2f" % ld["std"]).replace("0.", ".")
                out.append(r"  \draw[->] (%s) -- node[lab,pos=0.62] {%s} (%s);" % (_nid(lv), val, _nid(c)))
    for r in struct:
        sig = r["p"] is not None and r["p"] < .05
        val = ("%.2f" % r["std"]).replace("0.", ".").replace("-.", "−.") + _stars(r["p"] if r["p"] is not None else 1)
        out.append(r"  \draw[%s] (%s) -- node[lab,pos=0.5] {%s} (%s);" % ("->" if sig else "->,dashed", _nid(r["rval"]), val, _nid(r["lval"])))
    out.append(r"\end{tikzpicture}")
    return "\n".join(out)
