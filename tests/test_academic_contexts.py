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
from src.insights import GeminiInsightGenerator
from src.peer_review import PeerReviewGenerator
from src.utils import LLMGenerationError


def test_academic_contexts_completeness_for_all_datasets():
    """Verifies that all 8 datasets in catalog have distinct, rigorous academic contexts."""
    catalog = DatasetCatalog()
    datasets = catalog.get_all_datasets()
    assert len(datasets) == 14

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
        assert len(ctx.curated_references) >= 3

        # Uniqueness check across datasets
        assert ctx.academic_topic not in seen_topics, f"Duplicate topic: {ctx.academic_topic}"
        seen_topics.add(ctx.academic_topic)
        assert ctx.theoretical_framework not in seen_frameworks, f"Duplicate framework: {ctx.theoretical_framework}"
        seen_frameworks.add(ctx.theoretical_framework)

        # The fictitious journal IDs must never appear. The real journal title
        # "日本教育工学会論文誌" is allowed in a reference (verified citation of an existing article).
        for ref in ctx.curated_references:
            assert "Jpn．J．Educ．Technol．" not in ref and "Vol． XX，Suppl．" not in ref, f"Fictitious journal ID in reference: {ref}"

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


@pytest.mark.no_template_standin
def test_claude_failure_without_gemini_raises_instead_of_template():
    """If Claude fails and Gemini is unavailable, paper generation fails loudly (no template text)."""
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analysis = EduDataAnalyzer().analyze(dataset)

    gen = AcademicPaperGenerator(anthropic_api_key="dummy-sk-ant-key", gemini_api_key="")
    gen.gemini_client = None
    with patch.object(gen, "_generate_with_claude", side_effect=Exception("Anthropic 401 Unauthorized")):
        with pytest.raises(LLMGenerationError, match="Anthropic 401"):
            gen.generate_paper(dataset, analysis)


@pytest.mark.no_template_standin
def test_peer_review_claude_failure_raises_instead_of_template():
    """Peer review fails loudly too when no language model answers."""
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_high_school_informatics")
    analysis = EduDataAnalyzer().analyze(dataset)
    paper = AcademicPaperGenerator()._generate_template_fallback(dataset, analysis)

    rev_gen = PeerReviewGenerator(anthropic_api_key="dummy-sk-ant-key", gemini_api_key="")
    rev_gen.gemini_client = None
    with patch.object(rev_gen, "_generate_with_claude", side_effect=Exception("Anthropic 401 Unauthorized")):
        with pytest.raises(LLMGenerationError, match="Anthropic 401"):
            rev_gen.generate_review(paper, dataset, analysis)


@pytest.mark.no_template_standin
def test_insights_without_any_key_raise():
    """No API key at all is an error, not a silent template."""
    catalog = DatasetCatalog()
    dataset = catalog.get_by_id("japan_national_assessment_math")
    analysis = EduDataAnalyzer().analyze(dataset)
    gen = GeminiInsightGenerator(gemini_api_key="", anthropic_api_key="")
    gen.gemini_client = None
    with pytest.raises(LLMGenerationError):
        gen.generate_insights(dataset, analysis)


@pytest.mark.no_template_standin
def test_insights_missing_fields_are_an_error():
    """A model reply that lacks a field is rejected instead of being patched with template text."""
    with pytest.raises(LLMGenerationError):
        GeminiInsightGenerator._require_insight_fields({"executive_summary": "x" * 30}, "Claude")
    ok = GeminiInsightGenerator._require_insight_fields(
        {"executive_summary": "a" * 30, "counter_intuitive_finding": "b" * 30,
         "pedagogical_implications": "c" * 30, "future_challenges_and_policy": "d" * 30}, "Claude")
    assert len(ok) == 4


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

