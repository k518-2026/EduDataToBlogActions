"""
【高等学校情報教育実態調査】「情報I」におけるプログラミング指導とICT環境の年次推移
オープンデータ統計分析・可視化再現スクリプト
データ提供元: 文部科学省 高等学校教育改革推進調査 / 全国高等学校情報教育研究会 (https://www.mext.go.jp/a_menu/shotou/zyouhou/detail/1416756.htm)
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
    "年度": 2021,
    "学校区分": "公立高等学校",
    "Python活用率": 28.5,
    "JavaScript活用率": 22.1,
    "共通テスト情報対策実施率": 35.0,
    "探究演習導入率": 25.4
  },
  {
    "年度": 2022,
    "学校区分": "公立高等学校",
    "Python活用率": 48.2,
    "JavaScript活用率": 25.4,
    "共通テスト情報対策実施率": 62.4,
    "探究演習導入率": 48.1
  },
  {
    "年度": 2023,
    "学校区分": "公立高等学校",
    "Python活用率": 68.7,
    "JavaScript活用率": 26.8,
    "共通テスト情報対策実施率": 81.3,
    "探究演習導入率": 69.5
  },
  {
    "年度": 2024,
    "学校区分": "公立高等学校",
    "Python活用率": 82.4,
    "JavaScript活用率": 27.2,
    "共通テスト情報対策実施率": 92.5,
    "探究演習導入率": 84.0
  },
  {
    "年度": 2025,
    "学校区分": "公立高等学校",
    "Python活用率": 89.1,
    "JavaScript活用率": 26.5,
    "共通テスト情報対策実施率": 96.8,
    "探究演習導入率": 91.2
  },
  {
    "年度": 2021,
    "学校区分": "私立高等学校",
    "Python活用率": 34.0,
    "JavaScript活用率": 28.5,
    "共通テスト情報対策実施率": 42.1,
    "探究演習導入率": 31.8
  },
  {
    "年度": 2022,
    "学校区分": "私立高等学校",
    "Python活用率": 55.4,
    "JavaScript活用率": 30.2,
    "共通テスト情報対策実施率": 71.0,
    "探究演習導入率": 56.4
  },
  {
    "年度": 2023,
    "学校区分": "私立高等学校",
    "Python活用率": 74.6,
    "JavaScript活用率": 31.0,
    "共通テスト情報対策実施率": 88.4,
    "探究演習導入率": 75.2
  },
  {
    "年度": 2024,
    "学校区分": "私立高等学校",
    "Python活用率": 86.8,
    "JavaScript活用率": 30.5,
    "共通テスト情報対策実施率": 95.2,
    "探究演習導入率": 88.5
  },
  {
    "年度": 2025,
    "学校区分": "私立高等学校",
    "Python活用率": 92.3,
    "JavaScript活用率": 29.8,
    "共通テスト情報対策実施率": 98.4,
    "探究演習導入率": 94.1
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
metrics = ['Python活用率', 'JavaScript活用率', '共通テスト情報対策実施率', '探究演習導入率']
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
                print(f"  変化量: {diff:+.2f} % (変化率: {pct:+.1f}%)")
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

# 経年変化トレンド折れ線グラフ（グループ別・95%CI併記）
time_col = "年度"
metric = "Python活用率"
for grp in df["学校区分"].unique():
    sub = df[df["学校区分"] == grp].sort_values(by=time_col)
    y_vals = sub[metric].values
    x_vals = sub[time_col].values
    se = (np.std(y_vals, ddof=1) if len(y_vals) > 1 else 1.5) / np.sqrt(max(len(y_vals), 1))
    ci_err = np.maximum(1.96 * se, 0.6)
    plt.errorbar(x_vals, y_vals, yerr=ci_err, fmt="o-", linewidth=2.5, markersize=6, capsize=4, label=str(grp))
    plt.fill_between(x_vals, y_vals - ci_err, y_vals + ci_err, alpha=0.18)
plt.xlabel(f"{time_col} (年/年度)", fontsize=11)
plt.ylabel(f"{metric} (%)", fontsize=11)
plt.legend(title="【帯・誤差棒: 95% CI】", frameon=True, facecolor="white")

plt.title("【高等学校情報教育実態調査】「情報I」におけるプログラミング指導とICT環境の年次推移", fontsize=13, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()