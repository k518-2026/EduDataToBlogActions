# LuaLaTeX のソース置き場

論文1本につき1フォルダ（`<番号>_<dataset_id>/`）。ここを消さずに、題材が増えるたびに足していく。

- `paper.tex` … LuaLaTeX のソース（ltjsarticle、A4・2段組、本文10pt、原ノ味角ゴシック）。`lualatex paper.tex` を2回かけると `paper.pdf` ができる。
- `chart_*.png` … `paper.tex` が読む図（欄幅 8.4cm で読める大きさ。`tools/latex_charts.py` が描く）。
- `paper.pdf` … 組んだ PDF。投稿に使う PDF は `queue/pdf/<番号>_<dataset_id>.pdf`（同じ中身）。

## 作り直す

```
python -m tools.build_queue_pdf <番号>_<dataset_id>
```

`queue/<番号>_<dataset_id>.generation.json`（本文・参考文献）と `data/catalog/`（元データ）から、`paper.tex` と図を作り直し、PDF を組む。
本文を直したいときは、`paper.tex` ではなく generation.json を直して作り直す（`paper.tex` は毎回上書きされる）。

## 決まり

- 4ページ以内。1ページ目〜最終ページを画像にして、図の文字、表のはみ出し、参考文献の折り返しを目で確かめる。
- 時点のあるデータ（時系列を重ねた表）は、本文の数値と同じ最新年度の断面で表と図を作る（`tools/latex_paper.py`）。
- 図には題名を入れない（キャプションは LaTeX 側）。日本は赤。
- 数値は generation.json の本文のとおり。`tools/check_numbers.py` で事実ファイルと照合してから組む。
