"""
【世界銀行】教育支出と初等中等数学習熟度の国際比較分析
オープンデータ統計分析・可視化再現スクリプト
データ提供元: 世界銀行（World Bank） (https://databank.worldbank.org/source/education-statistics-%5eedstats%5e)
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
    "年": 2023,
    "国名": "日本",
    "数学最低習熟度達成率": 91.2,
    "教育支出対GDP比": 3.4,
    "インターネット利用率": 93.3
  },
  {
    "年": 2023,
    "国名": "シンガポール",
    "数学最低習熟度達成率": 94.5,
    "教育支出対GDP比": 2.9,
    "インターネット利用率": 92.8
  },
  {
    "年": 2023,
    "国名": "エストニア",
    "数学最低習熟度達成率": 88.7,
    "教育支出対GDP比": 5.8,
    "インターネット利用率": 93.1
  },
  {
    "年": 2023,
    "国名": "韓国",
    "数学最低習熟度達成率": 89.6,
    "教育支出対GDP比": 5.1,
    "インターネット利用率": 97.2
  },
  {
    "年": 2023,
    "国名": "フィンランド",
    "数学最低習熟度達成率": 85.3,
    "教育支出対GDP比": 5.6,
    "インターネット利用率": 96.5
  },
  {
    "年": 2023,
    "国名": "カナダ",
    "数学最低習熟度達成率": 83.1,
    "教育支出対GDP比": 5.2,
    "インターネット利用率": 93.8
  },
  {
    "年": 2023,
    "国名": "イギリス",
    "数学最低習熟度達成率": 80.4,
    "教育支出対GDP比": 4.9,
    "インターネット利用率": 94.8
  },
  {
    "年": 2023,
    "国名": "ドイツ",
    "数学最低習熟度達成率": 78.5,
    "教育支出対GDP比": 4.8,
    "インターネット利用率": 91.5
  },
  {
    "年": 2023,
    "国名": "アメリカ",
    "数学最低習熟度達成率": 73.2,
    "教育支出対GDP比": 5.4,
    "インターネット利用率": 91.8
  },
  {
    "年": 2023,
    "国名": "フランス",
    "数学最低習熟度達成率": 76.8,
    "教育支出対GDP比": 5.2,
    "インターネット利用率": 86.4
  },
  {
    "年": 2023,
    "国名": "オーストラリア",
    "数学最低習熟度達成率": 81.6,
    "教育支出対GDP比": 5.3,
    "インターネット利用率": 91.1
  },
  {
    "年": 2023,
    "国名": "ベトナム",
    "数学最低習熟度達成率": 77.4,
    "教育支出対GDP比": 4.1,
    "インターネット利用率": 78.6
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
metrics = ['数学最低習熟度達成率', '教育支出対GDP比', 'インターネット利用率']
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
        print(f"  平均値: {s.mean():.2f} %")
        print(f"  中央値: {s.median():.2f} %")
        print(f"  標準偏差: {s.std(ddof=1):.2f}")
        print(f"  最小値: {s.min():.2f} / 最大値: {s.max():.2f}")
        print(f"  四分位範囲 (IQR): {iqr:.2f}")

# ==============================================================================
# 3. 経年変化トレンド・線形回帰分析 & ベイズファクター (BF₁₀)
# ==============================================================================
time_col = "年"
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
                print(f"  変化量: {diff:+.2f} % (変化率: {pct:+.1f}%)")
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
# 5. データの可視化・グラフ生成
# ==============================================================================
plt.figure(figsize=(10, 5.8), dpi=150)
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

# 相関散布図 & 回帰トレンドライン（95%CI併記）
col_x, col_y = "教育支出対GDP比", "数学最低習熟度達成率"
sns.regplot(x=col_x, y=col_y, data=df, ci=95, color="#2a9d8f", line_kws={"color": "#e76f51", "linewidth": 2})
plt.xlabel(col_x, fontsize=11)
plt.ylabel(f"{col_y} (%)", fontsize=11)

plt.title("【世界銀行】教育支出と初等中等数学習熟度の国際比較分析", fontsize=13, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()