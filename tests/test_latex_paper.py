"""LaTeX 版の論文の、文字の変換（タグと特殊文字）。LuaLaTeX がなくても動く。"""
from tools.latex_paper import paragraphs, rq_block, tex


def test_tags_and_specials():
    assert tex("<i>r</i>=.39，<i>BF</i><sub>10</sub>=7.9") == r"\textit{r}=.39，\textit{BF}\textsubscript{10}=7.9"
    assert tex("5% & 10_a #1 $x$ {y}") == r"5\% \& 10\_a \#1 \$x\$ \{y\}"
    assert tex("<.001，BF>1000") == "<.001，BF>1000"  # タグでない < と > は、そのまま


def test_paragraphs_and_research_questions():
    assert paragraphs("あ\n\nい") == "あ\n\nい"
    out = rq_block("導入\n\n・RQ1：一つ目\n\n・RQ2：二つ目")
    assert r"\begin{itemize}" in out and out.count(r"\item") == 2 and out.startswith("導入")
