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
