"""
【OECD PISA】主要国の数学的リテラシー得点推移とデジタル機器活用状況の国際比較
オープンデータ統計分析・可視化再現スクリプト
データ提供元: OECD (Organisation for Economic Co-operation and Development) PISA Database (https://www.oecd.org/pisa/)
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
    "調査年": 2003,
    "国・地域": "日本",
    "数学得点": 534,
    "男子得点": 539,
    "女子得点": 529,
    "男女得点差": 10
  },
  {
    "調査年": 2006,
    "国・地域": "日本",
    "数学得点": 523,
    "男子得点": 531,
    "女子得点": 515,
    "男女得点差": 16
  },
  {
    "調査年": 2009,
    "国・地域": "日本",
    "数学得点": 529,
    "男子得点": 534,
    "女子得点": 524,
    "男女得点差": 10
  },
  {
    "調査年": 2012,
    "国・地域": "日本",
    "数学得点": 536,
    "男子得点": 545,
    "女子得点": 527,
    "男女得点差": 18
  },
  {
    "調査年": 2015,
    "国・地域": "日本",
    "数学得点": 532,
    "男子得点": 539,
    "女子得点": 525,
    "男女得点差": 14
  },
  {
    "調査年": 2018,
    "国・地域": "日本",
    "数学得点": 527,
    "男子得点": 532,
    "女子得点": 522,
    "男女得点差": 10
  },
  {
    "調査年": 2022,
    "国・地域": "日本",
    "数学得点": 536,
    "男子得点": 541,
    "女子得点": 531,
    "男女得点差": 10
  },
  {
    "調査年": 2022,
    "国・地域": "シンガポール",
    "数学得点": 575,
    "男子得点": 580,
    "女子得点": 570,
    "男女得点差": 10
  },
  {
    "調査年": 2022,
    "国・地域": "韓国",
    "数学得点": 527,
    "男子得点": 532,
    "女子得点": 522,
    "男女得点差": 10
  },
  {
    "調査年": 2022,
    "国・地域": "エストニア",
    "数学得点": 510,
    "男子得点": 512,
    "女子得点": 508,
    "男女得点差": 4
  },
  {
    "調査年": 2022,
    "国・地域": "カナダ",
    "数学得点": 497,
    "男子得点": 501,
    "女子得点": 493,
    "男女得点差": 8
  },
  {
    "調査年": 2022,
    "国・地域": "イギリス",
    "数学得点": 489,
    "男子得点": 494,
    "女子得点": 484,
    "男女得点差": 10
  },
  {
    "調査年": 2022,
    "国・地域": "アメリカ",
    "数学得点": 465,
    "男子得点": 472,
    "女子得点": 458,
    "男女得点差": 14
  },
  {
    "調査年": 2022,
    "国・地域": "OECD平均",
    "数学得点": 472,
    "男子得点": 477,
    "女子得点": 468,
    "男女得点差": 9
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
metrics = ['数学得点', '男子得点', '女子得点', '男女得点差']
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
        print(f"  平均値: {s.mean():.2f} Score (点)")
        print(f"  中央値: {s.median():.2f} Score (点)")
        print(f"  標準偏差: {s.std(ddof=1):.2f}")
        print(f"  最小値: {s.min():.2f} / 最大値: {s.max():.2f}")
        print(f"  四分位範囲 (IQR): {iqr:.2f}")

# ==============================================================================
# 3. 経年変化トレンド・線形回帰分析 (決定係数 R²)
# ==============================================================================
time_col = "調査年"
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
                print(f"  変化量: {diff:+.2f} Score (点) (変化率: {pct:+.1f}%)")
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
time_col = "調査年"
metric = "数学得点"
for grp in df["国・地域"].unique():
    sub = df[df["国・地域"] == grp].sort_values(by=time_col)
    plt.plot(sub[time_col], sub[metric], marker="o", linewidth=2.5, markersize=6, label=str(grp))
plt.xlabel(f"{time_col} (年/年度)", fontsize=11)
plt.ylabel(f"{metric} (Score (点))", fontsize=11)
plt.legend(frameon=True, facecolor="white")

plt.title("【OECD PISA】主要国の数学的リテラシー得点推移とデジタル機器活用状況の国際比較", fontsize=13, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()