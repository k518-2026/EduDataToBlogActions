# ローカル LLM（Ollama）と Claude Code の論文比較（2026-10-09）

## 条件
- 題材: TALIS 2024（oecd_talis_teacher_survey / talis_collaboration_ict）。同じ事実ファイル・同じ指示・同じ見本（別題材の完成版2本）。
- Ollama: `http://192.168.128.62:11434`（v0.40.1）。gemma4:12b と qwen3.5:9b（shosetsu は小説向けなので除外）。1回の生成のみ（JSON モード、think なし、num_ctx 49152、温度 0.3）。
- Claude: `queue/04`（Opus が執筆し、Sonnet の査読を受けて直し、4ページに短縮した完成版）。
- **注意**: Claude 側は「執筆→査読→修正」を経た完成版、Ollama 側は1回で書かせた生の出力。パイプライン全体の比較であり、モデル単体の比較ではない。
- 最初の試行は、見本に同じ題材の Opus の論文が入っていて、gemma が写してしまったため無効にした（`tools/ollama_paper.py` に、同じ題材が見本に入ったら止まる検査を入れた）。2回目は事実ファイルが別の角度のものだったため無効にし、3回目（これ）で揃えた。

## 結果
| | Opus（完成版） | gemma4:12b | qwen3.5:9b |
|---|---|---|---|
| 生成時間 | （サブエージェント、数分） | 211 秒 | 152 秒 |
| 本文の文字数 | 4,284 | 2,478 | 2,676 |
| 事実ファイルにない数値 | 4（手計算で確認済み：除外後の n、信頼区間、ペア数） | 0 | 0 |
| 匿名の採点（Sonnet、10点満点）：正確さ／深さ／慎重さ／総合 | 9／9／9／9 | 9／4／8／6 | 5／3／6／3 |
| 事実の誤り | なし | 軽微（「アルバルタ州」の誤記） | 6（日本のAI利用を「最も低い」と3か所で誤記。実際は53番目、最低はフランス）ほか |
| 引用 | 9本（解釈とつながる） | 6本（半分は飾り） | 5本 |
| 頑健性・多重比較 | 除外確認、ボンフェローニ | 一文のみ | 方法に書いたが実施していない |
| 4ページ | ○ | ○（短くて余る） | ○（同） |

匿名採点の順位: Opus > gemma4 > qwen3.5。

## 読み取り
- 数値の書式と因果の慎重さは、gemma4 は守れた。qwen3.5 は最上級の誤り、結果に書いていない相関の主張、方法と結果の矛盾があった。
- 差が出たのは「深さ」。Ollama の2つは、日本の位置と RQ2 の r を述べるだけで、AI利用が自信よりも少人数グループの指導と強く関連する、という対照や、除外による頑健性の確認がない。
- ローカルは速く、費用もかからないが、単独では公表用の水準に届かない。使うなら、下書き（骨格づくり）に使い、数値の検査（`tools/check_numbers.py`）と Claude の査読・修正を通す。qwen3.5:9b は論文には向かない。
- これは1題材・1回の生成での比較。ばらつきは調べていない。

## 再現
```
python -m tools.make_facts oecd_talis_teacher_survey talis_collaboration_ict
python -m tools.make_brief oecd_talis_teacher_survey talis_collaboration_ict
python -m tools.ollama_paper oecd_talis_teacher_survey talis_collaboration_ict gemma4:12b
python -m tools.compare_papers oecd_talis_teacher_survey talis_collaboration_ict "Opus=queue/04_…json" "gemma4=temp/ollama_cmp/gemma4_12b__….json"
```
