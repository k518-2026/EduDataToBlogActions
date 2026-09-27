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
    assert "査読報告書PDFを直接ダウンロード" in report.html_content

    # Test publisher copies the review PDF into reports_dir/pdf/
    reports_dir = tmp_path / "reports"
    publisher = MarkdownFilePublisher(reports_dir=reports_dir)
    success = publisher.publish(report)

    assert success is True
    published_review_pdf = reports_dir / "pdf" / fake_review_pdf.name
    assert published_review_pdf.exists()
    assert published_review_pdf.read_bytes() == b"%PDF- dummy review"


def test_peer_review_rejects_fatal_flaws():
    """Verify that peer review strictly rejects papers with part-whole artifacts or contradictory conclusions."""
    from src.academic_paper import AcademicPaper
    from src.analyzer import CorrelationResult, NoCorrelationResult
    from src.fetchers.base import EducationDataset
    import pandas as pd

    df = pd.DataFrame({
        "年度": [2020, 2021, 2022, 2023],
        "入学者総数": [1000, 1100, 1200, 1300],
        "女性比率": [15.0, 16.0, 17.0, 18.0],
    })
    dataset = EducationDataset(
        id="dummy_stem",
        title="テストデータ",
        category="math",
        region="japan",
        source_name="文科省",
        source_url="https://example.com",
        description="テスト",
        df=df,
        metrics=["入学者総数", "女性比率"],
        time_col="年度",
        unit="人",
    )

    analysis = EduDataAnalyzer().analyze(dataset)
    # Manually simulate a fatal flaw pair
    analysis.correlations = [
        CorrelationResult(
            metric_x="入学者総数",
            metric_y="女性比率",
            pearson_r=0.999,
            p_value=0.0001,
            interpretation="極めて強い相関",
            bf10=9999.0,
            bf_interpretation="極めて強い証拠",
        )
    ]
    paper = AcademicPaper(
        title="大学定員増と女性比率の推移",
        subtitle="副題",
        abstract="本稿は入学者総数と女性比率の相関を分析した。",
        keywords=["情報科学", "定員", "ジェンダー"],
        background="背景記述",
        objectives="RQ検証",
        methodology="相関分析",
        results_text="入学者総数と女性比率の間に極めて強い正の相関が認められた。",
        discussion="考察",
        references=["Ref 1"],
    )

    review_gen = PeerReviewGenerator()
    review = review_gen.generate_review(paper, dataset, analysis)

    assert review.decision == "不採録（Reject）"
    assert "不採録" in review.overall_critique
    assert "比率擬似相関" in review.overall_critique or "アーティファクト" in review.overall_critique
    grade, comment = review.scores["信頼性・統計的妥当性"]
    assert grade in ["D", "F"]

