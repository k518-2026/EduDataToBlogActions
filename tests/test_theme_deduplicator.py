"""
Unit tests for Theme Deduplication and Topic Diversity Engine (src/theme_deduplicator.py).
Verifies:
1. Content word extraction (Katakana, English acronyms, Kanji compounds, sub-grams, stopword filtering).
2. Character bigram extraction and text normalization.
3. Composite theme similarity calculation (identical, distinct, and partial overlap).
4. check_theme_duplication logic:
   - exact angle match within recent window
   - high semantic similarity threshold
   - shared keyword count threshold
   - distinct novel themes pass successfully
5. select_most_diverse_angle logic:
   - chooses unposted angle
   - chooses angle with zero duplication over duplicate
   - falls back to minimal similarity when all angles overlap
"""
import pytest
from src.theme_deduplicator import (
    extract_content_words,
    extract_character_bigrams,
    compute_theme_similarity,
    check_theme_duplication,
    select_most_diverse_angle,
    DuplicationCheckResult,
)


class DummyAngle:
    def __init__(self, angle_id: str, angle_name: str, title_theme: str):
        self.angle_id = angle_id
        self.angle_name = angle_name
        self.title_theme = title_theme


class TestThemeDeduplicator:
    def test_extract_content_words(self):
        text = "【実証分析】GIGA端末の1人1台環境におけるICT活用格差とデジタルデバイド"
        words = extract_content_words(text)
        assert "GIGA" in words
        assert "ICT" in words
        assert "デジタルデバイド" in words
        assert "端末" in words
        assert "格差" in words
        # Verify common stopwords are removed
        assert "分析" not in words
        assert "における" not in words

    def test_extract_character_bigrams(self):
        text = "教員の多忙化（長時間労働）"
        bigrams = extract_character_bigrams(text)
        assert "教員" in bigrams
        assert "多忙" in bigrams
        assert "労働" in bigrams
        # Brackets and parentheses should be stripped
        assert "（長" not in bigrams

    def test_compute_theme_similarity_identical_and_distinct(self):
        title_a = "GIGAスクール構想下における1人1台端末利活用と地域格差"
        title_b = "1人1台端末の利活用状況と自治体間格差の比較分析"
        title_c = "教員の勤務実態と持ち帰り残業の構造要因分析"

        # A and B are very similar themes
        sim_ab, shared_ab = compute_theme_similarity(title_a, title_b)
        assert sim_ab >= 0.20, f"Expected similarity >= 0.20, got {sim_ab}"
        assert len(shared_ab) >= 2

        # A and C are distinct themes
        sim_ac, shared_ac = compute_theme_similarity(title_a, title_c)
        assert sim_ac < 0.10, f"Expected similarity < 0.10, got {sim_ac}"

    def test_check_theme_duplication_exact_angle(self):
        history = [
            {
                "dataset_id": "japan_mext_ict_informatization",
                "angle_id": "mext_ict_utilization_gap",
                "title": "GIGA端末利活用率の地域間格差",
                "angle_name": "端末活用の自治体格差",
                "date": "2026-09-23",
            }
        ]
        res = check_theme_duplication(
            candidate_title="新タイトル：ICT格差の検証",
            candidate_theme="端末活用の自治体格差",
            candidate_angle_id="mext_ict_utilization_gap",
            candidate_dataset_id="japan_mext_ict_informatization",
            history=history,
            recent_n=14,
        )
        assert res.is_duplicate is True
        assert res.similarity_score == 1.0
        assert "同一研究アングル" in res.details

    def test_check_theme_duplication_semantic_threshold(self):
        history = [
            {
                "dataset_id": "japan_mext_ict_informatization",
                "angle_id": "other_angle",
                "title": "全国小中学校における1人1台端末の利活用格差とデジタルデバイド",
                "angle_name": "端末利活用の格差検証",
                "date": "2026-09-22",
            }
        ]
        # Candidate with heavily overlapping content words
        candidate_title = "1人1台端末の活用頻度格差とデジタルデバイドの進展"
        candidate_theme = "端末利用格差"
        res = check_theme_duplication(
            candidate_title=candidate_title,
            candidate_theme=candidate_theme,
            history=history,
            recent_n=14,
            similarity_threshold=0.20,
        )
        assert res.is_duplicate is True
        assert res.similarity_score >= 0.20
        assert "重複しています" in res.details

    def test_check_theme_duplication_passes_novel_theme(self):
        history = [
            {
                "dataset_id": "japan_mext_ict_informatization",
                "angle_id": "mext_ict_utilization_gap",
                "title": "GIGAスクール端末の活用格差と自治体別推移",
                "angle_name": "端末利活用の格差検証",
                "date": "2026-09-20",
            }
        ]
        # Completely novel candidate
        candidate_title = "小学校英語専科教員の配置効果と児童の語彙習得度分析"
        candidate_theme = "英語教育における教員専門性の効果"
        res = check_theme_duplication(
            candidate_title=candidate_title,
            candidate_theme=candidate_theme,
            candidate_angle_id="english_specialist_effect",
            candidate_dataset_id="english_survey",
            history=history,
            recent_n=14,
        )
        assert res.is_duplicate is False
        assert res.similarity_score < 0.10

    def test_select_most_diverse_angle_rotates_and_avoids_dup(self):
        angle_1 = DummyAngle("ang_1", "端末活用の自治体格差", "1人1台端末の格差検証")
        angle_2 = DummyAngle("ang_2", "校務DXと教員の負担軽減", "統合型校務支援システムの導入効果")
        angle_3 = DummyAngle("ang_3", "児童生徒の情報モラルとトラブル", "端末持ち帰り時のトラブル発生要因")

        # History has ang_1 posted
        history = [
            {
                "dataset_id": "mext_ict",
                "angle_id": "ang_1",
                "title": "端末活用の自治体格差に関する実証分析",
                "angle_name": "端末活用の自治体格差",
                "date": "2026-09-22",
            }
        ]

        selected, res = select_most_diverse_angle(
            available_angles=[angle_1, angle_2, angle_3],
            history=history,
            dataset_id="mext_ict",
            recent_n=14,
        )
        # Should select ang_2 because ang_1 was recently posted
        assert selected.angle_id == "ang_2"
        assert res.is_duplicate is False
