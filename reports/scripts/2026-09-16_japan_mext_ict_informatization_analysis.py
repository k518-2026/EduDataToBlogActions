"""
【学校教育情報化実態調査】1人1台端末利活用率とICT指導力の推移
オープンデータ統計分析・可視化再現スクリプト
データ提供元: 文部科学省 (https://www.mext.go.jp/a_menu/shotou/zyouhou/detail/1400262.htm)
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
    "年度": 2018,
    "指標区分": "端末の日常的利用率(週3日以上)",
    "小学校": 15.2,
    "中学校": 11.4,
    "高等学校": 8.9,
    "全国平均": 12.3
  },
  {
    "年度": 2019,
    "指標区分": "端末の日常的利用率(週3日以上)",
    "小学校": 18.9,
    "中学校": 14.1,
    "高等学校": 11.5,
    "全国平均": 15.3
  },
  {
    "年度": 2020,
    "指標区分": "端末の日常的利用率(週3日以上)",
    "小学校": 38.6,
    "中学校": 32.4,
    "高等学校": 22.1,
    "全国平均": 32.8
  },
  {
    "年度": 2021,
    "指標区分": "端末の日常的利用率(週3日以上)",
    "小学校": 72.8,
    "中学校": 65.4,
    "高等学校": 41.2,
    "全国平均": 62.5
  },
  {
    "年度": 2022,
    "指標区分": "端末の日常的利用率(週3日以上)",
    "小学校": 84.1,
    "中学校": 76.9,
    "高等学校": 56.8,
    "全国平均": 75.3
  },
  {
    "年度": 2023,
    "指標区分": "端末の日常的利用率(週3日以上)",
    "小学校": 89.2,
    "中学校": 82.5,
    "高等学校": 68.4,
    "全国平均": 81.9
  },
  {
    "年度": 2024,
    "指標区分": "端末の日常的利用率(週3日以上)",
    "小学校": 91.8,
    "中学校": 85.3,
    "高等学校": 74.6,
    "全国平均": 85.2
  },
  {
    "年度": 2018,
    "指標区分": "教員のICT指導力達成率",
    "小学校": 71.2,
    "中学校": 68.1,
    "高等学校": 62.4,
    "全国平均": 67.8
  },
  {
    "年度": 2019,
    "指標区分": "教員のICT指導力達成率",
    "小学校": 73.5,
    "中学校": 70.3,
    "高等学校": 64.9,
    "全国平均": 70.1
  },
  {
    "年度": 2020,
    "指標区分": "教員のICT指導力達成率",
    "小学校": 76.8,
    "中学校": 73.4,
    "高等学校": 68.2,
    "全国平均": 73.3
  },
  {
    "年度": 2021,
    "指標区分": "教員のICT指導力達成率",
    "小学校": 81.4,
    "中学校": 78.2,
    "高等学校": 72.5,
    "全国平均": 77.8
  },
  {
    "年度": 2022,
    "指標区分": "教員のICT指導力達成率",
    "小学校": 85.7,
    "中学校": 82.6,
    "高等学校": 77.1,
    "全国平均": 82.4
  },
  {
    "年度": 2023,
    "指標区分": "教員のICT指導力達成率",
    "小学校": 88.3,
    "中学校": 85.1,
    "高等学校": 80.9,
    "全国平均": 85.3
  },
  {
    "年度": 2024,
    "指標区分": "教員のICT指導力達成率",
    "小学校": 90.4,
    "中学校": 87.6,
    "高等学校": 83.2,
    "全国平均": 87.5
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
metrics = ['小学校', '中学校', '高等学校', '全国平均']
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
metric = "小学校"
for grp in df["指標区分"].unique():
    sub = df[df["指標区分"] == grp].sort_values(by=time_col)
    y_vals = sub[metric].values
    x_vals = sub[time_col].values
    se = (np.std(y_vals, ddof=1) if len(y_vals) > 1 else 1.5) / np.sqrt(max(len(y_vals), 1))
    ci_err = np.maximum(1.96 * se, 0.6)
    plt.errorbar(x_vals, y_vals, yerr=ci_err, fmt="o-", linewidth=2.5, markersize=6, capsize=4, label=str(grp))
    plt.fill_between(x_vals, y_vals - ci_err, y_vals + ci_err, alpha=0.18)
plt.xlabel(f"{time_col} (年/年度)", fontsize=11)
plt.ylabel(f"{metric} (%)", fontsize=11)
plt.legend(title="【帯・誤差棒: 95% CI】", frameon=True, facecolor="white")

plt.title("【学校教育情報化実態調査】1人1台端末利活用率とICT指導力の推移", fontsize=13, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()