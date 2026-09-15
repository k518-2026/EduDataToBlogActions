"""
Unit tests for Academic Paper and PDF Generator modules.
"""
from pathlib import Path
import pytest

from src.academic_paper import (
    AcademicPaperGenerator,
    AcademicPaper,
    normalize_jset_text,
    sort_jset_references,
    normalize_jset_reference,
    get_jset_author_sort_key,
)
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


def test_category_box_is_generative_ai_paper():
    """Verifies that the paper category label is '生成AI論文'."""
    pdf_gen_file = Path("src/pdf/pdf_generator.py").read_text(encoding="utf-8")
    assert "生成AI論文" in pdf_gen_file
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

        # 1. Background cites >= 2 foreign sources, >= 4 total citations, and has detailed explanation (> 400 chars)
        foreign_keywords = ["OECD", "TIMSS", "Mullis", "UNESCO", "Wing", "PISA"]
        found_foreign = [kw for kw in foreign_keywords if kw in paper.background]
        assert len(found_foreign) >= 2, f"Expected >= 2 foreign citations in background for {dataset_id}, found: {found_foreign}"
        assert len(paper.background) >= 400, f"Expected detailed background (>=400 chars), found: {len(paper.background)}"
        assert "文部科学省" in paper.background, f"Expected domestic policy citation in background for {dataset_id}"

        # 2. Exactly 2 RQs (RQ1, RQ2 on separate lines, RQ3 must not exist)
        rq_lines = [line.strip() for line in paper.objectives.split("\n") if any(line.startswith(f"・{k}") or line.startswith(k) for k in ["RQ1", "RQ2", "RQ3"])]
        assert len(rq_lines) == 2, f"Expected exactly 2 RQ lines in objectives for {dataset_id}, found: {rq_lines}"
        assert "RQ1" in rq_lines[0] and "RQ2" in rq_lines[1]
        assert "RQ3" not in paper.objectives, f"RQ3 must not exist in {dataset_id}"
        for line in rq_lines:
            assert line.startswith("・"), f"RQ line should start with bullet: {line}"

        # 3. References >= 8
        assert len(paper.references) >= 8, f"Expected >= 8 references for {dataset_id}, found: {len(paper.references)}"

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

        # 6. Discussion cites >= 2 prior studies for RQ1 and >= 2 prior studies for RQ2
        rq1_disc = paper.discussion[:paper.discussion.index("RQ2")]
        rq2_disc = paper.discussion[paper.discussion.index("RQ2"):]
        if dataset_id == "japan_national_assessment_math":
            assert "清水" in rq1_disc and "小柳" in rq1_disc, "RQ1 discussion in Math must cite 清水 and 小柳"
            assert "堀田" in rq2_disc and "黒上" in rq2_disc, "RQ2 discussion in Math must cite 堀田 and 黒上"
        else:
            assert "国立教育政策研究所" in rq1_disc and "中川" in rq1_disc, "RQ1 discussion in ICT must cite 国立教育政策研究所 and 中川"
            assert "堀田" in rq2_disc and "佐藤" in rq2_disc, "RQ2 discussion in ICT must cite 堀田 and 佐藤"



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

    # Verify heading styles do not block frame splitting
    assert pdf_gen.styles["Heading1"].keepWithNext is False
    assert pdf_gen.styles["Heading2"].keepWithNext is False
    assert pdf_gen.styles["Heading3"].keepWithNext is False

    # Verify document is strictly 4 pages
    pdf_bytes = res_path.read_bytes()
    page_count = (
        pdf_bytes.count(b"/Type /Page\n")
        + pdf_bytes.count(b"/Type/Page\n")
        + pdf_bytes.count(b"/Type /Page ")
    )
    assert page_count == 4, f"Expected exactly 4 pages for short letter, found {page_count}"


def test_sort_jset_references_alphabetical_order():
    """
    Verifies that references are sorted strictly by author surname in alphabetical order
    interleaving Japanese (Romaji surname reading) and English/Foreign authors (A-Z) in a single list,
    and foreign author surnames are in ALL CAPS with 'and'.
    """
    raw_shuffled_refs = [
        "清水静栄 (2020) 算数・数学教育における「数学的な見方・考え方」の育成と授業改善. 日本数学教育学会誌, <b>102</b> (4) : 12-23.",
        "文部科学省・国立教育政策研究所 (2024) 令和6年度 全国学力・学習状況調査 報告書. 国立教育政策研究所.",
        "Mullis, I. V. S., Martin, M. O., Foy, P., Kelly, D. L., & Fishbein, B. (2020) TIMSS 2019 International Results in Mathematics and Science. Boston College, TIMSS & PIRLS International Study Center.",
        "堀田龍也 (2021) 初等中等教育のデジタルトランスフォーメーションの動向と課題. 教育情報研究, <b>37</b> (2) ：15-24.",
        "OECD (2023) PISA 2022 Results (Volume I): The State of Learning and Equity in Education. OECD Publishing, Paris. https://doi.org/10.1787/53f23881-en",
        "黒上晴夫, 小柳和喜雄 (2020) シンキングツールを活用した深い学びの授業改善. 教育工学研究報告集, <b>20</b> (2) ：31-38.",
        "小柳和喜雄 (2019) 算数・数学科における深い学びを実現する問題解決型授業の構成原理. 教育方法学研究, <b>45</b> ：45-56.",
        "文部科学省 (2018) 小学校学習指導要領（平成29年告示）解説 算数編. 東洋館出版社, pp.1-240.",
    ]

    sorted_refs = sort_jset_references(raw_shuffled_refs)

    # 1. Verify exact 8 entries
    assert len(sorted_refs) == 8

    # 2. Verify foreign author normalization
    mullis_entry = [r for r in sorted_refs if "TIMSS 2019" in r][0]
    assert "MULLIS, I. V. S." in mullis_entry, "Foreign author surname should be capitalized"
    assert " and " in mullis_entry, "Co-authors should be joined with 'and'"
    author_part = mullis_entry.split("(2020)")[0]
    assert " & " not in author_part, "Author list should not contain '&'"

    # 3. Verify colon normalization
    shimizu_entry = [r for r in sorted_refs if "清水静栄" in r][0]
    assert "：12-23" in shimizu_entry, "Colon before page range should be full-width '：'"

    # 4. Verify strict alphabetical order by lead author surname Romaji reading
    # 堀田 (Horita: H) -> 黒上 (Kurokami: K) -> 文部科学省 (Monbukagakusho: Mo 2018)
    # -> 文部科学省・国立 (Monbukagakusho: Mo 2024) -> MULLIS (Mu) -> OECD (Oe) -> 小柳 (Oyanagi: Oy) -> 清水 (Shimizu: Sh)
    expected_lead_authors = [
        "堀田",
        "黒上",
        "文部科学省 (2018)",
        "文部科学省・国立教育政策研究所 (2024)",
        "MULLIS",
        "OECD",
        "小柳",
        "清水",
    ]
    for idx, expected in enumerate(expected_lead_authors):
        assert expected in sorted_refs[idx], f"Expected reference {idx+1} to contain '{expected}', got: {sorted_refs[idx]}"


def test_reference_hanging_indent_style():
    """Verifies that the reference style in EduPaperPdfGenerator has the exact JSET 2-character hanging indent."""
    pdf_gen = EduPaperPdfGenerator()
    ref_style = pdf_gen.styles["Reference"]

    assert ref_style.fontSize == 8.5, f"Expected 8.5pt font size, got {ref_style.fontSize}"
    assert ref_style.leftIndent == 17.0, f"Expected 17.0pt leftIndent (2 full-width chars), got {ref_style.leftIndent}"
    assert ref_style.firstLineIndent == -17.0, f"Expected -17.0pt firstLineIndent (hanging indent), got {ref_style.firstLineIndent}"


def test_resolve_metric_unit():
    """Verifies that resolve_metric_unit returns clean singular units without composite slashes."""
    from src.utils import resolve_metric_unit

    assert resolve_metric_unit("算数_平均得点", "点 / %") == "点"
    assert resolve_metric_unit("数学が好き_肯定率", "点 / %") == "%"
    assert resolve_metric_unit("端末利活用率", "%") == "%"
    assert resolve_metric_unit("情報工学入学者数", "人") == "人"
    assert resolve_metric_unit("学校数", "校") == "校"
    assert "/" not in resolve_metric_unit("テスト", "点 / %")


def test_clean_text_spaces():
    """Verifies that clean_text_spaces eliminates stray slashes and spaces while preserving HTML and URLs."""
    from src.utils import clean_text_spaces

    raw_text = "IEA（国際教育到達度評価学会） / 文部科学省・国立教育政策研究所 TIMSS調査"
    cleaned = clean_text_spaces(raw_text)
    assert " / " not in cleaned
    assert "・" in cleaned
    assert "TIMSS" in cleaned

    # Check composite units
    assert clean_text_spaces("平均582.08点 / %") == "平均582.08点"
    assert clean_text_spaces("変化量: +30.00点 / %") == "変化量: +30.00点"

    # Check HTML tags and URLs are preserved
    html_text = "決定係数 <i>R</i><sup>2</sup> = 0.856 https://example.com/test"
    cleaned_html = clean_text_spaces(html_text)
    assert "<i>R</i><sup>2</sup>" in cleaned_html
    assert "https://example.com/test" in cleaned_html


def test_paper_title_and_abstract_across_catalogs(tmp_path):
    """Verifies that titles across all catalog datasets fit within 2 lines and have no '/ %'."""
    from src.pdf.pdf_generator import PRINTABLE_W, ParagraphStyle, Paragraph

    catalog = DatasetCatalog()
    analyzer = EduDataAnalyzer()
    paper_gen = AcademicPaperGenerator()
    pdf_gen = EduPaperPdfGenerator()

    for dataset in catalog.get_all_datasets():
        analysis = analyzer.analyze(dataset)
        paper = paper_gen.generate_paper(dataset, analysis)

        # 1. No '/ %' in title or abstract
        assert "/ %" not in paper.title, f"Found '/ %' in title of {dataset.id}: {paper.title}"
        assert "/ %" not in paper.abstract, f"Found '/ %' in abstract of {dataset.id}: {paper.abstract}"

        # 2. Check title wraps in <= 2 lines
        p_title = Paragraph(paper.title, pdf_gen.styles["PaperTitle"])
        _, h_title = p_title.wrap(PRINTABLE_W, 1000)
        lines = round(h_title / pdf_gen.styles["PaperTitle"].leading)
        assert lines <= 2, f"Title for {dataset.id} exceeded 2 lines ({lines} lines): '{paper.title}'"


