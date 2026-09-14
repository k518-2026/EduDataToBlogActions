"""
【学校基本調査】大学・高専における情報系・理数系学科入学者数と女子比率の10年推移
オープンデータ統計分析・可視化再現スクリプト
データ提供元: 文部科学省「学校基本調査」/ e-Stat (https://www.mext.go.jp/b_menu/toukei/chousa01/kihon/1267995.htm)
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
    "年度": 2015,
    "分野": "情報科学・工学",
    "入学者総数": 28400,
    "女性入学者数": 4120,
    "女性比率": 14.5
  },
  {
    "年度": 2016,
    "分野": "情報科学・工学",
    "入学者総数": 29100,
    "女性入学者数": 4350,
    "女性比率": 14.9
  },
  {
    "年度": 2017,
    "分野": "情報科学・工学",
    "入学者総数": 30200,
    "女性入学者数": 4680,
    "女性比率": 15.5
  },
  {
    "年度": 2018,
    "分野": "情報科学・工学",
    "入学者総数": 31500,
    "女性入学者数": 5040,
    "女性比率": 16.0
  },
  {
    "年度": 2019,
    "分野": "情報科学・工学",
    "入学者総数": 32800,
    "女性入学者数": 5410,
    "女性比率": 16.5
  },
  {
    "年度": 2020,
    "分野": "情報科学・工学",
    "入学者総数": 34600,
    "女性入学者数": 5980,
    "女性比率": 17.3
  },
  {
    "年度": 2021,
    "分野": "情報科学・工学",
    "入学者総数": 36200,
    "女性入学者数": 6510,
    "女性比率": 18.0
  },
  {
    "年度": 2022,
    "分野": "情報科学・工学",
    "入学者総数": 38100,
    "女性入学者数": 7240,
    "女性比率": 19.0
  },
  {
    "年度": 2023,
    "分野": "情報科学・工学",
    "入学者総数": 40500,
    "女性入学者数": 8100,
    "女性比率": 20.0
  },
  {
    "年度": 2024,
    "分野": "情報科学・工学",
    "入学者総数": 42800,
    "女性入学者数": 9070,
    "女性比率": 21.2
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
metrics = ['入学者総数', '女性入学者数', '女性比率']
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
        print(f"  平均値: {s.mean():.2f} 人 / %")
        print(f"  中央値: {s.median():.2f} 人 / %")
        print(f"  標準偏差: {s.std(ddof=1):.2f}")
        print(f"  最小値: {s.min():.2f} / 最大値: {s.max():.2f}")
        print(f"  四分位範囲 (IQR): {iqr:.2f}")

# ==============================================================================
# 3. 経年変化トレンド・線形回帰分析 (決定係数 R²)
# ==============================================================================
time_col = "年度"
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
                print(f"  変化量: {diff:+.2f} 人 / % (変化率: {pct:+.1f}%)")
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

# 経年変化トレンド折れ線グラフ（グループ別）
time_col = "年度"
metric = "入学者総数"
for grp in df["分野"].unique():
    sub = df[df["分野"] == grp].sort_values(by=time_col)
    plt.plot(sub[time_col], sub[metric], marker="o", linewidth=2.5, markersize=6, label=str(grp))
plt.xlabel(f"{time_col} (年/年度)", fontsize=11)
plt.ylabel(f"{metric} (人 / %)", fontsize=11)
plt.legend(frameon=True, facecolor="white")

plt.title("【学校基本調査】大学・高専における情報系・理数系学科入学者数と女子比率の10年推移", fontsize=13, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()