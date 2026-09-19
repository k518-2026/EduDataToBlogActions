"""
Tests for Deduplication, Multi-Angle Research Diversity, and Topic Rotation.
Verifies that:
1. All 12 datasets have multiple scholarly research angles.
2. Angle rotation selects unposted or least-recently-used angles.
3. Storage persists angle metadata and retrieves recent research topics.
4. Dynamic report titles reflect selected_angle.title_theme.
5. Anti-duplication negative prompts are properly injected into LLM prompt builders.
6. Template fallbacks for paper and peer review dynamically adapt to the selected angle.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from src.academic_contexts import (
    DATASET_ACADEMIC_CONTEXTS,
    DATASET_RESEARCH_ANGLES,
    get_academic_context,
    get_all_angles_for_dataset,
)
from src.academic_paper import AcademicPaperGenerator
from src.analyzer import EduDataAnalyzer
from src.fetchers.base import EducationDataset
from src.fetchers.catalog import DatasetCatalog
from src.insights import GeminiInsightGenerator
from src.peer_review import PeerReviewGenerator
from src.reporter import EduReportBuilder, GeneratedReport
from src.storage import ReportStorage


class TestDiversityManager:
    """Comprehensive test suite for research topic deduplication and angle diversity."""

    def test_all_12_datasets_have_multiple_angles(self):
        """Every dataset in the catalog must have at least 2 distinct academic angles."""
        catalog = DatasetCatalog()
        datasets = catalog.get_all_datasets()
        assert len(datasets) == 12, f"Expected 12 datasets, got {len(datasets)}"

        for d in datasets:
            angles = get_all_angles_for_dataset(d.id)
            assert len(angles) >= 2, f"Dataset '{d.id}' has fewer than 2 angles: {len(angles)}"
            
            # Check required fields on each angle
            angle_ids = set()
            for ang in angles:
                assert ang.angle_id, f"Angle in dataset '{d.id}' missing angle_id"
                assert ang.angle_id not in angle_ids, f"Duplicate angle_id '{ang.angle_id}' in '{d.id}'"
                angle_ids.add(ang.angle_id)
                assert ang.angle_name, f"Angle '{ang.angle_id}' missing angle_name"
                assert ang.title_theme, f"Angle '{ang.angle_id}' missing title_theme"
                assert ang.theoretical_framework, f"Angle '{ang.angle_id}' missing theoretical_framework"
                assert len(ang.focus_metrics) >= 1, f"Angle '{ang.angle_id}' missing focus_metrics"
                assert len(ang.curated_references) >= 6, f"Angle '{ang.angle_id}' has insufficient references"

    def test_angle_selection_and_rotation(self):
        """Selecting an angle for a dataset rotates to unposted angle or least-recently used."""
        catalog = DatasetCatalog()
        dataset_id = "japan_timss_math_science"
        all_angles = get_all_angles_for_dataset(dataset_id)
        assert len(all_angles) >= 2

        # 1. No history: returns primary angle (angle 1)
        _, angle_first = catalog.select_dataset_and_angle(
            posted_history=[], dataset_id=dataset_id, force=True
        )
        assert angle_first.angle_id == all_angles[0].angle_id

        # 2. Angle 1 already posted: returns angle 2
        history_angle1 = [
            {"dataset_id": dataset_id, "angle_id": all_angles[0].angle_id, "title": "Test 1"}
        ]
        _, angle_second = catalog.select_dataset_and_angle(
            posted_history=history_angle1, dataset_id=dataset_id, force=True
        )
        assert angle_second.angle_id == all_angles[1].angle_id

        # 3. Both angles posted: wraps around to least recently used (angle 1)
        history_both = [
            {"dataset_id": dataset_id, "angle_id": all_angles[0].angle_id, "title": "Test 1"},
            {"dataset_id": dataset_id, "angle_id": all_angles[1].angle_id, "title": "Test 2"},
        ]
        _, angle_wrap = catalog.select_dataset_and_angle(
            posted_history=history_both, dataset_id=dataset_id, force=True
        )
        assert angle_wrap.angle_id == all_angles[0].angle_id

    def test_storage_deduplication_memory(self, tmp_path):
        """Storage records angle_id and angle_name, and extracts recent research topics."""
        history_file = tmp_path / "test_posted_reports.json"
        archive_file = tmp_path / "test_archive.md"
        storage = ReportStorage(json_path=history_file, archive_path=archive_file)

        # Record a post with angle info
        report1 = GeneratedReport(
            title="TIMSS分析：自己効力感の罠",
            html_content="<p>test</p>",
            markdown_content="# test",
            categories=["算数数学"],
            tags=["オープンデータ"],
            chart_path=Path("chart1.png"),
            dataset_id="japan_timss_math_science",
            created_at="2026-09-18",
            angle_id="timss_affective_decline",
            angle_name="情意面（自己効力感・好意度）の推移とTIMSSパラドックス",
        )
        storage.record_post(report1, platform="markdown_only")

        # Record a second post
        report2 = GeneratedReport(
            title="GIGA端末活用分析：活用の自治体格差",
            html_content="<p>test2</p>",
            markdown_content="# test2",
            categories=["情報教育"],
            tags=["オープンデータ"],
            chart_path=Path("chart2.png"),
            dataset_id="japan_mext_ict_informatization",
            created_at="2026-09-19",
            angle_id="mext_ict_utilization_gap",
            angle_name="1人1台端末の日常活用頻度と地域間格差（セカンド・デジタルデバイド）",
        )
        storage.record_post(report2, platform="markdown_only")

        # Verify get_past_angles_for_dataset
        past_angles_timss = storage.get_past_angles_for_dataset("japan_timss_math_science")
        assert past_angles_timss == ["timss_affective_decline"]

        # Verify get_recent_research_topics
        recent = storage.get_recent_research_topics(limit=5)
        assert len(recent) == 2
        assert recent[0]["dataset_id"] == "japan_mext_ict_informatization"
        assert recent[0]["angle_id"] == "mext_ict_utilization_gap"
        assert recent[1]["dataset_id"] == "japan_timss_math_science"
        assert recent[1]["angle_id"] == "timss_affective_decline"

    def test_dynamic_report_title_theme(self):
        """Report title must integrate selected_angle.title_theme."""
        catalog = DatasetCatalog()
        dataset = catalog.get_by_id("japan_timss_math_science")
        angle = get_academic_context("japan_timss_math_science", angle_id="timss_problem_solving_cognitive")

        builder = EduReportBuilder()
        insights_mock = MagicMock()
        insights_mock.executive_summary = "サマリー"
        insights_mock.pedagogical_implications = "示唆"
        insights_mock.future_challenges_and_policy = "課題"
        insights_mock.counter_intuitive_finding = "逆説"

        analysis_mock = MagicMock()
        analysis_mock.descriptive_stats = {}
        analysis_mock.trends = []
        analysis_mock.correlations = []
        analysis_mock.key_insights = []

        report = builder.build_report(
            dataset=dataset,
            analysis=analysis_mock,
            insights=insights_mock,
            chart_path=Path("test.png"),
            selected_angle=angle,
        )

        assert angle.title_theme in report.title
        assert report.angle_id == angle.angle_id
        assert report.angle_name == angle.angle_name

    def test_prompt_builders_inject_anti_duplication_constraints(self):
        """Insight and AcademicPaper prompt builders inject angle info and anti-duplication constraints."""
        catalog = DatasetCatalog()
        dataset = catalog.get_by_id("japan_timss_math_science")
        angle = get_academic_context("japan_timss_math_science", angle_id="timss_problem_solving_cognitive")
        past_topics = [
            {"title": "過去レポート1", "angle_name": "情意面（自己効力感・好意度）の推移"},
            {"title": "過去レポート2", "angle_name": "一般"},
        ]

        analysis = EduDataAnalyzer().analyze(dataset)

        # 1. Test Insight Generator Prompt
        insight_gen = GeminiInsightGenerator(gemini_api_key="", anthropic_api_key="")
        insight_prompt = insight_gen._build_insight_prompt(
            dataset=dataset, analysis=analysis, selected_angle=angle, past_topics=past_topics
        )
        assert "本レポート固有の研究アングル・焦点（最重要）" in insight_prompt
        assert angle.angle_name in insight_prompt
        assert "過去の投稿内容との重複排除・新規性担保の厳格指示" in insight_prompt
        assert "過去レポート1" in insight_prompt
        assert "厳格に禁止" in insight_prompt

        # 2. Test Academic Paper Generator Prompt
        paper_gen = AcademicPaperGenerator(gemini_api_key="", anthropic_api_key="")
        paper_prompt = paper_gen._build_academic_prompt(
            dataset=dataset, analysis=analysis, selected_angle=angle, past_topics=past_topics
        )
        assert f"本研究の研究アングル: {angle.angle_name}" in paper_prompt
        assert "過去の研究内容との重複排除・新規性担保の厳格指示" in paper_prompt
        assert "過去レポート1" in paper_prompt
        assert "厳格に禁止" in paper_prompt

    def test_template_fallbacks_adapt_to_selected_angle(self):
        """Academic paper and peer review template fallbacks dynamically adapt to selected angle."""
        catalog = DatasetCatalog()
        dataset = catalog.get_by_id("oecd_talis_teacher_survey")
        angle = get_academic_context("oecd_talis_teacher_survey", angle_id="talis_critical_thinking_instruction")

        analysis = EduDataAnalyzer().analyze(dataset)

        # Paper fallback
        paper_gen = AcademicPaperGenerator(gemini_api_key="", anthropic_api_key="")
        paper = paper_gen._generate_template_fallback(dataset, analysis, selected_angle=angle)
        assert angle.fallback_title in paper.title
        assert angle.title_en == paper.title_en

        # Peer review fallback
        review_gen = PeerReviewGenerator(gemini_api_key="", anthropic_api_key="")
        review = review_gen._generate_template_fallback(paper, dataset, analysis, selected_angle=angle)
        assert review.overall_critique == angle.fallback_review_critique
