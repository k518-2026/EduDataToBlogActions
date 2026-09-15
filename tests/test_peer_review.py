"""
Unit tests for Academic Peer Review Report and PDF Generator modules.
"""
from pathlib import Path
import pytest

from src.academic_paper import AcademicPaperGenerator
from src.analyzer import EduDataAnalyzer
from src.fetchers.catalog import DatasetCatalog
from src.pdf.peer_review_pdf_generator import PeerReviewPdfGenerator
from src.peer_review import PeerReviewGenerator, PeerReviewReport
from src.publishers.markdown_file import MarkdownFilePublisher
from src.reporter import EduReportBuilder
from src.insights import EducationalInsights


def test_peer_review_generator_math_dataset():
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    paper_gen = AcademicPaperGenerator()
    paper = paper_gen.generate_paper(dataset, analysis)

    review_gen = PeerReviewGenerator()
    review = review_gen.generate_review(paper, dataset, analysis)

    assert isinstance(review, PeerReviewReport)
    assert len(review.paper_title) > 0
    assert "条件付採録" in review.decision or "Major Revision" in review.decision

    # Check 5 criteria evaluations
    assert len(review.scores) == 5
    for key, (grade, comment) in review.scores.items():
        assert len(grade) > 0
        assert len(comment) > 10

    # Check strict academic critiques
    assert len(review.overall_critique) > 100
    assert len(review.major_revisions) >= 3
    assert len(review.minor_revisions) >= 2
    assert len(review.questions_to_authors) >= 2
    assert len(review.ai_disclosure_evaluation) > 30
    assert len(review.ai_review_disclosure) > 30
    assert "生成AI" in review.ai_review_disclosure

    # Ensure critical methodological critiques are included
    full_text = review.overall_critique + "".join(review.major_revisions)
    assert "生態学的誤謬" in full_text or "集約データ" in full_text
    assert "交絡" in full_text or "SES" in full_text or "因果" in full_text


def test_peer_review_generator_ict_dataset():
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_mext_ict_informatization")
    assert dataset is not None
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    paper_gen = AcademicPaperGenerator()
    paper = paper_gen.generate_paper(dataset, analysis)

    review_gen = PeerReviewGenerator()
    review = review_gen.generate_review(paper, dataset, analysis)

    assert isinstance(review, PeerReviewReport)
    assert len(review.paper_title) > 0
    assert "条件付採録" in review.decision


def test_peer_review_pdf_generator_builds_valid_pdf(tmp_path):
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    paper_gen = AcademicPaperGenerator()
    paper = paper_gen.generate_paper(dataset, analysis)

    review_gen = PeerReviewGenerator()
    review = review_gen.generate_review(paper, dataset, analysis)

    pdf_gen = PeerReviewPdfGenerator()
    output_pdf = tmp_path / "test_peer_review.pdf"
    pdf_gen.generate_pdf(review, output_pdf)

    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 20000

    # Check PDF magic bytes
    with open(output_pdf, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-"


def test_report_builder_and_markdown_publisher_with_peer_review(tmp_path):
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    insights = EducationalInsights(
        executive_summary="テストサマリーです。",
        pedagogical_implications="テスト授業示唆です。",
        future_challenges_and_policy="テスト政策提言です。",
    )

    fake_chart = tmp_path / "chart.png"
    fake_chart.write_bytes(b"dummy image data")
    fake_pdf = tmp_path / "paper.pdf"
    fake_pdf.write_bytes(b"%PDF- dummy paper")
    fake_review_pdf = tmp_path / "review.pdf"
    fake_review_pdf.write_bytes(b"%PDF- dummy review")
    fake_py = tmp_path / "analysis.py"
    fake_py.write_text("# dummy python", encoding="utf-8")

    builder = EduReportBuilder()
    report = builder.build_report(
        dataset=dataset,
        analysis=analysis,
        insights=insights,
        chart_path=fake_chart,
        pdf_path=fake_pdf,
        pdf_url="https://github.com/example/paper.pdf",
        peer_review_pdf_path=fake_review_pdf,
        peer_review_pdf_url="https://github.com/example/review.pdf",
        py_script_path=fake_py,
        py_script_url="https://github.com/example/analysis.py",
    )

    assert "査読報告書PDF" in report.markdown_content
    assert "https://github.com/example/review.pdf" in report.markdown_content
    assert "査読報告書（生成AI模擬査読・PDF）を閲覧" in report.html_content

    # Test publisher copies the review PDF into reports_dir/pdf/
    reports_dir = tmp_path / "reports"
    publisher = MarkdownFilePublisher(reports_dir=reports_dir)
    success = publisher.publish(report)

    assert success is True
    published_review_pdf = reports_dir / "pdf" / fake_review_pdf.name
    assert published_review_pdf.exists()
    assert published_review_pdf.read_bytes() == b"%PDF- dummy review"
