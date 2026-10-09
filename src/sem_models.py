"""重回帰分析・パス解析・SEM（潜在変数を含む構造方程式モデリング）と、そのパス図（TikZ）。

国・地域などの集計値に当てはめる探索的な分析で、因果の検証ではない（係数は「関連」。「効果」「媒介」とは書かない）。
- 重回帰: statsmodels の OLS。標準化偏回帰係数、ロバスト標準誤差（HC3）、VIF、R²、調整済みR²、ブートストラップの信頼区間。
- パス解析: 観測変数だけの再帰モデル。標準化したパス係数、決定係数、直接・間接・総合の関連（ブートストラップの信頼区間）。
  適合度（χ²、CFI、RMSEA など）は、semopy が使えるときだけ。観測数が少ないモデルの適合度は目安。
- SEM: 潜在変数（測定モデル `=~`）を含むモデルは、自前の最尤法（RAM 表現。_ram_fit）で推定する。
  適合度は χ²（N×F、lavaan の既定と同じ）、自由度、p、CFI、TLI、RMSEA。観測数が少ないモデルの適合度は目安。
  （semopy の χ²・自由度は、外生変数の扱いが標準と違い、手計算と合わなかったので使わない。）
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
    res["fit"] = _ram_fit(d, {}, equations)["fit"]
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
    """潜在変数を含む SEM。latent: {"潜在変数名": [指標の列名, ...]}, structural: ["潜在変数A ~ 潜在変数B + 観測変数"]。最尤法（自前のエンジン）。"""
    out = _ram_fit(df, latent, structural)
    desc = [f"{k} =~ " + " + ".join(v) for k, v in latent.items()] + list(structural)
    return {"type": "sem", "n": out["fit"]["n"], "model": "\n".join(desc), "estimates": out["estimates"], "fit": out["fit"], "R2": out["R2"]}


# ---------------------------------------------------------------- 最尤法の SEM エンジン（RAM 表現）
def _ram_fit(d: pd.DataFrame, latent: dict[str, list[str]], structural: list[str], n_start: int = 3, seed: int = 1) -> dict:
    """観測変数のパス解析と、潜在変数を含む SEM を、同じ最尤法で推定する。

    - 外生変数（観測・潜在）の分散と、外生変数どうしの共分散は、すべて自由推定（lavaan の fixed.x=FALSE と同じ）。
    - 潜在変数は、最初の指標の負荷量を1に固定してスケールを決める。
    - χ² = N × F_ML（lavaan の既定と同じ）。自由度 = 観測の積率の数 − 自由パラメータの数。
    - CFI・TLI の基準モデルは、観測変数の分散だけ自由で、共分散がすべて0のモデル。RMSEA = sqrt(max(χ²−df,0)/(N·df))。
    標準化推定値は、モデルから導く分散（観測・潜在）で標準化。p は、数値ヘッセ行列から求めたワルド検定。
    """
    from scipy import optimize, stats

    obs_all = list(dict.fromkeys(list(d.columns)))
    eqs = _parse(structural)
    lat = list(latent)
    used_obs = set(c for ind in latent.values() for c in ind) | {t for y, xs in eqs for t in [y] + xs if t in obs_all}
    obs = [c for c in obs_all if c in used_obs]
    z = d[obs].apply(pd.to_numeric, errors="coerce").dropna()
    n = len(z)
    S = np.cov(((z - z.mean()) / z.std(ddof=1)).values.T, ddof=0)
    p_obs = len(obs)
    names = obs + lat
    ix = {v: i for i, v in enumerate(names)}
    m = len(names)
    # A（パス）: A[結果, 原因]
    free_A, fixed_A = [], {}
    for lv, inds in latent.items():
        for j, c in enumerate(inds):
            if j == 0:
                fixed_A[(ix[c], ix[lv])] = 1.0
            else:
                free_A.append((ix[c], ix[lv]))
    for y, xs in eqs:
        for x in xs:
            free_A.append((ix[y], ix[x]))
    endog = {ix[c] for ind in latent.values() for c in ind} | {ix[y] for y, _ in eqs}
    exog = [i for i in range(m) if i not in endog]
    free_S = [(i, i) for i in range(m)] + [(a, b) for k, a in enumerate(exog) for b in exog[k + 1:]]
    npar = len(free_A) + len(free_S)
    moments = p_obs * (p_obs + 1) // 2
    df = moments - npar
    sel = np.zeros((p_obs, m))
    for i in range(p_obs):
        sel[i, i] = 1.0

    def build(theta):
        A = np.zeros((m, m))
        for (i, j), v in fixed_A.items():
            A[i, j] = v
        for k, (i, j) in enumerate(free_A):
            A[i, j] = theta[k]
        Sm = np.zeros((m, m))
        for k, (i, j) in enumerate(free_S):
            v = theta[len(free_A) + k]
            Sm[i, j] = v
            Sm[j, i] = v
        return A, Sm

    def implied(theta):
        A, Sm = build(theta)
        Ai = np.linalg.inv(np.eye(m) - A)
        full = Ai @ Sm @ Ai.T
        return sel @ full @ sel.T, full, A

    logdetS = np.linalg.slogdet(S)[1]

    def fml(theta):
        try:
            sig, _, _ = implied(theta)
            sign, ld = np.linalg.slogdet(sig)
            if sign <= 0:
                return 1e6
            return ld + float(np.trace(S @ np.linalg.inv(sig))) - logdetS - p_obs
        except np.linalg.LinAlgError:
            return 1e6

    rng = np.random.default_rng(seed)
    best = None
    for s in range(n_start):
        th0 = np.zeros(npar)
        for k, (i, j) in enumerate(free_A):
            if names[j] in latent and names[i] in latent[names[j]]:   # 負荷量: 最初の指標との相関を出発点に
                th0[k] = float(np.corrcoef(z[names[i]], z[latent[names[j]][0]])[0, 1])
            else:
                th0[k] = 0.2
        for k, (i, j) in enumerate(free_S):
            th0[len(free_A) + k] = (0.8 if names[i] in latent else 0.5 if i in endog else 1.0) if i == j else 0.0
        th0 = th0 + rng.normal(scale=0.05 * s, size=npar)
        bnds = [(None, None)] * len(free_A) + [((1e-4, None) if i == j else (None, None)) for (i, j) in free_S]
        r = optimize.minimize(fml, th0, method="L-BFGS-B", bounds=bnds, options={"maxiter": 5000, "ftol": 1e-12, "gtol": 1e-8})
        if best is None or r.fun < best.fun:
            best = r
    th = best.x
    F = max(float(best.fun), 0.0)
    chi2 = n * F
    # 基準モデル
    chi2_b = n * (np.sum(np.log(np.diag(S))) - logdetS)
    df_b = p_obs * (p_obs - 1) // 2
    fit = {"n": n, "chi2": _r(chi2, 3), "df": int(df), "n_free_params": int(npar), "converged": bool(best.success)}
    if df > 0:
        fit["p"] = _r(1 - stats.chi2.cdf(chi2, df), 4)
        fit["RMSEA"] = _r(math.sqrt(max(chi2 - df, 0) / (n * df)), 3)
        fit["CFI"] = _r(1 - max(chi2 - df, 0) / max(chi2_b - df_b, chi2 - df, 1e-12), 3)
        fit["TLI"] = _r(((chi2_b / df_b) - (chi2 / df)) / ((chi2_b / df_b) - 1), 3) if df_b > 0 else None
    else:
        fit["note"] = "飽和モデル（自由度0）：適合度は評価できない"
    # 推定値・標準化・p
    sig, full, A = implied(th)
    sd = np.sqrt(np.diag(full))
    try:
        import numdifftools as nd

        H = nd.Hessian(fml, step=1e-4)(th)
        cov = 2.0 * np.linalg.inv(n * H)
        se = np.sqrt(np.clip(np.diag(cov), 0, None))
    except Exception:  # noqa: BLE001
        se = np.full(npar, np.nan)
    rows = []
    for k, (i, j) in enumerate(free_A):
        std = th[k] * sd[j] / sd[i]
        pv = float(2 * (1 - stats.norm.cdf(abs(th[k] / se[k])))) if se[k] and not np.isnan(se[k]) else None
        rows.append({"lval": names[i], "op": "=~" if names[j] in latent and names[i] in latent[names[j]] else "~",
                     "rval": names[j], "est": _r(th[k]), "std": _r(std), "p": _r(pv, 4) if pv is not None else None, "se": _r(se[k], 3)})
    for (i, j), v in fixed_A.items():
        rows.append({"lval": names[i], "op": "=~", "rval": names[j], "est": 1.0, "std": _r(v * sd[j] / sd[i]), "p": None, "se": None})
    r2 = {names[i]: _r(1 - (th[len(free_A) + free_S.index((i, i))] / full[i, i])) for i in endog if (i, i) in free_S}
    return {"fit": fit, "estimates": rows, "R2": r2, "names": names, "latent": lat, "observed": obs}


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
    xpos = {}
    for v in order:
        xpos[v] = sum(xs_(j) for j in slot[v]) / len(slot[v])
    for v in order:
        x = xpos[v]
        ypos[v] = 0.0
        if v not in latent and layer[v] == 0:
            # 外生の観測変数は、矢印の邪魔にならないよう、結果の変数の少し上に置く
            targets = [r["lval"] for r in struct if r["rval"] == v]
            if targets and targets[0] in xpos:
                x = (xpos[targets[0]] + min(xpos.values())) / 2 + sw * 0.3
                x = min(max(x, 1.0), width_cm - 1.0)
                ypos[v] = 1.7
            xpos[v] = x
        extra = "" if v in latent else ",text width=%.2fcm,font=\\scriptsize" % (2 * sw - 0.35)
        out.append(r"  \node[%s%s] (%s) at (%.2f,%.2f) {%s};" % ("lat" if v in latent else "obs", extra, _nid(v), x, ypos[v], _tx(labels.get(v, v))))
    for lv, inds in latent.items():
        if lv not in slot:
            continue
        for j, c in zip(slot[lv], inds):
            out.append(r"  \node[obs] (%s) at (%.2f,-2.2) {%s};" % (_nid(c), xs_(j), _tx(labels.get(c, c))))
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
