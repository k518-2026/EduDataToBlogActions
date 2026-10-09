# 毎日1本の論文づくり（手順書）

この手順書は、定期タスクが毎日1回実行する。前の会話の記憶はないので、**この手順書とリポジトリのファイルだけで**進める。
作業フォルダ: `E:\ClaudeCode\src\pipeline\EduDataToBlogActions`（以下「リポジトリ」）。日付は Asia/Tokyo。

## 守ること（先に読む）
- 作る物は論文1本（ショートレター、**4ページ**、内容の量で約5,000字）と、その査読報告書。WPへの投稿・送信はしない。WP の設定にも触れない。
- 保存先は `E:\ClaudeCode\` 配下のみ。C: / D: に書かない。`E:\GoogleAntigravity\` は触らない。
- 数値は、`data/catalog/` の検証済みデータから作った事実ファイル（`temp/facts_<dataset>.json`）にあるものだけ。記憶で数値を補わない。
- 文献は、`data/references_verified.json` に登録された実在確認済みのものだけ。新しい文献は、手順 2a を通してから足す。
- 書き込みに、シェルの heredoc を使わない（バックスラッシュが壊れる）。ファイルは Write / Edit ツールで書く。
- 失敗したら、中途半端な物を push しない。題材を `failed`（理由つき）にして、報告して終わる。
- モデルの役割: **下書きは Ollama（gemma4:12b）、校正と査読は Sonnet**（Agent ツールの `model` で指定する）。Ollama が使えないときだけ、論文を Opus に書かせる。

## 手順
1. **題材を選ぶ** `queue/topics.json` の `topics` のうち、最初の `status: "todo"` を選ぶ。なければ「題材が尽きました。新しい検証済みデータが必要です」と報告して終わる。`note` を読む。
2. **前準備**
   - 2a. 参考文献が8本に足りない題材（`note` に書いてある）は、先に文献を足す。候補を Crossref（`https://api.crossref.org/works?query.bibliographic=…`）で検索し、**題名・著者・雑誌・巻号・頁が一致する**ものだけを選ぶ（題名に副題がある場合は、確かな範囲で書く）。`data/references_verified.json` に `{reference, evidence（Crossref DOI）, datasets}` を足し、`src/academic_contexts.py` の該当データセットの `curated_references` に同じ文字列を足す。書式は既存の行（例: `SHEN, C. and TAM, H. P. (2008) …, <b>14</b> (1) ：87-100.`）に合わせる。足したら `python -m pytest -q tests/test_academic_citations.py` が通ることを確かめる。内容に自信のない文献は足さない（7本でもよい）。
   - 2b. `python -m tools.make_facts <dataset_id> <angle_id>` で事実ファイルを、`python -m tools.make_brief <dataset_id> <angle_id>` で指示書を作る（`temp/brief_<dataset_id>.md` と `temp/review_brief_<dataset_id>.md`）。**事実ファイルは、必ずその日の角度で作り直す**（同じ題材の別の角度の事実ファイルが残っていることがある）。事実ファイルを読み、研究課題に足りない数値があれば、`tools/make_facts.py` に足す（元データだけから計算する）。
3. **下書き（Ollama）→ 校正（Claude）**（2026-10-09 の比較実験にもとづく。Opus が全文を書くより Claude の使用量が少ない）
   - 3a. **下書き** `python -m tools.ollama_paper <dataset_id> <angle_id> gemma4:12b`（既定の接続先 `http://192.168.128.62:11434`。2〜4分かかる。出力は `temp/ollama_cmp/gemma4_12b__<dataset_id>.json`）。標準出力の `json_ok` が `true` でなければ1回だけやり直す。接続できない・2回続けて失敗したときは、**下の「Opus で書く場合」に切り替える**（その日の報告に書く）。
   - 3b. **校正の指示書** `python -m tools.make_proof_brief <dataset_id> <angle_id>`（出力は `temp/proof_brief_<dataset_id>.md`）。
   - 3c. **校正（Sonnet）** Agent ツール（`model: "sonnet"`、`subagent_type: "general-purpose"`）に、「`temp/proof_brief_<dataset_id>.md` を最初から最後まで読み、指示どおりに下書きを校正してください。ファイルは Write ツールで書き、heredoc は使わないこと」と頼む。出力は `temp/draft_<dataset_id>.json`（以降は Claude が書いた場合と同じ手順）と、変更の記録 `temp/proof_changes_<dataset_id>.json`。
   - 3d. 校正の報告にある「直せなかった点」を読む。**校正後にも誤りが1つ残ることがある**（実験では、「日本と同じ値の国はない」という誤りが残った）。手順4・6で、元データから自分でも確かめる。
   - **Opus で書く場合**（Ollama が使えないときの代替）: `python -m tools.make_brief` で `temp/brief_<dataset_id>.md` を作り、Agent ツール（`model: "opus"`）に「`temp/brief_<dataset_id>.md` を最初から最後まで読み、指示どおりに論文を書いてください」と頼む。出力は `temp/draft_<dataset_id>.json`。
4. **数値の検査** `python -m tools.check_numbers temp/draft_<dataset_id>.json temp/facts_<dataset_id>.json`。「未照合」は、元データ `data/catalog/<dataset_id>.json` から自分で2通りの方法で計算して確かめる。正しければそのまま、違えば本文を直す。
5. **査読（Sonnet）** Agent ツール（`model: "sonnet"`）に、「`temp/review_brief_<dataset_id>.md` を読み、指示どおりに査読報告書を書いてください」と頼む。出力は `temp/review_<dataset_id>.json`。
6. **査読の点検と本文の修正** 査読を読む。査読が自分で計算した値は、**自分でも再計算して確かめる**（過去に査読の誤りがあった）。正しい指摘は本文に反映する（`temp/draft_<dataset_id>.json` を直す）。誤りの指摘は、`temp/review_<dataset_id>.json` から直す。本文を直したら手順4をやり直す。
7. **まとめる** `python -m tools.merge_draft <dataset_id> <angle_id> <番号>`（番号は `queue/` の既存の番号の最大＋1、2桁）。参考文献が引用から作られ、`queue/<番号>_<dataset_id>.generation.json` ができる。参考文献の数（8本前後）を確かめる。
8. **PDFを作る** `python -m src.main --dry-run --dataset <dataset_id> --angle <angle_id> --reuse queue/<番号>_<dataset_id>.generation.json`。
   - `reports/pdf/<日付>_<dataset_id>_paper.pdf` が**4ページ**であることを、`python -c "from pypdf import PdfReader; print(len(PdfReader(r'…').pages))"` で確かめる。5ページなら、本文を短くして（手順3の執筆担当に `SendMessage` で頼むか、自分で直す）やり直す。
   - `PermissionError`（PDFが開かれている）が出たら、20秒待って再実行する。続くなら、そのままにして報告に書く。
   - 図（`reports/assets/<日付>_chart_*.png`）を開いて、読めるか確かめる。
9. **キューに入れる** `queue/index.json` の `items` に、`{"id": "<番号>_<dataset_id>", "dataset_id", "angle_id", "file", "title", "status": "ready", "prepared_on": "<日付>", "drafted_by": "ollama-gemma4:12b+sonnet-proof" または "opus"}` を足す。`queue/topics.json` の題材を `done`（`done_on`: 日付）にする。
10. **検査して push** `python -m pytest -q tests` が通ることを確かめる。`git add queue reports data src tests tools` → `git commit`（メッセージ末尾に `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`）→ `git push origin HEAD`。`git fetch` のあと `git log --oneline -1 origin/main` で、push が届いたことを確かめる。
11. **記録** `E:\ClaudeCode\data\Obsidian Vault\Claude作業内容\セッション記録 <日付>-EduData.md` に、題材、査読で直した点、誤りの発見、ページ数を数行で追記する（既存の記述は消さない。末尾に足すだけ）。
12. **報告** 題材、文献の数、ページ数、査読の判定、直した点、未解決の点を、日本語で簡潔に報告する。

## 品質の基準（精度は少しずつ上げる）
- ショートレターとして、因果を断定せず、数値が元データと一致し、限界が書かれていればよい。
- 小さい区分・少人数の群に依存した強調をしない。時点が少ない時系列では、相関を主な結果にしない。標準誤差がないときは「有意」と書かない。
- 生の Ollama の下書きに多い誤り（校正で必ず点検する）: 最上級（「最も低い」）が順位と合わない、方法と結果の矛盾、結果にない主張を抄録に書く、他の題材の文献を引用する、実施していない確認を方法に書く。
- 過去に査読で見つかった誤り: 小さい区分（564人）に依存した強調、査読側の再計算の誤り、グラフに誤差棒（反復観測がないのに付けていた）、相関表の自由度の誤り。
