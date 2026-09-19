"""
Tests for academic contexts across all 8 datasets, anti-cliché constraints,
and Claude/Gemini generation fallback hierarchy.
"""
from unittest.mock import patch
import pytest

from src.academic_contexts import DATASET_ACADEMIC_CONTEXTS, get_academic_context
from src.academic_paper import AcademicPaperGenerator
from src.analyzer import EduDataAnalyzer
from src.fetchers.catalog import DatasetCatalog
from src.peer_review import PeerReviewGenerator


def test_academic_contexts_completeness_for_all_datasets():
    """Verifies that all 8 datasets in catalog have distinct, rigorous academic contexts."""
    catalog = DatasetCatalog()
    datasets = catalog.get_all_datasets()
    assert len(datasets) == 12

    seen_topics = set()
    seen_frameworks = set()

    for ds in datasets:
        ctx = get_academic_context(ds.id, ds.category)
        assert ctx.dataset_id == ds.id
        assert len(ctx.academic_topic) > 10
        assert len(ctx.theoretical_framework) > 10
        assert len(ctx.core_research_problems) > 30
        assert len(ctx.banned_cliches) >= 3
        assert len(ctx.specific_prompt_guidance) > 30
        assert len(ctx.curated_references) >= 8

        # Uniqueness check across datasets
        assert ctx.academic_topic not in seen_topics, f"Duplicate topic: {ctx.academic_topic}"
        seen_topics.add(ctx.academic_topic)
        assert ctx.theoretical_framework not in seen_frameworks, f"Duplicate framework: {ctx.theoretical_framework}"
        seen_frameworks.add(ctx.theoretical_framework)

        # No forbidden society names in curated references
        for ref in ctx.curated_references:
            assert "日本教育工学会" not in ref, f"Forbidden society name found in reference: {ref}"

        # Fallback background checks
        assert len(ctx.fallback_background) >= 400
        for cliche in ctx.banned_cliches:
            assert cliche not in ctx.fallback_background, f"Banned cliche '{cliche}' found in background of {ds.id}!"

        # Fallback objectives checks
        assert "・RQ1" in ctx.fallback_objectives
        assert "・RQ2" in ctx.fallback_objectives
        assert "RQ3" not in ctx.fallback_objectives

        # Fallback discussion checks
        assert "RQ1" in ctx.fallback_discussion and "RQ2" in ctx.fallback_discussion
        assert ctx.fallback_discussion.index("RQ1") < ctx.fallback_discussion.index("RQ2")
        assert ("同じところ" in ctx.fallback_discussion or "共通点" in ctx.fallback_discussion)
        assert ("違うところ" in ctx.fallback_discussion or "相違点" in ctx.fallback_discussion)
        assert "今後の課題" in ctx.fallback_discussion

        # Fallback peer review checks
        assert len(ctx.fallback_review_critique) > 50
        assert len(ctx.fallback_major_revisions) >= 3
        assert len(ctx.fallback_minor_revisions) >= 2
        assert len(ctx.fallback_questions_to_authors) >= 2


def test_claude_generation_graceful_fallback():
    """Verifies that if Claude API fails, AcademicPaperGenerator gracefully falls back to Gemini or template."""
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    # Initialize generator with dummy Anthropic key
    gen = AcademicPaperGenerator(anthropic_api_key="dummy-sk-ant-key")

    # Mock Claude failure (e.g. invalid key 401 HTTP error)
    with patch.object(gen, "_generate_with_claude", side_effect=Exception("Anthropic 401 Unauthorized")):
        paper = gen.generate_paper(dataset, analysis)
        assert paper is not None
        assert len(paper.title) > 0
        assert len(paper.background) >= 400


def test_peer_review_claude_graceful_fallback():
    """Verifies that if Claude API fails, PeerReviewGenerator gracefully falls back to Gemini or template."""
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_high_school_informatics")
    analyzer = EduDataAnalyzer()
    analysis = analyzer.analyze(dataset)

    paper_gen = AcademicPaperGenerator()
    paper = paper_gen.generate_paper(dataset, analysis)

    rev_gen = PeerReviewGenerator(anthropic_api_key="dummy-sk-ant-key")
    with patch.object(rev_gen, "_generate_with_claude", side_effect=Exception("Anthropic 401 Unauthorized")):
        review = rev_gen.generate_review(paper, dataset, analysis)
        assert review is not None
        assert "条件付採録" in review.decision
        assert len(review.major_revisions) >= 3


def test_resolve_anthropic_model_logic():
    """Tests intelligent model selection from available models list."""
    from src.utils import resolve_anthropic_model

    # When API call returns mock model list
    with patch("src.utils.get_available_anthropic_models", return_value=["claude-3-5-haiku-20241022", "claude-sonnet-5", "claude-opus-5"]):
        # Preferred model exists
        assert resolve_anthropic_model("key", "claude-sonnet-5") == "claude-sonnet-5"
        # Preferred model is deprecated / doesn't exist -> resolves to available Sonnet 5
        assert resolve_anthropic_model("key", "claude-3-5-sonnet-20241022") == "claude-sonnet-5"

    # When API call fails / empty
    with patch("src.utils.get_available_anthropic_models", return_value=[]):
        assert resolve_anthropic_model("key", "claude-sonnet-5") == "claude-sonnet-5"

