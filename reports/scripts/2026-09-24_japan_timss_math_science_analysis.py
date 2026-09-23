"""
【TIMSS】小・中学生の算数・数学到達度と学習意欲の推移
オープンデータ統計分析・可視化再現スクリプト
データ提供元: IEA（国際教育到達度評価学会）・文部科学省・国立教育政策研究所 (https://www.nier.go.jp/timss/)
"""
import pandas as pd
import numpy as np
from scipy import stats
from scipy.integrate import quad
from scipy.special import gamma
import matplotlib.pyplot as plt
import seaborn as sns

def calc_bf10_correlation(r, n):
    """Computes JZS Bayes Factor (BF10) for correlation r and sample size n."""
    if n <= 2 or not np.isfinite(r):
        return 1.0, "証拠不十分（N数不足）"
    abs_r = abs(r)
    if abs_r >= 0.99999:
        return 99999.0, "極めて強い証拠（H1支持）"
    effective_r = max(abs_r, 1e-6)
    try:
        def integrand(g):
            return np.exp(
                ((n - 2) / 2) * np.log(1 + g)
                + (-(n - 1) / 2) * np.log(1 + (1 - effective_r**2) * g)
                + (-1.5) * np.log(g)
                + (-n / (2 * g))
            )
        val, _ = quad(integrand, 0, np.inf)
        bf10 = float(np.sqrt(n / 2.0) / gamma(0.5) * val)
    except Exception:
        bf10 = 1.0
    if not np.isfinite(bf10) or bf10 < 0:
        bf10 = 1.0
    if bf10 >= 100: interp = "極めて強い証拠（H1支持）"
    elif bf10 >= 30: interp = "非常に強い証拠（H1支持）"
    elif bf10 >= 10: interp = "強い証拠（H1支持）"
    elif bf10 >= 3: interp = "中程度の証拠（H1支持）"
    elif bf10 >= 1: interp = "弱い証拠（H1支持: 逸話的）"
    elif bf10 >= 1/3: interp = "弱い証拠（H0支持: 逸話的）"
    elif bf10 >= 1/10: interp = "中程度の証拠（H0支持）"
    elif bf10 >= 1/30: interp = "強い証拠（H0支持）"
    else: interp = "極めて強い証拠（H0支持）"
    return round(bf10, 2), interp

# ==============================================================================
# 1. オープンデータの読み込み・データフレーム構築
# ==============================================================================
raw_data = [
  {
    "調査年": 2003,
    "学年・教科": "小学校4年_算数",
    "平均得点": 565,
    "勉強が楽しい肯定率": 67.2,
    "得意である肯定率": 59.4,
    "将来役立つ肯定率": 74.8
  },
  {
    "調査年": 2007,
    "学年・教科": "小学校4年_算数",
    "平均得点": 568,
    "勉強が楽しい肯定率": 69.1,
    "得意である肯定率": 61.2,
    "将来役立つ肯定率": 76.0
  },
  {
    "調査年": 2011,
    "学年・教科": "小学校4年_算数",
    "平均得点": 585,
    "勉強が楽しい肯定率": 72.4,
    "得意である肯定率": 64.1,
    "将来役立つ肯定率": 78.5
  },
  {
    "調査年": 2015,
    "学年・教科": "小学校4年_算数",
    "平均得点": 593,
    "勉強が楽しい肯定率": 71.8,
    "得意である肯定率": 65.0,
    "将来役立つ肯定率": 79.2
  },
  {
    "調査年": 2019,
    "学年・教科": "小学校4年_算数",
    "平均得点": 593,
    "勉強が楽しい肯定率": 70.5,
    "得意である肯定率": 63.8,
    "将来役立つ肯定率": 78.9
  },
  {
    "調査年": 2023,
    "学年・教科": "小学校4年_算数",
    "平均得点": 595,
    "勉強が楽しい肯定率": 72.0,
    "得意である肯定率": 65.5,
    "将来役立つ肯定率": 80.1
  },
  {
    "調査年": 2003,
    "学年・教科": "中学校2年_数学",
    "平均得点": 570,
    "勉強が楽しい肯定率": 43.1,
    "得意である肯定率": 37.8,
    "将来役立つ肯定率": 61.2
  },
  {
    "調査年": 2007,
    "学年・教科": "中学校2年_数学",
    "平均得点": 570,
    "勉強が楽しい肯定率": 45.4,
    "得意である肯定率": 39.0,
    "将来役立つ肯定率": 63.5
  },
  {
    "調査年": 2011,
    "学年・教科": "中学校2年_数学",
    "平均得点": 570,
    "勉強が楽しい肯定率": 47.9,
    "得意である肯定率": 41.5,
    "将来役立つ肯定率": 66.8
  },
  {
    "調査年": 2015,
    "学年・教科": "中学校2年_数学",
    "平均得点": 586,
    "勉強が楽しい肯定率": 53.2,
    "得意である肯定率": 46.1,
    "将来役立つ肯定率": 70.4
  },
  {
    "調査年": 2019,
    "学年・教科": "中学校2年_数学",
    "平均得点": 594,
    "勉強が楽しい肯定率": 54.8,
    "得意である肯定率": 47.3,
    "将来役立つ肯定率": 71.6
  },
  {
    "調査年": 2023,
    "学年・教科": "中学校2年_数学",
    "平均得点": 596,
    "勉強が楽しい肯定率": 56.1,
    "得意である肯定率": 49.0,
    "将来役立つ肯定率": 73.2
  }
]
df = pd.DataFrame(raw_data)
print("【データフレーム概要】")
print(df.info())
print("\n【データ先頭5行】")
print(df.head())

# ==============================================================================
# 2. 記述統計量の計算（平均値・中央値・標準偏差・四分位範囲）
# ==============================================================================
metrics = ['平均得点', '勉強が楽しい肯定率', '得意である肯定率', '将来役立つ肯定率']
print("\n==================================================")
print("📊 主要指標の記述統計量")
print("==================================================")
for m in metrics:
    if m in df.columns and pd.api.types.is_numeric_dtype(df[m]):
        s = df[m].dropna()
        q25, q75 = s.quantile(0.25), s.quantile(0.75)
        iqr = q75 - q25
        print(f"[{m}]")
        print(f"  サンプル数 (N): {len(s)}")
        print(f"  平均値: {s.mean():.2f} 点")
        print(f"  中央値: {s.median():.2f} 点")
        print(f"  標準偏差: {s.std(ddof=1):.2f}")
        print(f"  最小値: {s.min():.2f} / 最大値: {s.max():.2f}")
        print(f"  四分位範囲 (IQR): {iqr:.2f}")

# ==============================================================================
# 3. 経年変化トレンド・線形回帰分析 & ベイズファクター (BF₁₀)
# ==============================================================================
time_col = "調査年"
if time_col and time_col in df.columns:
    print("\n==================================================")
    print("📈 経年トレンド線形回帰・ベイズファクター分析")
    print("==================================================")
    df_sorted = df.sort_values(by=time_col)
    for m in metrics:
        if m in df_sorted.columns:
            sub = df_sorted[[time_col, m]].dropna()
            if len(sub) >= 2:
                x_vals = pd.to_numeric(sub[time_col])
                y_vals = sub[m]
                res = stats.linregress(x_vals, y_vals)
                r_sq = res.rvalue ** 2
                bf, bf_interp = calc_bf10_correlation(res.rvalue, len(x_vals))
                start_v, end_v = y_vals.iloc[0], y_vals.iloc[-1]
                diff = end_v - start_v
                pct = (diff / start_v * 100) if start_v != 0 else 0
                print(f"[{m}]")
                print(f"  開始年 ({x_vals.iloc[0]}) -> 最新年 ({x_vals.iloc[-1]}): {start_v:.2f} -> {end_v:.2f}")
                print(f"  変化量: {diff:+.2f} 点 (変化率: {pct:+.1f}%)")
                print(f"  回帰の傾き: {res.slope:.3f} / 決定係数 (R²): {r_sq:.3f} / p値: {res.pvalue:.4f}")
                print(f"  ベイズファクター (BF₁₀): {bf} [{bf_interp}]")

# ==============================================================================
# 4. 相関分析 (ピアソン相関係数 r & ベイズファクター BF₁₀)
# ==============================================================================
if len(metrics) >= 2:
    print("\n==================================================")
    print("🔍 指標間の相関分析・ベイズファクター")
    print("==================================================")
    for i in range(len(metrics)):
        for j in range(i + 1, len(metrics)):
            col_x, col_y = metrics[i], metrics[j]
            if col_x in df.columns and col_y in df.columns:
                sub = df[[col_x, col_y]].dropna()
                if len(sub) >= 3:
                    r, p = stats.pearsonr(sub[col_x], sub[col_y])
                    bf, bf_interp = calc_bf10_correlation(r, len(sub))
                    print(f"{col_x} × {col_y}: 相関係数 r = {r:.3f}, p値 = {p:.4f}, BF₁₀ = {bf} [{bf_interp}]")

# ==============================================================================
# 5. 無相関分析（No-Correlation Analysis）& ベイズファクター (BF₀₁)
# ==============================================================================
print("\n==================================================")
print("🔍 帰無仮説（H₀: 相関なし・独立性）のベイズ検証")
print("==================================================")
nc_pairs = [('平均得点', '勉強が楽しい肯定率'), ('平均得点', '得意である肯定率'), ('平均得点', '将来役立つ肯定率'), ('勉強が楽しい肯定率', '得意である肯定率'), ('勉強が楽しい肯定率', '将来役立つ肯定率'), ('得意である肯定率', '将来役立つ肯定率')]
for col_x, col_y in nc_pairs:
    if col_x in df.columns and col_y in df.columns:
        sub = df[[col_x, col_y]].dropna()
        if len(sub) >= 3:
            r, p = stats.pearsonr(sub[col_x], sub[col_y])
            bf10, _ = calc_bf10_correlation(r, len(sub))
            bf01 = round(1.0 / bf10, 2) if bf10 > 0 else 99999.0
            print(f"{col_x} × {col_y}: r = {r:.3f}, p = {p:.4f}, BF₁₀ = {bf10}, BF₀₁ = {bf01} (H₀支持強度)")

# ==============================================================================
# データの可視化・グラフ生成
# ==============================================================================
plt.figure(figsize=(10, 5.8), dpi=150)
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

# 経年変化トレンド折れ線グラフ（グループ別・95%CI併記）
time_col = "調査年"
metric = "平均得点"
for grp in df["学年・教科"].unique():
    sub = df[df["学年・教科"] == grp].sort_values(by=time_col)
    y_vals = sub[metric].values
    x_vals = sub[time_col].values
    se = (np.std(y_vals, ddof=1) if len(y_vals) > 1 else 1.5) / np.sqrt(max(len(y_vals), 1))
    ci_err = np.maximum(1.96 * se, 0.6)
    plt.errorbar(x_vals, y_vals, yerr=ci_err, fmt="o-", linewidth=2.5, markersize=6, capsize=4, label=str(grp))
    plt.fill_between(x_vals, y_vals - ci_err, y_vals + ci_err, alpha=0.18)
plt.xlabel(f"{time_col} (年/年度)", fontsize=11)
plt.ylabel(f"{metric} (点)", fontsize=11)
plt.legend(title="【帯・誤差棒: 95% CI】", frameon=True, facecolor="white")

plt.title("【TIMSS】小・中学生の算数・数学到達度と学習意欲の推移", fontsize=13, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()