r"""論文の JSON（generation.json）から、LuaLaTeX で組んだ PDF を作る（試作）。

    python -m tools.latex_paper <generation.json> <dataset_id> <angle_id> [<出力フォルダ>]

出力フォルダの既定: temp/latex/<dataset_id>/。そこに paper.tex、図、paper.pdf を作る。
体裁は、reportlab 版（src/pdf/pdf_generator.py）の JSET 風（A4・2段組）に合わせる。本文は10pt。
LuaLaTeX は PATH にあるもの（TeX Live）を使う。
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from src.academic_contexts import get_all_angles_for_dataset
from src.academic_paper import AcademicPaper
from src.analyzer import EduDataAnalyzer, format_apa_p, format_apa_stat
from src.config import TEMP_DIR
from src.fetchers.catalog import DatasetCatalog
from src.utils import format_bayes_factor
from src.visualizer import EduDataVisualizer

SPECIALS = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
            "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "$": r"\$"}
TAGS = {"<i>": r"\textit{", "</i>": "}", "<em>": r"\textit{", "</em>": "}", "<b>": r"\textbf{", "</b>": "}",
        "<strong>": r"\textbf{", "</strong>": "}", "<sub>": r"\textsubscript{", "</sub>": "}",
        "<sup>": r"\textsuperscript{", "</sup>": "}"}
TAG_RE = re.compile(r"(</?(?:i|em|b|strong|sub|sup)>)")


def tex(s):
    """HTML 風の簡単なタグ（i, b, sub, sup）を LaTeX にし、特殊文字をエスケープする。"""
    out = []
    for part in TAG_RE.split(s or ""):
        if part in TAGS:
            out.append(TAGS[part])
        else:
            out.append("".join(SPECIALS.get(c, c) for c in part))
    return "".join(out)


def paragraphs(s):
    return "\n\n".join(tex(p.strip()) for p in (s or "").split("\n\n") if p.strip())


def rq_block(s):
    """objectives: 先頭の文と、「・RQ…」の項目を、段落と箇条書きにする。"""
    parts = [p.strip() for p in (s or "").split("\n") if p.strip()]
    lead = [p for p in parts if not p.startswith("・")]
    items = [p[1:].strip() for p in parts if p.startswith("・")]
    out = "\n\n".join(tex(p) for p in lead)
    if items:
        out += "\n\\begin{itemize}\n" + "\n".join(r"\item " + tex(i) for i in items) + "\n\\end{itemize}"
    return out


PREAMBLE = r"""\documentclass[a4paper,10pt,twocolumn]{ltjsarticle}
\usepackage[haranoaji]{luatexja-preset}
\usepackage[top=18mm,bottom=20mm,left=17mm,right=17mm,columnsep=8mm]{geometry}
\usepackage{graphicx,booktabs,array,caption,enumitem,xcolor,tikz}
\usetikzlibrary{shapes.geometric}
\setlength{\parindent}{1\zw}
\renewcommand{\baselinestretch}{1.0}
\setlength{\parskip}{0pt}
\renewcommand{\thesection}{\arabic{section}.}
\renewcommand{\thesubsection}{\arabic{section}.\arabic{subsection}.}
\makeatletter
\renewcommand{\section}{\@startsection{section}{1}{\z@}{1.1\Cvs \@plus.4\Cdp \@minus.2\Cdp}{.5\Cvs \@plus.2\Cdp}{\normalfont\gtfamily\bfseries\large}}
\renewcommand{\subsection}{\@startsection{subsection}{2}{\z@}{.8\Cvs \@plus.3\Cdp \@minus.2\Cdp}{.3\Cvs \@plus.1\Cdp}{\normalfont\gtfamily\bfseries\normalsize}}
\makeatother
\captionsetup{font={small,sf},labelsep=space,justification=raggedright,singlelinecheck=false,skip=3pt}
\captionsetup[table]{position=top}
\setlist[itemize]{leftmargin=1.2\zw,itemsep=0pt,topsep=2pt,parsep=0pt}
\setlength{\textfloatsep}{8pt plus 2pt minus 2pt}
\setlength{\floatsep}{8pt plus 2pt minus 2pt}
\setlength{\intextsep}{8pt plus 2pt minus 2pt}
\pagestyle{plain}
\raggedbottom
"""


def build_tables(analysis, dataset):
    rows1 = []
    for name, st in analysis.descriptive_stats.items():
        rows1.append(f"{tex(name)} & {st.count} & {st.mean:.1f} & {st.std:.1f} & {st.median:.1f} & {st.min_val:.1f} & {st.max_val:.1f} \\\\")
    t1 = (r"\begin{table*}[!t]" "\n" r"\caption{主要指標の基本記述統計量}" "\n" r"\centering\small" "\n"
          r"\begin{tabular}{>{\raggedright\arraybackslash}p{9.2cm}rrrrrr}" "\n" r"\toprule" "\n"
          r"指標 & \textit{K} & 平均 & \textit{SD} & 中央値 & 最小 & 最大 \\" "\n" r"\midrule" "\n"
          + "\n".join(rows1) + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n"
          r"\par\smallskip{\footnotesize 注）単位は" + tex(dataset.unit or "") + r"，\textit{K}は観測数（国・地域）．}" "\n" r"\end{table*}")
    rows2 = []
    for cr in analysis.correlations[:5]:
        bf = format_bayes_factor(cr.bf10)
        rows2.append(f"{tex(cr.metric_x)} & {tex(cr.metric_y)} & {tex(format_apa_stat(cr.pearson_r, bounded=True))} & "
                     f"{tex(format_apa_p(cr.p_value))} & {tex(str(bf))} \\\\")
    t2 = (r"\begin{table*}[!t]" "\n" r"\caption{主要指標間のピアソンの相関係数と，ベイズファクター}" "\n" r"\centering\small" "\n"
          r"\begin{tabular}{>{\raggedright\arraybackslash}p{6.4cm}>{\raggedright\arraybackslash}p{6.4cm}rrr}" "\n" r"\toprule" "\n"
          r"指標 \textit{X} & 指標 \textit{Y} & \textit{r} & \textit{p} & \textit{BF}\textsubscript{10} \\" "\n" r"\midrule" "\n"
          + "\n".join(rows2) + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n"
          r"\par\smallskip{\footnotesize 注）\textit{BF}\textsubscript{10}はJZSベイズファクター（3を超えれば関連を支持，1/3を下回れば関連がないことを支持）．全ペアの探索の一部を載せた．}" "\n" r"\end{table*}")
    return t1, t2


def model_blocks(dataset_id, angle_id):
    """data/model_specs.json の定義から、重回帰・パス解析・SEM の表と図（LaTeX）を作る。なければ空。"""
    from src import sem_models as sm
    from tools.make_facts import _model_spec, _run_models

    spec = _model_spec(dataset_id, angle_id)
    if not spec:
        return [], [], None
    ds = DatasetCatalog().get_by_id(dataset_id)
    res = _run_models(ds.df, spec)
    labels = spec.get("path", {}).get("labels", {})
    tables, figures = [], []

    def num(x, nd=2):
        t = f"{x:+.{nd}f}"
        return t.replace("+", "$+$").replace("-", "$-$")

    if "regression" in res:
        r = res["regression"]
        rows = "\n".join(
            f"{tex(labels.get(c['x'], c['x']))} & {num(c['beta'])} & [{num(c['beta_ci95_boot'][0])}, {num(c['beta_ci95_boot'][1])}] & {c['p']:.3f} & {c['VIF']:.2f} \\\\"
            for c in r["coefficients"])
        note = ("注）従属変数：" + tex(r["y"]) + f"．\\textit{{n}}={r['n']}，\\textit{{R}}\\textsuperscript{{2}}={r['R2']:.2f}（調整済み {r['adj_R2']:.2f}），"
                f"\\textit{{F}}({r['df'][0]},{r['df'][1]})={r['F']:.2f}．標準化係数．95\\%CIはブートストラップ（{r['n_boot']}回）．")
        tables.append("\\begin{table}[t]\n\\caption{" + tex(spec["regression"].get("title", "重回帰分析")) + "}\n\\centering\\scriptsize\\setlength{\\tabcolsep}{3pt}\n"
                      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{3.0cm}rrrr}\n\\toprule\n説明変数 & $\\beta$ & 95\\%CI & \\textit{p} & VIF \\\\\n\\midrule\n"
                      + rows + "\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip{\\scriptsize " + note + "}\n\\end{table}")
    if "path" in res:
        pm = res["path"]
        figures.append("\\begin{figure*}[t]\\centering\n" + sm.path_diagram_tikz(pm, labels, width_cm=15.5) + "\n"
                       "\\caption{パス図（標準化係数。破線は \\textit{p}$\\ge$.05。\\textit{n}=" + str(pm["n"]) + "）}\n\\end{figure*}")
        eff = "\n".join(
            f"{tex(labels.get(e['from'], e['from']))} → {tex(labels.get(e['to'], e['to']))} & {e['direct']:.2f} & "
            f"{e['indirect']:.2f} [{e['indirect_ci95_boot'][0]:.2f}, {e['indirect_ci95_boot'][1]:.2f}] & {e['total']:.2f} \\\\"
            for e in pm["effects"])
        fit = pm.get("fit") or {}
        fit_txt = (f"\\textit{{$\\chi^2$}}({fit['df']:.0f})={fit['chi2']:.2f}，RMSEA={fit['RMSEA']:.2f}，CFI={fit['CFI']:.2f}（観測数が少ないため目安）．" if fit.get("chi2") is not None and fit.get("df") else "")
        tables.append("\\begin{table}[t]\n\\caption{パス解析：直接・間接・総合の関連（標準化）}\n\\centering\\scriptsize\\setlength{\\tabcolsep}{3pt}\n"
                      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{3.4cm}rrr}\n\\toprule\n経路 & 直接 & 間接 [95\\%CI] & 総合 \\\\\n\\midrule\n"
                      + eff + "\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip{\\scriptsize 注）" + fit_txt
                      + f"間接の95\\%CIはブートストラップ（{pm['n_boot']}回）．「直接」が0.00の経路は，モデルに含めていない．}}\n\\end{{table}}")
    if "sem" in res:
        se = res["sem"]
        fit = se["fit"]
        figures.append("\\begin{figure*}[t]\\centering\n" + sm.sem_diagram_tikz(se, spec["sem"]["latent"], spec["sem"].get("labels") or labels, width_cm=15.5) + "\n"
                       "\\caption{" + tex(spec["sem"].get("title", "SEM")) + f"（標準化推定値。\\textit{{$\\chi^2$}}({fit['df']:.0f})={fit['chi2']:.2f}，"
                       f"CFI={fit['CFI']:.2f}，RMSEA={fit['RMSEA']:.2f}，\\textit{{n}}={se['n']}。破線は \\textit{{p}}$\\ge$.05）}}\n\\end{{figure*}}")
    return tables, figures, res


def build(gen_path, dataset_id, angle_id, out_dir=None):
    gen = json.loads(Path(gen_path).read_text(encoding="utf-8"))
    p = AcademicPaper(**gen["paper"])
    angle = [a for a in get_all_angles_for_dataset(dataset_id) if a.angle_id == angle_id][0]
    dataset = DatasetCatalog().get_by_id(dataset_id)
    analysis = EduDataAnalyzer().analyze(dataset, selected_angle=angle)
    out = Path(out_dir) if out_dir else TEMP_DIR / "latex" / dataset_id
    out.mkdir(parents=True, exist_ok=True)
    viz = EduDataVisualizer(output_dir=out)
    c1 = viz.generate_chart(dataset, analysis, selected_angle=angle)
    c2 = viz.generate_secondary_chart(dataset, analysis, selected_angle=angle)
    t1, t2 = build_tables(analysis, dataset)
    focus = (angle.focus_metrics or [dataset.metrics[0]])[0]
    cap1 = tex(f"{focus}の値の比較（上位・下位と日本を抜粋）")
    cap2 = tex(f"{angle.scatter_x_metric}と{angle.scatter_y_metric}の関連（回帰直線と95%信頼区間の帯）") if angle.scatter_x_metric and angle.scatter_y_metric else "指標間の関連"
    date = gen.get("date", "2026年10月")
    body = []
    body.append(r"\begin{document}")
    body.append(r"\twocolumn[{")
    body.append(r"\noindent\fbox{\gtfamily\small\ 生成AI論文\ }\par\medskip")
    body.append(r"\begin{center}")
    body.append(r"{\gtfamily\bfseries\LARGE " + tex(p.title.rstrip("†")) + r"$^{\dagger}$}\par\medskip")
    if p.subtitle:
        body.append(r"{\gtfamily\bfseries\large " + tex(p.subtitle) + r"}\par\medskip")
    body.append(r"{\normalsize EduData調査研究グループ$^{*1}$・教育データサイエンス解析班$^{*2}$}\par")
    body.append(r"{\small オープン教育統計推進プロジェクト$^{*1}$・初等中等STEM教育データ基盤ユニット$^{*2}$}")
    body.append(r"\end{center}\smallskip")
    body.append(r"\noindent\begin{minipage}{\textwidth}\small " + tex(p.abstract) + r"\par\smallskip")
    body.append(r"\noindent{\gtfamily キーワード：}" + tex("，".join(p.keywords)) + r"\end{minipage}\medskip")
    body.append(r"}]")  # 本文に「]」（信頼区間）があっても、囲みが終わらないように、波括弧で包む
    body.append(r"\let\thefootnote\relax")
    body.append(r"\footnotetext{\footnotesize " + date + r"執筆\\ $^{\dagger}$" + tex(p.title_en) + r"\\ $^{*1}$ Open Education Data Project, Tokyo, Japan\quad $^{*2}$ Educational Data Science Unit, Tokyo, Japan}")
    body.append(r"\section{はじめに}")
    body.append(r"\subsection{研究の背景}")
    body.append(paragraphs(p.background))
    body.append(r"\subsection{リサーチクエスチョン}")
    body.append(rq_block(p.objectives))
    body.append(r"\section{調査対象および分析方法}")
    body.append(paragraphs(p.methodology))
    m_tables, m_figs, _models = model_blocks(dataset_id, angle_id)
    body.append(t1)  # 2段幅の表は、次のページの先頭にしか置けない。結果の前に宣言して、2ページ目の先頭に来るようにする
    body.append(t2)
    body.append(r"\section{結果}")
    body.append(paragraphs(p.results_text))
    body.append(r"\begin{figure}[t]\centering\includegraphics[width=\columnwidth]{" + c1.name + r"}\caption{" + cap1 + r"}\end{figure}")
    body.append(r"\begin{figure}[t]\centering\includegraphics[width=\columnwidth]{" + c2.name + r"}\caption{" + cap2 + r"}\end{figure}")
    for blk in m_tables + m_figs:
        body.append(blk)
    body.append(r"\section{考察}")
    body.append(paragraphs(p.discussion))
    body.append(r"\section*{参考文献}")
    body.append(r"\begingroup\scriptsize\setlength{\parindent}{0pt}\raggedright")
    for r_ in p.references:
        body.append(r"\par\hangindent=1.5\zw\hangafter=1 " + tex(r_) + r"\vspace{1pt}")
    body.append(r"\endgroup")
    body.append(r"\section*{Summary}")
    body.append(r"{\footnotesize\setlength{\parindent}{0pt}" + tex(p.summary_en) + r"\par\smallskip KEYWORDS: " + tex(", ".join(p.keywords_en)) + r"\par}")
    body.append(r"\medskip\noindent\fbox{\parbox{\dimexpr\columnwidth-2\fboxsep-2\fboxrule}{\footnotesize\gtfamily "
                r"【付記：生成AIによる自動執筆に関する開示】\\ 本論文は学生への教育目的で作成している．使用しているデータは公的オープンデータである．"
                r"統計の算出はPythonで行い，文章は生成AI（Anthropic Claude等）を活用して作成した．記載した統計数値は元データに準拠しているが，"
                r"教育学的な考察や提言の妥当性は，指導現場の実情に応じて，批判的に吟味してほしい．}}")
    body.append(r"\end{document}")
    (out / "paper.tex").write_text(PREAMBLE + "\n".join(body) + "\n", encoding="utf-8")
    log = None
    for _ in range(2):
        log = subprocess.run(["lualatex", "-interaction=nonstopmode", "-halt-on-error", "paper.tex"], cwd=out,
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
    pdf = out / "paper.pdf"
    pages = None
    if pdf.exists():
        from pypdf import PdfReader

        pages = len(PdfReader(str(pdf)).pages)
    return {"tex": str(out / "paper.tex"), "pdf": str(pdf) if pdf.exists() else None, "pages": pages,
            "returncode": log.returncode, "log_tail": (log.stdout or "")[-1500:] if log.returncode else ""}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    gen, ds, ang = sys.argv[1:4]
    res = build(gen, ds, ang, sys.argv[4] if len(sys.argv) > 4 else None)
    print(json.dumps(res, ensure_ascii=False, indent=1))
