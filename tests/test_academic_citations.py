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
    UnverifiedCitationError,
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
def test_in_text_citations_are_in_curated_references(dataset_id):
    """
    Every in-text citation in fallback_background & fallback_discussion must be in curated_references.
    (curated_references itself is gated by test_curated_references_are_verified.)
    """
    ctx = DATASET_ACADEMIC_CONTEXTS[dataset_id]
    text = (ctx.fallback_background or "") + "\n" + (ctx.fallback_discussion or "")
    refs = ctx.curated_references or []

    assert len(refs) >= 3, f"{dataset_id} must have at least 3 curated references"

    for author_str, year in extract_in_text_citations(text):
        parts = [
            p.strip()
            for p in re.split(r"[\s,・＆&]+|and", author_str)
            if p.strip() and p.lower() not in ["et", "al", "al."]
        ]
        matched = any(
            year in r and any(p.lower() in r.lower() for p in parts) for r in refs
        )
        assert (
            matched
        ), f"In-text citation '{author_str} ({year})' in {dataset_id} is missing from curated_references!"


def test_curated_references_are_verified():
    """
    A reference may be listed only if its existence was confirmed against an outside source
    and registered, with the evidence, in data/references_verified.json (2026-10-05:
    most of the earlier Japanese journal references could not be found and were removed).
    """
    import json
    from pathlib import Path

    reg = json.loads((Path(__file__).resolve().parent.parent / "data" / "references_verified.json").read_text(encoding="utf-8"))
    verified = {e["reference"] for e in reg["references"]}
    lists = [(k, c.curated_references) for k, c in DATASET_ACADEMIC_CONTEXTS.items()]
    from src.academic_contexts import DATASET_RESEARCH_ANGLES
    lists += [(k, a.curated_references) for k, angs in DATASET_RESEARCH_ANGLES.items() for a in angs]
    for ds, refs in lists:
        for r in refs:
            assert r in verified, f"Unverified reference in {ds}: {r}"



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
        discussion="Wigfield & Eccles (2000) および国立教育政策研究所 (2024) の指摘通り，主体的学びが重要である．",
        references=[],  # Completely empty references list!
    )

    synced = synchronize_citations_and_references(paper, "japan_national_assessment_math")

    # All 4 cited authors must now appear in paper.references!
    ref_text = "\n".join(synced.references)
    assert "堀田龍也" in ref_text
    assert "MULLIS" in ref_text
    assert "WIGFIELD" in ref_text
    assert "国立教育政策研究所 (2024)" in ref_text
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

    # An unknown citation must stop the paper; no reference is ever synthesized.
    with pytest.raises(UnverifiedCitationError):
        synchronize_citations_and_references(paper, "japan_timss_math_science")
    assert paper.references == []


def test_synchronize_drops_references_the_model_wrote_itself():
    paper = AcademicPaper(
        title="テスト†",
        subtitle="副題",
        abstract="要旨",
        keywords=["テスト"],
        background="Wigfield & Eccles (2000) の期待―価値理論を参照する．",
        objectives="・RQ1: テスト\n・RQ2: テスト",
        methodology="手法",
        results_text="結果",
        discussion="考察",
        references=["架空太郎 (2021) 存在しない論文. 架空学会誌, <b>1</b> (1) ：1-10."],
    )
    synced = synchronize_citations_and_references(paper, "japan_national_assessment_math")
    assert not any("架空太郎" in r for r in synced.references)
    assert any("WIGFIELD" in r for r in synced.references)


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
        assert len(cites) >= 2

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
