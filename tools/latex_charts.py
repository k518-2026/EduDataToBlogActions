r"""LuaLaTeX 版の論文に入れる図（欄幅 8.6cm で読める大きさ）。

reportlab 版・記事用の図（src/visualizer.py）は、10×5.8インチで、題名や注記を画像の中に持つ。
2段組の1欄に縮めると、文字が約4ptになって読めない。ここでは、欄幅にそのまま入る大きさで描き、
題名は付けない（キャプションは LaTeX 側で付ける）。フォントは、本文と同じ原ノ味角ゴシックを使う。

    ranking_bar(dataset, metric, out_path)         上位・下位と日本の横棒グラフ
    scatter(dataset, analysis, angle, out_path)   散布図、回帰直線、95%信頼区間の帯
"""
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src.analyzer import is_collinear_or_redundant_pair
from src.utils import resolve_metric_unit

COL_W_IN = 8.4 / 2.54  # 1欄の幅（geometry: 用紙210mm、左右17mm、欄間8mm → (210-34-8)/2 = 84mm）
BLUE, RED, ORANGE, TEAL, CORAL, INK = "#457b9d", "#d62839", "#f4a261", "#2a9d8f", "#e76f51", "#1e293b"


def _setup_font():
    names = []
    for f in ("HaranoAjiGothic-Medium.otf", "HaranoAjiGothic-Bold.otf"):
        try:
            p = subprocess.run(["kpsewhich", f], capture_output=True, text=True).stdout.strip()
        except OSError:
            p = ""
        if p and Path(p).exists():
            fm.fontManager.addfont(p)
            names.append(fm.FontProperties(fname=p).get_name())
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = (names[:1] or []) + ["Yu Gothic", "Meiryo", "MS Gothic", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = True
    plt.rcParams["font.size"] = 6.5
    plt.rcParams["axes.linewidth"] = 0.5


def _clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(width=0.5, length=2, labelsize=6)
    ax.grid(True, linewidth=0.3, alpha=0.5, zorder=0)
    ax.set_axisbelow(True)


def _is_japan(name):
    return "日本" in str(name) or "Japan" in str(name)


def ranking_bar(dataset, metric, out_path, max_bars=24, n_top=14, n_bottom=6):
    df = dataset.df.copy()
    gcol = dataset.group_col
    if dataset.time_col and dataset.time_col in df.columns:
        df = df[df[dataset.time_col] == df[dataset.time_col].max()]
    s = df.groupby(gcol)[metric].mean().dropna().sort_values(ascending=True).reset_index()
    n_all = len(s)
    if n_all > max_bars:
        keep = set(range(n_all - n_top, n_all)) | set(range(n_bottom))
        keep |= {i for i, n in enumerate(s[gcol]) if _is_japan(n)}
        s = s.iloc[sorted(keep)].reset_index(drop=True)
    colors = [RED if _is_japan(n) else (ORANGE if ("平均" in str(n) or "OECD" in str(n)) else BLUE) for n in s[gcol]]
    unit = resolve_metric_unit(metric, dataset.unit)
    _setup_font()
    h = min(0.105 * len(s) + 0.5, 3.3)
    fig, ax = plt.subplots(figsize=(COL_W_IN, h))
    bars = ax.barh(s[gcol], s[metric], color=colors, height=0.72, zorder=3)
    top, bottom = float(s[metric].max()), float(s[metric].min())
    lo, hi = min(bottom, 0.0), max(top, 0.0)
    span = (hi - lo) or 1.0
    for b, v in zip(bars, s[metric]):
        # 負の棒の値は、ゼロ線の右に置く（左に置くと軸の名前に重なる）
        x_txt = v + 0.012 * span if v >= 0 else 0.012 * span
        ax.text(x_txt, b.get_y() + b.get_height() / 2, f"{v:.1f}".replace("-", "−"), va="center", ha="left", fontsize=5.5, color=INK, zorder=4)
    ax.set_xlim(lo - (0.04 * span if lo < 0 else 0.0), hi + 0.14 * span)
    if lo < 0:
        ax.axvline(0, color="#475569", linewidth=0.6, zorder=3.5)
    label = metric if metric.endswith(")") else f"{metric}（{unit}）"
    ax.set_xlabel(label, fontsize=6.5)
    _clean(ax)
    ax.grid(False, axis="y")
    ax.tick_params(axis="y", labelsize=5.5)
    for t, n in zip(ax.get_yticklabels(), s[gcol]):
        if _is_japan(n):
            t.set_color(RED)
    fig.tight_layout(pad=0.3)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return {"n_all": n_all, "n_shown": len(s)}


def pick_xy(dataset, analysis, angle):
    df = dataset.df
    tx, ty = getattr(angle, "scatter_x_metric", None), getattr(angle, "scatter_y_metric", None)
    if tx and ty and tx in df.columns and ty in df.columns and not is_collinear_or_redundant_pair(tx, ty):
        return tx, ty
    for cr in analysis.correlations:
        if cr.metric_x in df.columns and cr.metric_y in df.columns and not is_collinear_or_redundant_pair(cr.metric_x, cr.metric_y):
            return cr.metric_x, cr.metric_y
    return None, None


def _place_labels(ax, fig, pts):
    """名前を、点と他の名前に重ならない位置へ置く（8方向を試す）。置けないものは省く。"""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    placed = []
    axbox = ax.get_window_extent(rend)
    offs = [(4, 3, "left", "bottom"), (4, -3, "left", "top"), (-4, 3, "right", "bottom"), (-4, -3, "right", "top"),
            (0, 6, "center", "bottom"), (0, -6, "center", "top"), (7, 0, "left", "center"), (-7, 0, "right", "center")]
    xy_disp = [ax.transData.transform((x, y)) for _, x, y in pts]
    dots = [tuple(p) for p in xy_disp]
    for (name, x, y), (px, py) in zip(pts, xy_disp):
        for dx, dy, ha, va in offs:
            t = ax.annotate(name, (x, y), textcoords="offset points", xytext=(dx, dy), ha=ha, va=va, fontsize=5.5,
                            color=RED if _is_japan(name) else "#264653", zorder=6,
                            arrowprops=dict(arrowstyle="-", lw=0.3, color="#94a3b8", shrinkA=0, shrinkB=1.5))
            bb = t.get_window_extent(rend).expanded(1.03, 1.1)
            ok = axbox.x0 <= bb.x0 and bb.x1 <= axbox.x1 and axbox.y0 <= bb.y0 and bb.y1 <= axbox.y1
            ok = ok and not any(bb.overlaps(p) for p in placed)
            ok = ok and not any(bb.x0 - 2 <= qx <= bb.x1 + 2 and bb.y0 - 2 <= qy <= bb.y1 + 2 for qx, qy in dots if (qx, qy) != (px, py))
            if ok:
                placed.append(bb)
                break
            t.remove()


def scatter(dataset, analysis, angle, out_path, n_end_y=4, n_end_x=3, xy=None, logx=False):
    """xy=(x指標, y指標) で指標を指定できる。logx=True なら、横軸を常用対数にし、回帰直線と帯も対数にした x で求める。"""
    cx, cy = xy if xy else pick_xy(dataset, analysis, angle)
    if not cx:
        return None
    df = dataset.df.copy()
    d = df[[cx, cy] + ([dataset.group_col] if dataset.group_col in df.columns else [])].copy()
    d[cx] = pd.to_numeric(d[cx], errors="coerce")
    d[cy] = pd.to_numeric(d[cy], errors="coerce")
    d = d.dropna(subset=[cx, cy])
    if logx:
        d = d[d[cx] > 0]
    x, y = d[cx].to_numpy(float), d[cy].to_numpy(float)
    n = len(x)
    u = np.log10(x) if logx else x  # 回帰は、図の横軸と同じ尺度（対数なら対数）で行う
    _setup_font()
    fig, ax = plt.subplots(figsize=(COL_W_IN, COL_W_IN * 0.7))
    ax.scatter(x, y, s=9, color=TEAL, alpha=0.85, linewidths=0, zorder=3)
    if n > 3 and np.ptp(u) > 0:
        slope, icpt, *_ = stats.linregress(u, y)
        us = np.linspace(u.min(), u.max(), 100)
        res = y - (icpt + slope * u)
        se = np.sqrt(res @ res / (n - 2))
        tcrit = stats.t.ppf(0.975, n - 2)
        half = tcrit * se * np.sqrt(1 / n + (us - u.mean()) ** 2 / ((u - u.mean()) ** 2).sum())
        xs = 10 ** us if logx else us
        ax.fill_between(xs, icpt + slope * us - half, icpt + slope * us + half, color=CORAL, alpha=0.18, linewidth=0, zorder=2)
        ax.plot(xs, icpt + slope * us, color=CORAL, linewidth=1.0, zorder=4)
    if logx:
        ax.set_xscale("log")
    gcol = dataset.group_col
    if gcol in d.columns:
        idx = set(d.index[d[gcol].astype(str).str.contains("日本|Japan")])
        if n <= 30:
            idx |= set(d.index)
        else:
            for col, k in ((cy, n_end_y), (cx, n_end_x)):
                order = d[col].sort_values()
                idx |= set(order.index[:k]) | set(order.index[-k:])
        pts = [(str(d.at[i, gcol]), d.at[i, cx], d.at[i, cy]) for i in sorted(idx, key=lambda i: (not _is_japan(d.at[i, gcol]), i))]
        px = np.ptp(x) or 1.0
        py = np.ptp(y) or 1.0
        if logx:
            ax.set_xlim(x.min() / 1.25, x.max() * 1.6)
        else:
            ax.set_xlim(x.min() - 0.05 * px, x.max() + 0.08 * px)
        ax.set_ylim(y.min() - 0.08 * py, y.max() + 0.10 * py)
        fig.tight_layout(pad=0.3)
        _place_labels(ax, fig, pts)
    ux, uy = resolve_metric_unit(cx, dataset.unit), resolve_metric_unit(cy, dataset.unit)
    ax.set_xlabel(cx if cx.endswith(")") or cx.endswith("）") else f"{cx}（{ux}）", fontsize=6.5)
    ax.set_ylabel(cy if cy.endswith(")") or cy.endswith("）") else f"{cy}（{uy}）", fontsize=6.5)
    _clean(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return {"x": cx, "y": cy, "n": n}
