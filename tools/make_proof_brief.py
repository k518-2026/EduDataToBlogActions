"""ローカル LLM（Ollama）の下書きを、Claude が校正するための指示書を作る。

    python -m tools.make_proof_brief <dataset_id> <angle_id> [<下書きのJSON>]

下書きの既定: temp/ollama_cmp/gemma4_12b__<dataset_id>.json（tools/ollama_paper.py の出力）。
出力: temp/proof_brief_<dataset_id>.md。校正後は temp/draft_<dataset_id>.json に書かせる（以降の手順は、Claude が書いた場合と同じ）。
temp/brief_<dataset_id>.md（tools/make_brief.py の出力）から、守ること・文献の表を取り出して使う。
"""
import re
import sys
from pathlib import Path

from src.config import BASE_DIR, TEMP_DIR

TEMPLATE = """# 下書きの校正の指示書（ローカルLLMの下書きを Claude が校正する）

あなたは教育統計・教育工学に詳しい校正者です。ローカルの小さな言語モデルが書いた論文の下書き（ショートレター、4ページ）を、**事実と論理を正しく、公表できる水準に**直してください。書き直しすぎず、下書きの良い部分は残します。

## 読む資料
- 下書き: `{draft}`（`paper` と `insights`）
- 事実ファイル（使ってよい数値の全体）: `{facts}`
- 元データ: `{catalog}`
- 見本（完成済みの別題材の論文。水準の目安）: `{ex1}` の `paper`
- 題材: {theme}。研究課題は下書きの objectives にある。

## やること（順に）
1. **数値・順位・最上級を、元データで確かめる。** 順位は「並べ替えて位置を見る」と「それより大きい（小さい）値を数える」の2通りで。相関は2通りの式で。「最も低い」「最も高い」が順位と合っているか、同じ値の項目がないか（同順位）を必ず確かめる。誤りは直す。
2. **論理の誤りを直す。** 方法と結果の矛盾、結果に書かれていない主張を抄録・考察が言っていないか、因果の断定がないか、事実ファイルの「全ペアの探索」を「探索していない」と書いていないか。
3. **足りない内容を補う。** 事実ファイルと元データにある内容だけで、次の観点で足りなければ補う（無理に足さない）。(a) 位置づけ（順位・平均との比較。平均が何を母集団にした値かを区別する）、(b) 研究課題の主な関連の r・95%信頼区間・ρ・n・p・BF₁₀、(c) 探索したペア数と多重比較の基準（ボンフェローニ＝.05÷ペア数）、(d) 特定の項目に依存しないことの確認（上位・外れ値・注意が付いた項目・規模の小さい項目を除いた場合、1項目ずつ除いた場合。元データから計算する）、(e) 対照となる指標との比較（主な関連が、別の指標との関連より強いか弱いか）、(f) 限界。
4. **文献の使い方を整える。** 引用が、結果の解釈とつながっているか。飾りの引用は、つなげるか削る。**文献は下の表のものだけ**（他の題材の文献を引用していたら、直す）。本数を無理に保たない。
5. **長さを守る。** 6項目（abstract, background, objectives, methodology, results_text, discussion）の合計が **4,940字以内**（HTMLタグ込み）。足したら別の部分を削る。
6. **書式を守る。** 下の「守ること」「文献」に従う。title は末尾「†」、`references` は空のまま、数字の桁区切りのカンマは使わない。

{rules}

{refs}

## 書くもの
- 校正後を `{out}` に、下書きと同じ形のJSON（`paper` と `insights`。`insights` も数値・断定を点検して直す）で Write ツールで書く。シェルの heredoc は使わない（バックスラッシュが壊れる）。
- 変更の記録を `{log}` に Write ツールで書く。形式: `{{"changes": [{{"kind": "事実の誤り" か "論理の誤り" か "補った内容" か "削った内容" か "文献" か "体裁", "where": "項目名", "before": "…", "after": "…", "why": "…"}}], "unfixed": ["直せなかった点"]}}`。

## 書いたあとにやること
`cd {root}` で `python -m tools.check_numbers {out} {facts}` を実行する。「未照合」は、元データから自分で計算して確かめ、誤りなら直す。

## 報告（5文以内）
(1) 事実の誤りの件数と内容、(2) 補った内容、(3) 文字数の合計、(4) 下書きのうち、そのまま使えた割合の感触（％）、(5) 直せなかった点。
"""


def make(dataset_id, angle_id, draft=None):
    brief = (TEMP_DIR / f"brief_{dataset_id}.md").read_text(encoding="utf-8")
    sec = lambda n: re.search(rf"## {n}\..*?(?=\n## \d\.|\Z)", brief, re.S).group(0)
    theme = re.search(r"- テーマ: (.*)", brief).group(1)
    ex1 = BASE_DIR / "queue" / "02_oecd_pisa2025_gender_gap.generation.json"
    if dataset_id == "oecd_pisa2025_gender_gap":
        ex1 = BASE_DIR / "queue" / "01_timss2023_student_attitudes.generation.json"
    draft = Path(draft) if draft else TEMP_DIR / "ollama_cmp" / f"gemma4_12b__{dataset_id}.json"
    text = TEMPLATE.format(
        draft=draft, facts=TEMP_DIR / f"facts_{dataset_id}.json", catalog=BASE_DIR / "data" / "catalog" / f"{dataset_id}.json",
        ex1=ex1, theme=theme, rules=sec(3), refs=sec(4), out=TEMP_DIR / f"draft_{dataset_id}.json",
        log=TEMP_DIR / f"proof_changes_{dataset_id}.json", root=BASE_DIR)
    out = TEMP_DIR / f"proof_brief_{dataset_id}.md"
    out.write_text(text, encoding="utf-8")
    return out


if __name__ == "__main__":
    ds, ang = sys.argv[1:3]
    print(make(ds, ang, sys.argv[3] if len(sys.argv) > 3 else None))
