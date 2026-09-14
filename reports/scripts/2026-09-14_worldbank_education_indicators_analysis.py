"""
【世界銀行 EdStats】世界各国の数学的習熟度と公的教育支出・デジタル普及率の相関分析
オープンデータ統計分析・可視化再現スクリプト
データ提供元: World Bank Open Data (World Development Indicators & EdStats) (https://databank.worldbank.org/source/education-statistics-%5eedstats%5e)
"""
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

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
        print(f"  平均値: {s.mean():.2f} % / 指標値")
        print(f"  中央値: {s.median():.2f} % / 指標値")
        print(f"  標準偏差: {s.std(ddof=1):.2f}")
        print(f"  最小値: {s.min():.2f} / 最大値: {s.max():.2f}")
        print(f"  四分位範囲 (IQR): {iqr:.2f}")

# ==============================================================================
# 3. 経年変化トレンド・線形回帰分析 (決定係数 R²)
# ==============================================================================
time_col = "年"
if time_col and time_col in df.columns:
    print("\n==================================================")
    print("📈 経年トレンド線形回帰分析")
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
                start_v, end_v = y_vals.iloc[0], y_vals.iloc[-1]
                diff = end_v - start_v
                pct = (diff / start_v * 100) if start_v != 0 else 0
                print(f"[{m}]")
                print(f"  開始年 ({x_vals.iloc[0]}) -> 最新年 ({x_vals.iloc[-1]}): {start_v:.2f} -> {end_v:.2f}")
                print(f"  変化量: {diff:+.2f} % / 指標値 (変化率: {pct:+.1f}%)")
                print(f"  回帰の傾き: {res.slope:.3f} / 決定係数 (R²): {r_sq:.3f} / p値: {res.pvalue:.4f}")

# ==============================================================================
# 4. 相関分析 (ピアソン相関係数 r)
# ==============================================================================
if len(metrics) >= 2:
    print("\n==================================================")
    print("🔍 指標間の相関分析")
    print("==================================================")
    for i in range(len(metrics)):
        for j in range(i + 1, len(metrics)):
            col_x, col_y = metrics[i], metrics[j]
            if col_x in df.columns and col_y in df.columns:
                sub = df[[col_x, col_y]].dropna()
                if len(sub) >= 3:
                    r, p = stats.pearsonr(sub[col_x], sub[col_y])
                    print(f"{col_x} × {col_y}: 相関係数 r = {r:.3f}, p値 = {p:.4f}")

# ==============================================================================
# 5. データの可視化・グラフ生成
# ==============================================================================
plt.figure(figsize=(10, 5.8), dpi=150)
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

# 相関散布図 & 回帰トレンドライン
col_x, col_y = "教育支出対GDP比", "数学最低習熟度達成率"
sns.regplot(x=col_x, y=col_y, data=df, color="#2a9d8f", line_kws={"color": "#e76f51", "linewidth": 2})
plt.xlabel(col_x, fontsize=11)
plt.ylabel(f"{col_y} (% / 指標値)", fontsize=11)

plt.title("【世界銀行 EdStats】世界各国の数学的習熟度と公的教育支出・デジタル普及率の相関分析", fontsize=13, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()