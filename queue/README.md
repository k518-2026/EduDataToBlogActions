# 投稿キュー

校正済みの論文（本文・査読報告書）を，ここに蓄積し，2日に1本ずつ投稿する。

- `index.json` … 投稿の順番と状態。`status` は `ready`（待ち）／`hold`（保留）／`posted`（投稿済み）。`min_interval_days` が投稿の間隔（日）。
- `NN_<dataset>.generation.json` … 論文（`paper`），査読報告書（`review`），記事の本文（`insights`）。**直したいときはこの JSON を直す。**
- 投稿は `python -m src.main --from-queue`。待ちがない，または前回の投稿から間隔が足りないときは何もしない。
  投稿の日付・図・PDF・分析コードは，投稿のときに作り直される（日付は投稿日）。
- 数値は `data/catalog/` の検証済みデータだけから取る。新しい数値や文献を足すときは，`data/references_verified.json` と `src/academic_contexts.py` にも登録する。

## 論文を増やす手順（2026-10-06 の試走で確立）
1. `python -m tools.make_facts <dataset_id> <angle_id>` で、使ってよい数値の一覧（`temp/facts_<dataset_id>.json`）を作る。
2. 執筆担当（Opus）が、事実ファイルと文献表だけを根拠に、論文と記事本文を書く。字数は6項目の合計で約5,000字（4ページ）。
3. `python -m tools.check_numbers <生成JSON> <事実ファイル>` で、本文の数値が事実ファイルにあるかを検査する。未照合は元データで手計算して確かめる。
4. 査読担当（Sonnet）が、数値を元データで確かめながら査読報告書を書く。査読の指摘で本文を直し、査読自体の誤りも点検する（今回は査読の「r=.09」が誤りで、執筆側の計算の -.02 が正しかった）。
5. `--reuse` で PDF・図・コードを作り、4ページか確認して、`index.json` に `hold` で入れる。利用者が読んで `ready` にする。
