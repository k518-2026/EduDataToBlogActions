"""重回帰・パス解析・SEM・パス図（合成データ）。"""
import numpy as np
import pandas as pd

from src import sem_models as sm


def _df(n=300, seed=3):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=n)
    m = 0.6 * x + rng.normal(scale=0.8, size=n)
    y = 0.5 * m + rng.normal(scale=0.8, size=n)
    return pd.DataFrame({"x": x, "m": m, "y": y, "u": rng.normal(size=n)})


def test_regression_recovers_the_signal_and_reports_vif():
    r = sm.fit_regression(_df(), "y", ["m", "u"], n_boot=300)
    b = {c["x"]: c for c in r["coefficients"]}
    assert b["m"]["beta"] > 0.4 and b["m"]["p"] < .001 and abs(b["u"]["beta"]) < 0.15
    assert r["R2"] > 0.2 and r["max_VIF"] < 1.2 and r["n"] == 300


def test_path_analysis_indirect_effect_and_diagram():
    res = sm.fit_path_model(_df(), ["m ~ x", "y ~ m"], focus=[["x", "y"]], n_boot=300)
    e = res["effects"][0]
    assert e["direct"] == 0 and e["indirect"] > 0.15 and e["indirect_ci95_boot"][0] > 0
    assert abs(e["indirect"] - res["paths"][0]["beta"] * res["paths"][1]["beta"]) < 0.01
    tikz = sm.path_diagram_tikz(res, {"x": "原因", "m": "中間", "y": "結果"})
    assert tikz.count(r"\node") == 3 and tikz.count(r"\draw") == 2 and "R^2" in tikz


def test_sem_with_latent_variables():
    rng = np.random.default_rng(5)
    n = 400
    f = rng.normal(size=n)
    d = pd.DataFrame({f"a{i}": 0.8 * f + rng.normal(scale=0.6, size=n) for i in range(3)})
    d["y"] = 0.5 * f + rng.normal(scale=0.8, size=n)
    res = sm.fit_sem(d, {"F": ["a0", "a1", "a2"]}, ["y ~ F"])
    loads = [r for r in res["estimates"] if r["rval"] == "F" and r["lval"].startswith("a")]
    assert len(loads) == 3 and all(r["std"] > 0.6 for r in loads)
    assert "tikzpicture" in sm.sem_diagram_tikz(res, {"F": ["a0", "a1", "a2"]})
