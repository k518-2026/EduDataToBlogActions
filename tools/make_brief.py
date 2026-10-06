"""執筆担当（Opus）と査読担当（Sonnet）への指示書を作る。

    python -m tools.make_brief <dataset_id> <angle_id>

temp/facts_<dataset_id>.json（tools/make_facts.py の出力）がなければ、先に作る。
出力: temp/brief_<dataset_id>.md（執筆）と temp/review_brief_<dataset_id>.md（査読）。
"""
import sys

from src.academic_contexts import get_all_angles_for_dataset
from src.config import BASE_DIR, TEMP_DIR

EXEMPLARS = ("queue/04_oecd_talis_teacher_survey.generation.json", "queue/05_japan_stem_cs_enrollment.generation.json")

WRITER = """# 論文執筆の指示書：{ds}（{angle_id}）

あなたは教育データ分析のショートレター（日本語、JSET学会誌の体裁、**4ページ**）の執筆者です。次の資料だけを根拠に書きます。

## 1. 読む資料（すべて読むこと）
- 事実ファイル（使ってよい数値の一覧）: `{facts}`
- 見本（同じ形式の完成済み。語り口・構成・長さ・注意の払い方を真似る）: `{ex1}` と `{ex2}` の `paper` と `insights`
- テーマ: {theme}
- 研究課題案: RQ1「{rq1}」 / RQ2「{rq2}」
- データの性質と書いてはいけないこと:
  {core}
  {guide}

## 2. 書くもの
`{out}` に、次のJSONを書く（Write ツールを使う。シェルの heredoc で書かない。バックスラッシュが壊れる）。

```
{{"paper": {{"title": "…†", "subtitle": "…", "abstract": "…", "keywords": ["…"], "background": "…", "objectives": "…",
            "methodology": "…", "results_text": "…", "discussion": "…", "references": [],
            "title_en": "…", "authors_en": "EduData Research Group*1 and Educational Data Science Team*2",
            "summary_en": "…", "keywords_en": ["…"]}},
 "insights": {{"executive_summary": "…", "pedagogical_implications": "…", "future_challenges_and_policy": "…", "counter_intuitive_finding": "…"}}}}
```
- 句読点は「，」「．」（論文本体）。insights は「、」「。」でよい。統計記号は `<i>r</i>`、`<i>BF</i><sub>10</sub>`、`<i>p</i>`、`<i>n</i>` を使う。数字の桁区切りのカンマは使わない（12719人）。
- **長さ（HTMLタグ込みの文字数）の上限**: abstract 360 / background 700 / objectives 230 / methodology 600 / results_text 1,600 / discussion 1,450（合計 4,940）。これを超えると5ページになる。**内容の量を絞ってこの中に収める**（ショートレター）。
- title は末尾に「†」。title_en と summary_en に日本語を含めない。`references` は空の配列にする（本文の引用から自動で作る）。
- results_text には【RQ1】【RQ2】の見出しを付けず、段落で「RQ1について，…」「RQ2について，…」と書く。

## 3. 絶対に守ること（過去に実際に起きた誤り）
1. **数値は事実ファイルにあるものだけ。** ない数値（割合、人数、順位、平均、ほかの国の値）を書かない。記憶で数値を補わない。
2. **因果・効果・理由を断定しない。** 「〜を招く」「〜が原因」「〜を阻害」「急務」「構造的」「劇的」を使わない。集計値の関連は個人の因果を示さない（生態学的誤謬）。理由は「考えられる」「仮説にとどまる」と書き、本研究のデータでは検証できないと添える。
3. **計算でつながった指標の相関を結果にしない。** 計と部分、割合とその分子・分母、増減と元の値、男女計と男女別。`correlations_all_pairs` は全ペアの探索なので、研究課題に関わるペアを選び、全ペアを調べたことと多重比較の注意（ボンフェローニ基準＝.05÷ペア数）を方法か結果に書く。
4. **相関は r、95%信頼区間、n、p、BF₁₀、スピアマンの ρ をそろえる。** BF₁₀ が 1/3 未満なら「関連がないことを支持」、3 を超えれば「関連を支持」。観測数が少ない（10未満）ときは、相関を主な結果にしない（記述にとどめる）。
5. **小さい区分・少人数の群に依存した強調をしない。** 最大値・最小値を例に挙げるときは、その区分の人数（規模）を確かめ、小さいものは書くか、規模を添える（過去に入学者564人の学科を「工学にも高い区分がある」と強調して査読で指摘された）。
6. **使ってよい文献は下の表だけ。** 本文中の引用は「Shen and Tam (2008)」「Hyde et al. (2008)」のように著者名と年で書くか、括弧書きなら「（文部科学省，2022）」の形にする。**括弧の中に括弧を入れない**。表にない文献を引用しない。各文献の主張は、タイトルから確実に言える範囲にとどめる。表の文献を、background と discussion で、少なくとも{min_refs}本引用する。
7. 限界（集計値のみ、自己申告、標本抽出の注意、交絡を統制していない、時点の数）を discussion に書く。教育現場への示唆は、確かめられたことと区別し、「効果は確かめられていない」と書く。
8. 決まり文句（「近年のSociety 5.0の進展に伴い」）、「驚くべき」「劇的」「画期的」を使わない。
9. 時系列で標準誤差がない場合、「有意」「統計的に確かな増加」と書かない。差の大きさだけを述べる。

## 4. 使ってよい文献（これ以外を引用しない）
{refs}

## 5. 書いたあとにやること（必ず）
1. `cd {root}` で `python -m tools.check_numbers {out} {facts}` を実行する。「未照合」に出た数値は、(a) 事実ファイルから正しい値に直す、(b) その文を削る、のどちらかにする。年・月・方法の定数・列挙番号は検査が通す。通せない数値が残る場合は、元データ `data/catalog/{ds}.json` から自分で計算して確かめ、報告に書く。
2. 報告には、(1) 項目ごとの文字数、(2) 未照合の数と対処、(3) 自分で気になった点（根拠が薄い文、解釈が強すぎる文、小さい区分への依存）を書く。
"""

REVIEWER = """# 査読の指示書：{ds}

あなたは教育統計・教育工学の査読者です。下の論文（ショートレター。模擬査読で、論文執筆を学ぶ学生や若手研究者への教育支援が目的）を、厳しく、しかし公正に査読してください。

## 読む資料
- 論文の本文: `{draft}` の `paper`（abstract, background, objectives, methodology, results_text, discussion）。参考文献は本文の引用から後で自動で作られるので、`references` が空でも指摘しない。生成AIの付記も PDF の末尾に自動で付くので、本文に付記がないことは指摘しない。
- 事実ファイル（論文が使ってよい数値の全体）: `{facts}`
- 元データ: `{catalog}`
- 見本の査読報告書（形式・長さ・語り口）: `{exemplar}` の `review`

## 査読の観点（各観点に A〜D の評価と、2〜3文の根拠を付ける）
独創性・新規性／有用性・教育的貢献／信頼性・統計的妥当性／論理的一貫性・構成／表現・体裁・引用規範

## 必ずやること
1. 本文の数値を、事実ファイルと元データに当たって確かめる。**自分で計算した値を査読に書くときは、計算を2通りの方法で確かめる**（過去に査読側の再計算が誤っていた）。誤りがあれば、どの数値がどう違うかを指摘する（ない場合は「確認した」と書く）。
2. 因果の断定、生態学的誤謬、交絡、計算でつながった指標の相関、多重比較、自己申告の限界、標本の限界、小さい区分への依存、引用が主張を支えているかを点検する。
3. 論文が言っていないことを批判しない。論文が書いた限界や但し書きは、読んだうえで評価する。
4. 指摘は、具体的に（どの文のどこ）、修正できる形で書く。

## 書くもの
`{out}` に、次のJSONを Write ツールで書く（シェルの heredoc で書かない）。

```
{{"review": {{"paper_title": "（論文の title をそのまま）", "category": "生成AI論文",
  "decision": "条件付採録（Minor Revision）" か "条件付採録（Major Revision）" か "不採録（Reject）",
  "scores": {{"独創性・新規性": ["B", "根拠"], "有用性・教育的貢献": ["B", "根拠"], "信頼性・統計的妥当性": ["B", "根拠"],
             "論理的一貫性・構成": ["B", "根拠"], "表現・体裁・引用規範": ["B", "根拠"]}},
  "overall_critique": "総評（500〜800字）", "major_revisions": ["…（3〜5件）"], "minor_revisions": ["…（2〜3件）"],
  "questions_to_authors": ["…（2〜3件）"],
  "ai_disclosure_evaluation": "生成AIの利用の開示についての評価（60〜120字）",
  "review_date": "{review_date}",
  "ai_review_disclosure": "本査読報告書は，学術論文執筆を学ぶ学生や若手研究者への教育支援（批判的推敲プロセスの模擬体験）を目的として，大規模言語モデル・生成AI（Anthropic Claude）を活用して自動生成された模擬査読レポートです．実際の論文修正や教育現場への適用にあたっては，指導教員等の専門的助言とともに批判的に吟味してください．"}}}}
```
- 句読点は「，」「．」に統一する。
- 報告の最後に、(1) 数値を確かめた結果（確認した件数、誤りの件数）、(2) 判定の理由を2文で書く。
"""


def make(dataset_id, angle_id, review_date="2026年10月06日"):
    angle = [a for a in get_all_angles_for_dataset(dataset_id) if a.angle_id == angle_id][0]
    root = str(BASE_DIR)
    facts = str(TEMP_DIR / f"facts_{dataset_id}.json")
    out = str(TEMP_DIR / f"draft_{dataset_id}.json")
    refs = "\n".join(f"- {r}" for r in angle.curated_references)
    writer = WRITER.format(
        ds=dataset_id, angle_id=angle_id, facts=facts, ex1=str(BASE_DIR / EXEMPLARS[0]), ex2=str(BASE_DIR / EXEMPLARS[1]),
        theme=angle.title_theme, rq1=angle.rq1, rq2=angle.rq2, core=angle.core_research_problems, guide=angle.specific_prompt_guidance,
        out=out, refs=refs, min_refs=min(8, len(angle.curated_references)), root=root)
    reviewer = REVIEWER.format(
        ds=dataset_id, draft=out, facts=facts, catalog=str(BASE_DIR / "data" / "catalog" / f"{dataset_id}.json"),
        exemplar=str(BASE_DIR / EXEMPLARS[0]), out=str(TEMP_DIR / f"review_{dataset_id}.json"), review_date=review_date)
    w, r = TEMP_DIR / f"brief_{dataset_id}.md", TEMP_DIR / f"review_brief_{dataset_id}.md"
    w.write_text(writer, encoding="utf-8")
    r.write_text(reviewer, encoding="utf-8")
    return w, r


if __name__ == "__main__":
    ds, ang = sys.argv[1:3]
    if not (TEMP_DIR / f"facts_{ds}.json").exists():
        from tools.make_facts import make as make_facts
        make_facts(ds, ang)
    from src.utils_date import get_jst_now

    d = get_jst_now()
    w, r = make(ds, ang, review_date=f"{d.year}年{d.month:02d}月{d.day:02d}日")
    print(w)
    print(r)
