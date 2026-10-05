# 公表元のデータ（原本）

`data/catalog/` の `oecd_pisa_math_ict.json` と `japan_timss_math_science.json` は、
ここにある Excel から `python -m tools.build_pisa_timss_catalog` で作ります。手入力はしていません。

取得日: 2026-10-05

## PISA（OECD）

『PISA 2025 Results (Volume I)』（OECD、2026-09-08 公開）の StatLink（付表の Excel）。
報告書: https://www.oecd.org/en/publications/pisa-2025-results-volume-i_73451bc5-en.html

| ファイル | 取得元 | 中身 |
|---|---|---|
| `pisa2025_vol1_table_B1.2a_mrq53f.xlsx` | https://stat.link/files/73451bc5-en/mrq53f.xlsx | Table I.B1.2a.38 数学の平均得点 2003〜2025（男女計） |
| `pisa2025_vol1_table_B1.4_68stqn.xlsx` | https://stat.link/files/73451bc5-en/68stqn.xlsx | Table I.B1.2c.29/30/31 女子・男子の数学の平均得点と男女差 2015〜2025 |

- 「OECD average-23」は、2003年から全回に参加した 23 の OECD 加盟国の平均。
- 国名の「*」（Canada*, United States*）は、PISA の標本抽出基準を満たさなかった項目があるという OECD の注意。

## TIMSS（IEA）

『TIMSS 2023 International Results in Mathematics and Science』（IEA / Boston College）の Exhibit。
https://timss2023.org/results/math-achievement/

| ファイル | 取得元 |
|---|---|
| `1-1-10_ach-g4m-trend-table.xlsx` | https://timss2023.org/wp-content/uploads/2024/11/1-1-10_ach-g4m-trend-table.xlsx（小4 平均得点の推移） |
| `1-1-11_ach-g4m-trend-gender.xlsx` | https://timss2023.org/wp-content/uploads/2024/11/1-1-11_ach-g4m-trend-gender.xlsx（小4 女子・男子） |
| `1-2-10_ach-g8m-trend-table.xlsx` | https://timss2023.org/wp-content/uploads/2024/11/1-2-10_ach-g8m-trend-table.xlsx（中2 平均得点の推移） |
| `1-2-11_ach-g8m-trend-gender.xlsx` | https://timss2023.org/wp-content/uploads/2024/11/1-2-11_ach-g8m-trend-gender.xlsx（中2 女子・男子） |

## 使っていないもの

- TIMSS の意識（楽しい・自信・価値）の Exhibit 6.2.2〜6.2.8 は 2023 年の 1 回分の国際比較で、経年の表がない。
  国別の横断分析なら使える（今回は作っていない）。
