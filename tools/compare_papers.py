"""複数の論文（draft の形の JSON）を、同じ物差しで機械的に比べる。

    python -m tools.compare_papers <dataset_id> <angle_id> <名前=JSONのパス> [<名前=JSONのパス> ...]

JSON は {"paper": {...}, "insights": {...}} の形（generation.json でも可）。
見るもの: 文字数、事実ファイルにない数値、禁止語、引用の実在（文献表との対応）、英文の日本語混入、PDFのページ数。
"""
import json
import re
import sys
import tempfile
from pathlib import Path

from src.academic_contexts import get_all_angles_for_dataset
from src.academic_paper import AcademicPaper, UnverifiedCitationError, extract_in_text_citations, synchronize_citations_and_references
from src.analyzer import EduDataAnalyzer
from src.config import TEMP_DIR
from src.fetchers.catalog import DatasetCatalog
from tools.check_numbers import SECTIONS, check

FORBIDDEN = ["招く", "原因", "阻害", "急務", "構造的", "劇的", "驚くべき", "画期的", "Society 5.0", "必然", "決定的", "明らかに", "確実に"]
CAUSAL = ["ため", "によって", "による", "もたらす", "結果として", "影響を与え", "左右"]
JA = re.compile(r"[぀-ヿ一-龯]")


def evaluate(name, path, ds, angle_id):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    paper = data["paper"]
    body = {f: paper.get(f, "") for f in SECTIONS}
    res = {"name": name}
    res["chars"] = {f: len(v) for f, v in body.items()}
    res["chars_total"] = sum(res["chars"].values())
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump({"paper": paper}, tf, ensure_ascii=False)
    un = check(tf.name, str(TEMP_DIR / f"facts_{ds}.json"))
    res["numbers_unmatched"] = [(s, t, c) for s, t, c in un]
    text = "".join(body.values())
    res["forbidden_hits"] = {w: text.count(w) for w in FORBIDDEN if w in text}
    res["causal_phrase_count"] = sum(text.count(w) for w in CAUSAL)
    angle = [a for a in get_all_angles_for_dataset(ds) if a.angle_id == angle_id][0]
    cites = extract_in_text_citations(body["background"] + "\n" + body["discussion"])
    res["citations_found"] = len(cites)
    try:
        p2 = synchronize_citations_and_references(AcademicPaper(**{**paper, "references": []}), ds, angle)
        res["references_resolved"] = len(p2.references)
        res["unverified_citations"] = []
    except UnverifiedCitationError as e:
        res["references_resolved"] = 0
        res["unverified_citations"] = [str(e)[:200]]
        p2 = None
    en = paper.get("title_en", "") + paper.get("summary_en", "")
    res["japanese_in_english"] = bool(JA.search(en))
    res["title_dagger"] = paper.get("title", "").endswith("†")
    res["italic_tag_balance"] = text.count("<i>") == text.count("</i>")
    # PDF の枚数（論文だけ。図は同じものを使う）
    try:
        from src.pdf.pdf_generator import EduPaperPdfGenerator

        dataset = DatasetCatalog().get_by_id(ds)
        analysis = EduDataAnalyzer().analyze(dataset, selected_angle=angle)
        chart = TEMP_DIR / f"chart_{ds}.png"
        sec = TEMP_DIR / f"chart_secondary_{ds}.png"
        if p2 is not None and chart.exists():
            out = Path(tempfile.gettempdir()).parent / "ollama_cmp_tmp.pdf"
            out = TEMP_DIR / "ollama_cmp" / f"{name}.pdf"
            out.parent.mkdir(exist_ok=True)
            EduPaperPdfGenerator().generate_pdf(p2, dataset, analysis, chart, out, secondary_chart_path=sec if sec.exists() else None)
            from pypdf import PdfReader

            res["pdf_pages"] = len(PdfReader(str(out)).pages)
    except Exception as e:  # noqa: BLE001
        res["pdf_error"] = f"{type(e).__name__}: {e}"[:200]
    return res


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ds, ang = sys.argv[1:3]
    out = []
    for spec in sys.argv[3:]:
        name, path = spec.split("=", 1)
        out.append(evaluate(name, path, ds, ang))
    (TEMP_DIR / "ollama_cmp" / f"compare_{ds}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in out:
        print("=====", r["name"])
        print(" 文字数", r["chars_total"], r["chars"])
        print(" 未照合の数値", len(r["numbers_unmatched"]), [t for _, t, _ in r["numbers_unmatched"]][:12])
        print(" 禁止語", r["forbidden_hits"], "| 因果っぽい語", r["causal_phrase_count"])
        print(" 引用", r["citations_found"], "→ 文献表と対応", r["references_resolved"], r["unverified_citations"])
        print(" 英文に日本語", r["japanese_in_english"], "| †", r["title_dagger"], "| <i>対応", r["italic_tag_balance"], "| PDF", r.get("pdf_pages"), r.get("pdf_error", ""))
