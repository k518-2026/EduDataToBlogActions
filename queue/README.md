# 投稿キュー

校正済みの論文（本文・査読報告書）を，ここに蓄積し，2日に1本ずつ投稿する。

- `index.json` … 投稿の順番と状態。`status` は `ready`（待ち）／`hold`（保留）／`posted`（投稿済み）。`min_interval_days` が投稿の間隔（日）。
- `NN_<dataset>.generation.json` … 論文（`paper`），査読報告書（`review`），記事の本文（`insights`）。**直したいときはこの JSON を直す。**
- 投稿は `python -m src.main --from-queue`。待ちがない，または前回の投稿から間隔が足りないときは何もしない。
  投稿の日付・図・PDF・分析コードは，投稿のときに作り直される（日付は投稿日）。
- 数値は `data/catalog/` の検証済みデータだけから取る。新しい数値や文献を足すときは，`data/references_verified.json` と `src/academic_contexts.py` にも登録する。
