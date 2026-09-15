"""
Unit tests for Citation and Reference Synchronization in Academic Papers.
Validates 100% bidirectional citation parity across all 8 educational datasets.
"""
import re
import pytest

from src.academic_contexts import DATASET_ACADEMIC_CONTEXTS
from src.academic_paper import (
    AcademicPaper,
    AcademicPaperGenerator,
    extract_in_text_citations,
    resolve_missing_reference,
    synchronize_citations_and_references,
    sort_jset_references,
)
from src.analyzer import EduDataAnalyzer
from src.fetchers.catalog import DatasetCatalog


def test_extract_in_text_citations_patterns():
    text = (
        "先行研究において，Bandura (1997) や Pekrun (2006) は情意面の重要性を指摘している．"
        "我が国でも文部科学省 (2018) や国立教育政策研究所 (2020) の指針に基づき推進されている（清水，2020）．"
        "国際比較（TIMSS；Mullis et al.，2020）や小中接続の知見（中川・村井，2018；豊福，2023）とも整合的である．"
        "さらに，Tschannen-Moran & Hoy (2001) の効力感理論や，Hanushek & Woessmann (2015) の教育生産関数にも合致する．"
    )
    citations = extract_in_text_citations(text)
    years = [y for a, y in citations]
    assert "1997" in years
    assert "2006" in years
    assert "2018" in years
    assert "2020" in years
    assert "2023" in years
    assert "2001" in years
    assert "2015" in years

    # Check author extraction
    authors = [a for a, y in citations]
    assert any("Bandura" in a for a in authors)
    assert any("Pekrun" in a for a in authors)
    assert any("清水" in a for a in authors)
    assert any("Mullis" in a for a in authors)
    assert any("中川" in a for a in authors)
    assert any("Tschannen-Moran" in a for a in authors)
    assert any("Woessmann" in a for a in authors)


@pytest.mark.parametrize("dataset_id", list(DATASET_ACADEMIC_CONTEXTS.keys()))
def test_bidirectional_citation_parity_for_all_datasets(dataset_id):
    """
    Every in-text citation in fallback_background & fallback_discussion
    MUST be in curated_references, and every curated_reference MUST be cited in the text.
    """
    ctx = DATASET_ACADEMIC_CONTEXTS[dataset_id]
    text = (ctx.fallback_background or "") + "\n" + (ctx.fallback_discussion or "")
    refs = ctx.curated_references or []

    assert len(refs) >= 8, f"{dataset_id} must have at least 8 curated references"

    # 1. In-text citations -> must exist in refs
    in_text_cites = extract_in_text_citations(text)
    assert len(in_text_cites) >= 6, f"{dataset_id} must have at least 6 in-text citations"

    for author_str, year in in_text_cites:
        parts = [
            p.strip()
            for p in re.split(r"[\s,・＆&]+|and", author_str)
            if p.strip() and p.lower() not in ["et", "al", "al."]
        ]
        matched = False
        for r in refs:
            if year in r:
                if any(p.lower() in r.lower() for p in parts):
                    matched = True
                    break
        assert (
            matched
        ), f"In-text citation '{author_str} ({year})' in {dataset_id} is missing from curated_references!"

    # 2. Curated references -> must be cited in text
    for r in refs:
        # Extract author raw and year
        m = re.search(r"^([^\(（]+)[\(（]([12][09]\d\d)[\)）]", r.strip())
        assert m is not None, f"Could not parse reference year: {r}"
        authors_raw = m.group(1).strip()
        year = m.group(2).strip()

        # Extract surname keywords
        names = []
        for org in [
            "文部科学省",
            "国立教育政策研究所",
            "大学入試センター",
            "経済産業省",
            "OECD",
            "UNESCO",
            "ITU",
            "World Bank",
        ]:
            if org.lower() in authors_raw.lower():
                names.append(org)
        for part in re.split(r"[,，、・\s&]+|and", authors_raw):
            part = part.strip()
            if not part:
                continue
            if re.match(r"^[A-Za-z]+$", part) and len(part) > 1:
                names.append(part)
            elif re.match(r"^[\u4e00-\u9faf]+$", part):
                if part.startswith("八木澤") or part.startswith("八木沢"):
                    names.append("八木澤")
                    names.append("八木沢")
                elif len(part) >= 2:
                    names.append(part[:2])
                    names.append(part)

        assert year in text, f"Reference '{r}' (year {year}) is not cited in {dataset_id} body text!"
        name_found = any(n.lower() in text.lower() for n in names)
        assert (
            name_found
        ), f"Reference author from '{r}' ({names}) is not cited in {dataset_id} body text!"


def test_synchronize_citations_and_references_heals_missing_entries():
    """
    Simulates an LLM omitting references from the JSON references list
    despite citing them in the text. Verifies that synchronize_citations_and_references
    automatically detects and resolves the missing references.
    """
    paper = AcademicPaper(
        title="テスト論文†",
        subtitle="テスト副題",
        abstract="要旨",
        keywords=["テスト"],
        background="本研究では，堀田 (2021) や Mullis et al. (2020) の知見に着目した．",
        objectives="・RQ1: テスト\n・RQ2: テスト",
        methodology="手法",
        results_text="結果",
        discussion="小柳 (2021) および黒上 (2020) の指摘通り，主体的学びが重要である．",
        references=[],  # Completely empty references list!
    )

    synced = synchronize_citations_and_references(paper, "japan_national_assessment_math")

    # All 4 cited authors must now appear in paper.references!
    ref_text = "\n".join(synced.references)
    assert "堀田龍也" in ref_text
    assert "MULLIS" in ref_text
    assert "小柳和喜雄" in ref_text
    assert "黒上晴夫" in ref_text
    assert len(synced.references) >= 4


def test_synchronize_citations_and_references_synthesizes_unknown_author():
    """
    If an author citation is not found in any database, a clean JSET reference must be synthesized.
    """
    paper = AcademicPaper(
        title="未知の文献テスト†",
        subtitle="副題",
        abstract="要旨",
        keywords=["テスト"],
        background="架空の研究として，新未知研究者 (2025) は新しい教育AI手法を提案した．",
        objectives="・RQ1: テスト\n・RQ2: テスト",
        methodology="手法",
        results_text="結果",
        discussion="考察",
        references=[],
    )

    synced = synchronize_citations_and_references(paper, "japan_timss_math_science")
    ref_text = "\n".join(synced.references)
    assert "新未知研究者" in ref_text
    assert "2025" in ref_text
    assert len(synced.references) >= 1


def test_academic_paper_generator_parity_end_to_end():
    catalog = DatasetCatalog()
    analyzer = EduDataAnalyzer()
    generator = AcademicPaperGenerator()

    for ds_id in ["japan_national_assessment_math", "japan_mext_ict_informatization"]:
        dataset = catalog.get_by_id(ds_id)
        analysis = analyzer.analyze(dataset)
        paper = generator.generate_paper(dataset, analysis)

        # Check that all in-text citations are in paper.references
        full_text = paper.background + "\n" + paper.discussion
        cites = extract_in_text_citations(full_text)
        assert len(cites) >= 6

        for a, y in cites:
            parts = [
                p.strip()
                for p in re.split(r"[\s,・＆&]+|and", a)
                if p.strip() and p.lower() not in ["et", "al", "al."]
            ]
            matched = False
            for r in paper.references:
                if y in r and any(p.lower() in r.lower() for p in parts):
                    matched = True
                    break
            assert matched, f"In paper for {ds_id}, '{a} ({y})' is missing from paper.references!"
