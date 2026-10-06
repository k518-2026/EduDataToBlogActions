"""Test-only stand-in for the language models.

Production code never publishes template text: when every language model fails it raises
LLMGenerationError. The unit tests, however, run offline and need a deterministic paper/review/insight
to exercise the PDF, report and audit code. So by default the three generate_* methods fall back to
the (test-only) template builders. Tests that check the "fail loudly" policy opt out with
@pytest.mark.no_template_standin.
"""
import pytest

from src.academic_paper import AcademicPaperGenerator
from src.insights import GeminiInsightGenerator
from src.peer_review import PeerReviewGenerator
from src.utils import LLMGenerationError


def pytest_configure(config):
    config.addinivalue_line("markers", "no_template_standin: do not substitute templates for failed LLM calls")
    config.addinivalue_line("markers", "verified_gate: run with the verified-data gate enabled")


@pytest.fixture(autouse=True)
def no_real_llm_calls(monkeypatch):
    """The tests never call a real language model (the local .env holds real API keys and an Ollama server)."""
    from src.config import Config

    monkeypatch.setattr(Config, "OLLAMA_BASE_URL", "")
    monkeypatch.setattr(Config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(Config, "GEMINI_API_KEY", "")


@pytest.fixture(autouse=True)
def template_standin(request, monkeypatch):
    if request.node.get_closest_marker("no_template_standin"):
        return

    orig_insights = GeminiInsightGenerator.generate_insights
    orig_paper = AcademicPaperGenerator.generate_paper
    orig_review = PeerReviewGenerator.generate_review

    def insights(self, dataset, analysis, selected_angle=None, past_topics=None):
        try:
            return orig_insights(self, dataset, analysis, selected_angle=selected_angle, past_topics=past_topics)
        except LLMGenerationError:
            return self._generate_template_fallback(dataset, analysis, selected_angle=selected_angle)

    def paper(self, dataset, analysis, selected_angle=None, past_topics=None):
        try:
            return orig_paper(self, dataset, analysis, selected_angle=selected_angle, past_topics=past_topics)
        except LLMGenerationError:
            return self._generate_template_fallback(dataset, analysis, selected_angle=selected_angle)

    def review(self, paper, dataset, analysis, selected_angle=None):
        try:
            return orig_review(self, paper, dataset, analysis, selected_angle=selected_angle)
        except LLMGenerationError:
            audit = self.audit_paper_integrity(paper, dataset, analysis, selected_angle=selected_angle)
            report = self._generate_template_fallback(
                paper, dataset, analysis, selected_angle=selected_angle, audit_issues=audit
            )
            return self._enforce_rejection_for_fatal_flaws(report, audit) if audit else report

    monkeypatch.setattr(GeminiInsightGenerator, "generate_insights", insights)
    monkeypatch.setattr(AcademicPaperGenerator, "generate_paper", paper)
    monkeypatch.setattr(PeerReviewGenerator, "generate_review", review)


@pytest.fixture(autouse=True)
def allow_unverified_data(request, monkeypatch):
    """Most tests exercise code with the (unverified) catalog entries; the gate tests opt out."""
    if request.node.get_closest_marker("verified_gate"):
        monkeypatch.delenv("ALLOW_UNVERIFIED_DATA", raising=False)
    else:
        monkeypatch.setenv("ALLOW_UNVERIFIED_DATA", "true")
