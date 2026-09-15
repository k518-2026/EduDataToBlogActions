"""
Unit tests for Academic Paper and PDF Generator modules.
"""
from pathlib import Path
import pytest

from src.academic_paper import AcademicPaperGenerator, AcademicPaper, normalize_jset_text
from src.analyzer import EduDataAnalyzer
from src.fetchers.catalog import DatasetCatalog
from src.pdf.font_loader import register_japanese_fonts
from src.pdf.pdf_generator import EduPaperPdfGenerator, JIS_B5
from src.reporter import EduReportBuilder
from src.insights import EducationalInsights


def test_japanese_font_registration():
    mincho, gothic = register_japanese_fonts()
    assert mincho is not None
    assert gothic is not None
    assert len(mincho) > 0
    assert len(gothic) > 0


def test_jset_text_normalization():
    raw = "本研究では、オープンデータを活用し、学力構造を分析した。その結果、有意な差が認められた。"
    expected = "本研究では，オープンデータを活用し，学力構造を分析した．その結果，有意な差が認められた．"
    assert normalize_jset_text(raw) == expected


def test_academic_paper_generator_creates_all_sections():
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    paper_gen = AcademicPaperGenerator()
    paper = paper_gen.generate_paper(dataset, analysis)

    assert isinstance(paper, AcademicPaper)
    assert len(paper.title) > 0
    assert paper.title.endswith("†")
    assert len(paper.abstract) > 50
    assert len(paper.keywords) >= 3
    assert len(paper.background) > 100
    assert len(paper.objectives) > 50
    assert len(paper.methodology) > 50
    assert len(paper.results_text) > 50
    assert len(paper.discussion) > 100
    assert len(paper.references) >= 3
    assert len(paper.title_en) > 0
    assert len(paper.authors_en) > 0
    assert len(paper.summary_en) > 0
    assert len(paper.keywords_en) >= 3


def test_pdf_generator_builds_valid_pdf(tmp_path):
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    from src.visualizer import EduDataVisualizer
    viz = EduDataVisualizer(output_dir=tmp_path)
    chart_path = viz.generate_chart(dataset, analysis)

    paper_gen = AcademicPaperGenerator()
    paper = paper_gen.generate_paper(dataset, analysis)

    pdf_gen = EduPaperPdfGenerator()
    out_pdf = tmp_path / "test_thesis_output.pdf"
    res_path = pdf_gen.generate_pdf(paper, dataset, analysis, chart_path, out_pdf)

    assert res_path.exists()
    assert res_path.stat().st_size > 15000  # Should be substantial size

    with open(res_path, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-"


def test_no_society_name_in_paper_and_pdf(tmp_path):
    """Ensures academic society names and fictitious journal IDs are never published."""
    catalog = DatasetCatalog()
    forbidden_strings = ["日本教育工学会", "Jpn．J．Educ．Technol．", "Vol． XX，Suppl．"]

    for dataset_id in ["japan_national_assessment_math", "japan_mext_ict_informatization"]:
        dataset = catalog.get_by_id(dataset_id)
        analyzer = EduDataAnalyzer()
        analysis = analyzer.analyze(dataset)
        paper_gen = AcademicPaperGenerator()
        paper = paper_gen.generate_paper(dataset, analysis)

        all_text = " ".join([
            paper.title, paper.subtitle, paper.abstract, " ".join(paper.keywords),
            paper.background, paper.objectives, paper.methodology,
            paper.results_text, paper.discussion, " ".join(paper.references),
            paper.title_en, paper.summary_en,
        ])
        for forbidden in forbidden_strings:
            assert forbidden not in all_text, f"Forbidden society string '{forbidden}' found in paper text!"

    # Verify PDF compiles cleanly without errors
    pdf_gen = EduPaperPdfGenerator()
    out_pdf = tmp_path / "check_no_society.pdf"
    res_path = pdf_gen.generate_pdf(paper, dataset, analysis, None, out_pdf)
    assert res_path.exists()
    assert res_path.stat().st_size > 10000


def test_category_box_is_short_letter():
    """Verifies that the paper category label is 'ショートレター' and not '教育実践研究論文'."""
    pdf_gen_file = Path("src/pdf/pdf_generator.py").read_text(encoding="utf-8")
    assert "ショートレター" in pdf_gen_file
    assert "教育実践研究論文" not in pdf_gen_file



def test_reporter_integrates_pdf_link(tmp_path):
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    insights = EducationalInsights(
        executive_summary="サマリーテスト",
        pedagogical_implications="指導示唆テスト",
        future_challenges_and_policy="政策提言テスト",
    )

    chart_file = tmp_path / "dummy_chart.png"
    chart_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")

    dummy_pdf_url = "https://github.com/k518-2026/EduDataToBlogActions/blob/main/reports/pdf/2026-09-14_test_paper.pdf"
    dummy_pdf_path = tmp_path / "2026-09-14_test_paper.pdf"
    dummy_pdf_path.write_bytes(b"%PDF-1.4 dummy")

    builder = EduReportBuilder()
    report = builder.build_report(
        dataset=dataset,
        analysis=analysis,
        insights=insights,
        chart_path=chart_file,
        pdf_path=dummy_pdf_path,
        pdf_url=dummy_pdf_url,
    )

    assert report.pdf_url == dummy_pdf_url
    assert report.pdf_path == dummy_pdf_path
    assert dummy_pdf_url in report.html_content
    assert "学術論文形式の完全版レポート" in report.html_content
    assert dummy_pdf_url in report.markdown_content
    assert "学術論文形式PDF" in report.markdown_content


def test_enhanced_academic_paper_requirements():
    """Verifies foreign citations in background, exactly 2 RQs, aligned Results & Discussion by RQ1->RQ2, 4 references, and 2 citations per RQ in discussion."""
    catalog = DatasetCatalog()
    for dataset_id in ["japan_national_assessment_math", "japan_mext_ict_informatization"]:
        dataset = catalog.get_by_id(dataset_id)
        analyzer = EduDataAnalyzer()
        analysis = analyzer.analyze(dataset)
        paper_gen = AcademicPaperGenerator()
        paper = paper_gen.generate_paper(dataset, analysis)

        # 1. Background cites >= 2 foreign sources and has detailed explanation (> 400 chars)
        foreign_keywords = ["OECD", "TIMSS", "Mullis", "UNESCO", "Wing", "PISA"]
        found_foreign = [kw for kw in foreign_keywords if kw in paper.background]
        assert len(found_foreign) >= 2, f"Expected >= 2 foreign citations in background for {dataset_id}, found: {found_foreign}"
        assert len(paper.background) >= 400, f"Expected detailed background (>=400 chars), found: {len(paper.background)}"

        # 2. Exactly 2 RQs (RQ1, RQ2 on separate lines, RQ3 must not exist)
        rq_lines = [line.strip() for line in paper.objectives.split("\n") if any(line.startswith(f"・{k}") or line.startswith(k) for k in ["RQ1", "RQ2", "RQ3"])]
        assert len(rq_lines) == 2, f"Expected exactly 2 RQ lines in objectives for {dataset_id}, found: {rq_lines}"
        assert "RQ1" in rq_lines[0] and "RQ2" in rq_lines[1]
        assert "RQ3" not in paper.objectives, f"RQ3 must not exist in {dataset_id}"
        for line in rq_lines:
            assert line.startswith("・"), f"RQ line should start with bullet: {line}"

        # 3. Strictly 4 references
        assert len(paper.references) == 4, f"Expected strictly 4 references for {dataset_id}, found: {len(paper.references)}"

        # 4. Results text references RQ1 then RQ2 in order, plus multi-tables/figures
        assert "RQ1" in paper.results_text and "RQ2" in paper.results_text
        assert paper.results_text.index("RQ1") < paper.results_text.index("RQ2"), "Results must discuss RQ1 before RQ2"
        assert "表１" in paper.results_text
        assert "表２" in paper.results_text
        assert "図１" in paper.results_text
        assert "図２" in paper.results_text

        # 5. Discussion compares similarities and differences for RQ1 then RQ2 in order, plus future challenges
        assert "RQ1" in paper.discussion and "RQ2" in paper.discussion
        assert paper.discussion.index("RQ1") < paper.discussion.index("RQ2"), "Discussion must discuss RQ1 before RQ2"
        assert "同じところ" in paper.discussion or "共通点" in paper.discussion
        assert "違うところ" in paper.discussion or "相違点" in paper.discussion
        assert "今後の課題" in paper.discussion

        # 6. Discussion cites 2 prior studies for RQ1 and 2 prior studies for RQ2
        rq1_disc = paper.discussion[:paper.discussion.index("RQ2")]
        rq2_disc = paper.discussion[paper.discussion.index("RQ2"):]
        if dataset_id == "japan_national_assessment_math":
            assert "清水" in rq1_disc and "OECD" in rq1_disc, "RQ1 discussion in Math must cite 清水 and OECD"
            assert "堀田" in rq2_disc and "Mullis" in rq2_disc, "RQ2 discussion in Math must cite 堀田 and Mullis"
        else:
            assert "国立教育政策研究所" in rq1_disc and "UNESCO" in rq1_disc, "RQ1 discussion in ICT must cite 国立教育政策研究所 and UNESCO"
            assert "堀田" in rq2_disc and "Wing" in rq2_disc, "RQ2 discussion in ICT must cite 堀田 and Wing"



def test_pdf_with_multiple_tables_and_figures_and_ai_disclosure(tmp_path):
    """Verifies PDF generation with 2 tables, 2 figures, and generative AI disclosure note."""
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    from src.visualizer import EduDataVisualizer
    viz = EduDataVisualizer(output_dir=tmp_path)
    primary_chart = viz.generate_chart(dataset, analysis)
    secondary_chart = viz.generate_secondary_chart(dataset, analysis)

    paper_gen = AcademicPaperGenerator()
    paper = paper_gen.generate_paper(dataset, analysis)

    pdf_gen = EduPaperPdfGenerator()
    out_pdf = tmp_path / "comprehensive_test_paper.pdf"
    res_path = pdf_gen.generate_pdf(
        paper=paper,
        dataset=dataset,
        analysis=analysis,
        chart_path=primary_chart,
        output_pdf_path=out_pdf,
        secondary_chart_path=secondary_chart,
    )

    assert res_path.exists()
    assert res_path.stat().st_size > 20000
