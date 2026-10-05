# 公表元のデータ（原本）

`data/catalog/` の 12 本のうち、公表元から取り込んだものの原本と、作り方をここにまとめます。
**どのデータも、公表された表の値を転記または機械的に取り込んだものです。** 値を作ったり、補ったりしていません。
作るスクリプトは `tools/build_*.py`、照合のテストは `tests/test_catalog_from_source.py` です。

| データ | 作るスクリプト | 原本 |
|---|---|---|
| 不登校・World Bank | （手入力。経年表・API の値） | `docs/DATA_VERIFICATION_2026-10-05.md` |
| PISA・TIMSS | `python -m tools.build_pisa_timss_catalog` | 下の「PISA」「TIMSS」 |
| 教員勤務実態調査 | `python -m tools.build_workload_catalog` | `mext/20240404-mxt_zaimu01-100003067-1.pdf`（画像で読んだ表の転記） |
| 教育の情報化（ICT環境） | `python -m tools.build_ict_catalog` | `mext/ict_r5_gaiyo.pdf`（グラフの値の転記） |
| 高校情報科の担当教員 | `python -m tools.build_info_teachers_catalog` | `mext/info_teachers_r4.pdf` |
| 通級による指導 | `python -m tools.build_tokkyu_catalog` | `mext/tokkyu_r4.pdf` |
| TIMSS 2023 の意識 | `python -m tools.build_timss_attitudes_catalog` | `timss2023_*.xlsx`（下の「TIMSS 2023 の意識」） |
| TALIS 2024 | `python -m tools.build_talis_catalog` | `talis2024_vol1_statlink_n0x63b.xlsx` ほか |
| UNESCO（ICTスキル） | `python -m tools.build_unesco_catalog [--fetch]` | `uis_ictskill_2021.json` |
| 関係学科別 大学入学者 | `python -m tools.build_enrollment_catalog` | `estat/*.xlsx` |
| 全国学力・学習状況調査 | `python -m tools.build_national_assessment_catalog` | `mext/nat_assess_extract.txt` |

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

## TIMSS 2023 の意識（国別の横断データ）

2026-10-06 に `timss2023_student_attitudes` として作った（Exhibit 6.2.2〜6.2.8 は 2023 年の 1 回分で経年の表がないため、国別の横断分析）。

| ファイル | 取得元 |
|---|---|
| `timss2023_6-2-1-3_con-stu-slm.xlsx` | https://timss2023.org/wp-content/uploads/2024/10/6-2-1-3_con-stu-slm.xlsx（好き。小4・中2） |
| `timss2023_6-2-4-6_con-stu-scm.xlsx` | https://timss2023.org/wp-content/uploads/2025/01/6-2-4-6_con-stu-scm.xlsx（自信。小4・中2） |
| `timss2023_6-2-7-8_con-stu-svm.xlsx` | https://timss2023.org/wp-content/uploads/2024/11/6-2-7-8_con-stu-svm.xlsx（価値。中2のみ） |
| `timss2023_1-1-1_ach-g4m-dist.xlsx` | https://timss2023.org/wp-content/uploads/2024/11/1-1-1_ach-g4m-dist.xlsx（小4 算数の平均得点） |
| `timss2023_1-2-1_ach-g8m-dist.xlsx` | https://timss2023.org/wp-content/uploads/2024/11/1-2-1_ach-g8m-dist.xlsx（中2 数学の平均得点） |

## 文部科学省の PDF（`mext/`）

取得日 2026-10-05。PDF はテキスト層が壊れているもの（日本語が文字化け）や、表が画像に近いものがあり、
ページを画像にして読み、スクリプトの中の表（SERIES など）に転記した。転記の検査はスクリプトの中にある。

| ファイル | 取得元 |
|---|---|
| `20240404-mxt_zaimu01-100003067-1.pdf` | https://www.mext.go.jp/content/20240404-mxt_zaimu01-100003067-1.pdf（教員勤務実態調査（令和4年度）集計【確定値】（概要）） |
| `ict_r5_gaiyo.pdf` | https://www.mext.go.jp/content/20241031-mxt_jogai02-000037398_01.pdf（令和5年度 学校における教育の情報化の実態等に関する調査結果（概要）【確定値】） |
| `info_teachers_r4.pdf` | https://www.mext.go.jp/content/20221108-mxt_jogai02-000021518_001.pdf（高等学校情報科担当教員の配置状況及び指導体制の充実に向けて、令和4年11月） |
| `tokkyu_r4.pdf` | https://www.mext.go.jp/content/20241107-mxt_tokubetu02-000032436_2.pdf（令和4年度通級による指導実施状況調査結果） |
| `nat_assess_extract.txt` | 全国学力・学習状況調査の結果（概要）。令和元年度 https://www.nier.go.jp/19chousakekkahoukoku/19summary.pdf 、令和3年度 .../21chousakekkahoukoku/21summary.pdf 、令和4年度 .../22chousakekkahoukoku/22summary.pdf 、令和5年度 .../23chousakekkahoukoku/report/data/23summary.pdf 、令和6年度 .../24chousakekkahoukoku/report/data/24summary.pdf 、令和7年度 https://www.mext.go.jp/content/20251017-mxt_kyoiku01-000045415_12.pdf の3ページ（概要のポイント。画像で確認）。PDF は容量が大きいため保存せず、該当行の抜き書きだけを保存した |

## TALIS 2024（OECD）

『Results from TALIS 2024: The State of Teaching』（2025-10-07 公開）。

| ファイル | 取得元 |
|---|---|
| `talis2024_vol1_statlink_n0x63b.xlsx` | https://stat.link/files/90df6235-en/n0x63b.xlsx（第1章の統計表 Table 1.1〜1.63。2025-12-10 更新） |
| `talis2024_country_note_japan.pdf` | https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/10/results-from-talis-2024-country-notes_eafd703e/japan_4e66c75b/b48b1dd7-en.pdf（日本の国別ノート。AI利用17%などの検算に使った） |

OECD の Web ページは自動取得を拒否するため、StatLink の Excel は、ブラウザで章のページを開いて StatLink のコードを調べ、
`https://stat.link/files/90df6235-en/<コード>.xlsx` の形で取得した。第3章（`0tgheo`）と第4章（`9pg1y4`）の図のデータにも
労働時間・協働に関する値があるが、列の意味を確認できなかったため使っていない。

## UNESCO 統計研究所（UIS）

`uis_ictskill_2021.json` は、UIS の Data API（データ版 20260507-91260335）から、指標 ICTSKILLPCPR・ICTSKILLARSP・ICTSKILLEPRS と
それぞれの女性（.F）・男性（.M）の 2021 年の値を取得して保存したもの。取り直すには `python -m tools.build_unesco_catalog --fetch`。
URL は JSON の `url` に記録している。

## e-Stat（学校基本調査）

`estat/` は、政府統計の総合窓口 e-Stat から取得した『関係学科別 大学入学状況』（表番号15）。
https://www.e-stat.go.jp/stat-search/file-download?statInfId=<ID>&fileKind=0

| ファイル | 年度 |
|---|---|
| `estat_000040128620.xlsx` | 令和5年度（2023） |
| `estat_000040230323.xlsx` | 令和6年度（2024） |
| `estat_000040392734.xlsx` | 令和7年度（2025） |
