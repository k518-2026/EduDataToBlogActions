"""
【児童生徒指導要録調査】小・中学校における不登校児童生徒数とICT学習支援の推移
オープンデータ統計分析・可視化再現スクリプト
データ提供元: 文部科学省「児童生徒の問題行動・不登校等生徒指導上の諸課題に関する調査」 (https://www.mext.go.jp/a_menu/shotou/seitoshidou/1302902.htm)
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
    "年度": 2018,
    "学校種": "小学校",
    "不登校児童生徒数": 36120,
    "千人あたり不登校率": 5.7,
    "ICT出席扱い生徒数": 286
  },
  {
    "年度": 2019,
    "学校種": "小学校",
    "不登校児童生徒数": 44430,
    "千人あたり不登校率": 7.0,
    "ICT出席扱い生徒数": 434
  },
  {
    "年度": 2020,
    "学校種": "小学校",
    "不登校児童生徒数": 63350,
    "千人あたり不登校率": 10.0,
    "ICT出席扱い生徒数": 2623
  },
  {
    "年度": 2021,
    "学校種": "小学校",
    "不登校児童生徒数": 81498,
    "千人あたり不登校率": 13.0,
    "ICT出席扱い生徒数": 5264
  },
  {
    "年度": 2022,
    "学校種": "小学校",
    "不登校児童生徒数": 105112,
    "千人あたり不登校率": 17.0,
    "ICT出席扱い生徒数": 9425
  },
  {
    "年度": 2018,
    "学校種": "中学校",
    "不登校児童生徒数": 128574,
    "千人あたり不登校率": 36.5,
    "ICT出席扱い生徒数": 982
  },
  {
    "年度": 2019,
    "学校種": "中学校",
    "不登校児童生徒数": 137350,
    "千人あたり不登校率": 39.4,
    "ICT出席扱い生徒数": 1278
  },
  {
    "年度": 2020,
    "学校種": "中学校",
    "不登校児童生徒数": 132777,
    "千人あたり不登校率": 40.9,
    "ICT出席扱い生徒数": 4185
  },
  {
    "年度": 2021,
    "学校種": "中学校",
    "不登校児童生徒数": 163442,
    "千人あたり不登校率": 50.0,
    "ICT出席扱い生徒数": 6184
  },
  {
    "年度": 2022,
    "学校種": "中学校",
    "不登校児童生徒数": 193936,
    "千人あたり不登校率": 59.8,
    "ICT出席扱い生徒数": 10432
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
metrics = ['不登校児童生徒数', '千人あたり不登校率', 'ICT出席扱い生徒数']
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
        print(f"  平均値: {s.mean():.2f} 人")
        print(f"  中央値: {s.median():.2f} 人")
        print(f"  標準偏差: {s.std(ddof=1):.2f}")
        print(f"  最小値: {s.min():.2f} / 最大値: {s.max():.2f}")
        print(f"  四分位範囲 (IQR): {iqr:.2f}")

# ==============================================================================
# 3. 経年変化トレンド・線形回帰分析 & ベイズファクター (BF₁₀)
# ==============================================================================
time_col = "年度"
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
                print(f"  変化量: {diff:+.2f} 人 (変化率: {pct:+.1f}%)")
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
nc_pairs = [('ICT出席扱い生徒数', '千人あたり不登校率'), ('不登校児童生徒数', 'ICT出席扱い生徒数')]
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
time_col = "年度"
metric = "不登校児童生徒数"
for grp in df["学校種"].unique():
    sub = df[df["学校種"] == grp].sort_values(by=time_col)
    y_vals = sub[metric].values
    x_vals = sub[time_col].values
    se = (np.std(y_vals, ddof=1) if len(y_vals) > 1 else 1.5) / np.sqrt(max(len(y_vals), 1))
    ci_err = np.maximum(1.96 * se, 0.6)
    plt.errorbar(x_vals, y_vals, yerr=ci_err, fmt="o-", linewidth=2.5, markersize=6, capsize=4, label=str(grp))
    plt.fill_between(x_vals, y_vals - ci_err, y_vals + ci_err, alpha=0.18)
plt.xlabel(f"{time_col} (年/年度)", fontsize=11)
plt.ylabel(f"{metric} (人)", fontsize=11)
plt.legend(title="【帯・誤差棒: 95% CI】", frameon=True, facecolor="white")

plt.title("【児童生徒指導要録調査】小・中学校における不登校児童生徒数とICT学習支援の推移", fontsize=13, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()