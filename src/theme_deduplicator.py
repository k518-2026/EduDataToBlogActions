"""
Theme Deduplication and Research Topic Diversity Engine.
Prevents thematic overlap, content duplication, and cliché recurrence across articles
by performing multi-dimensional semantic similarity checking against past posted articles.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# Common meta-words, structural stopwords, and generic terms to ignore during theme comparison
STOP_WORDS: Set[str] = {
    "調査", "分析", "データ", "推移", "比較", "関す", "おけ", "およ", "平成", "令和",
    "主要", "実態", "報告", "報告書", "全国", "日本", "年度", "年次", "結果", "検討",
    "検証", "考察", "研究", "学校", "児童", "生徒", "教員", "テスト", "レポート", "一覧",
    "モデル", "評価", "指標", "小中学校", "高等学校", "高校", "大学", "教育", "オープンデータ",
    "統計分析", "最新", "概要", "状況", "に関する", "における", "および", "小・中学校",
    # Additional generic reporting, structural, and grade-level tokens
    "示唆", "意外", "実証", "変容", "向上", "低下", "改善", "課題", "背景", "要因",
    "意識", "影響", "関連", "関係", "傾向", "構造", "実証分析", "計量分析", "国際比較",
    "小4", "中2", "小・中", "初等", "中等", "小学", "中学", "現場",
}


def extract_content_words(text: str) -> Set[str]:
    """
    Extracts substantive content words (Kanji compounds, Katakana terms, English acronyms)
    from a title or theme description, excluding common stopwords.
    """
    if not text:
        return set()

    words: Set[str] = set()

    # 1. Katakana loanwords (length >= 2, e.g. プログラミング, デジタルデバイド, パラドックス)
    # Split on punctuation (including middle dot ・)
    for block in re.split(r"[^\u30a0-\u30fa\u30fc]+", text):
        w = block.strip()
        if len(w) >= 2 and w not in STOP_WORDS:
            words.add(w)

    # 2. English words and acronyms (e.g. ICT, GIGA, PISA, TIMSS, STEM, Python)
    for w in re.findall(r"[A-Za-z0-9_]{2,}", text):
        w_clean = w.strip().upper()
        if w_clean.isdigit():
            continue
        if w_clean not in STOP_WORDS:
            words.add(w_clean)

    # 3. Kanji compounds of length >= 2
    for block in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(block) >= 2 and block not in STOP_WORDS:
            words.add(block)
        # Extract 2-character sub-grams for compound nouns (e.g. 端末利活用 -> 端末, 活用)
        for i in range(len(block) - 1):
            sub = block[i : i + 2]
            if sub not in STOP_WORDS:
                words.add(sub)

    return words


def extract_character_bigrams(text: str) -> Set[str]:
    """
    Extracts character 2-grams from Japanese/alphanumeric text after stripping
    punctuation, whitespace, and bracket formatting.
    """
    if not text:
        return set()
    clean = re.sub(r"[\s\d【】（）()・:：、。/／\-~〜!！?？「」『』\[\]]+", "", text)
    if len(clean) < 2:
        return set()
    return {clean[i : i + 2] for i in range(len(clean) - 1)}


def compute_theme_similarity(text_a: str, text_b: str) -> Tuple[float, Set[str]]:
    """
    Computes a composite semantic similarity score [0.0, 1.0] between two titles or themes
    using content word overlap, Jaccard similarity, and character bigram Dice coefficient.
    Returns (similarity_score, shared_content_words).
    """
    if not text_a or not text_b:
        return 0.0, set()

    wa = extract_content_words(text_a)
    wb = extract_content_words(text_b)
    inter_w = wa & wb
    union_w = wa | wb
    min_w = min(len(wa), len(wb))

    jaccard_w = len(inter_w) / len(union_w) if union_w else 0.0
    overlap_w = len(inter_w) / min_w if min_w else 0.0

    ba = extract_character_bigrams(text_a)
    bb = extract_character_bigrams(text_b)
    inter_b = ba & bb
    dice_b = (2.0 * len(inter_b)) / (len(ba) + len(bb)) if (len(ba) + len(bb)) else 0.0

    # Composite similarity: balanced between substantive word overlap and character bigrams
    score = 0.40 * overlap_w + 0.35 * jaccard_w + 0.25 * dice_b
    return min(1.0, max(0.0, score)), inter_w


@dataclass
class DuplicationCheckResult:
    """Detailed result of a theme duplication check against past posted history."""

    is_duplicate: bool
    similarity_score: float
    threshold: float
    conflicting_post: Optional[Dict[str, Any]] = None
    overlapping_keywords: List[str] = field(default_factory=list)
    details: str = ""


def check_theme_duplication(
    candidate_title: str,
    candidate_theme: str,
    history: List[Dict[str, Any]],
    candidate_angle_id: Optional[str] = None,
    candidate_dataset_id: Optional[str] = None,
    recent_n: int = 14,
    similarity_threshold: float = 0.20,
    keyword_overlap_threshold: int = 2,
) -> DuplicationCheckResult:
    """
    Evaluates whether the candidate title or research theme overlaps significantly
    with any of the last `recent_n` posted reports in history.

    Rules for flagging duplication:
    1. Exact same angle_id posted within the last recent_n articles.
    2. Composite similarity score between candidate theme/title and a recent post >= similarity_threshold.
    3. 2 or more core domain concepts overlap with a recent post AND similarity >= 0.14.
    """
    if not history:
        return DuplicationCheckResult(
            is_duplicate=False,
            similarity_score=0.0,
            threshold=similarity_threshold,
            details="No history entries found; duplication check passed.",
        )

    # Inspect up to recent_n entries (newest first)
    inspected_entries = list(reversed(history))[:recent_n]
    candidate_text = f"{candidate_title} {candidate_theme}"

    max_sim = 0.0
    conflicting_entry: Optional[Dict[str, Any]] = None
    best_overlapping_keywords: List[str] = []
    conflict_reason = ""

    for entry in inspected_entries:
        past_title = entry.get("title", "")
        past_theme = entry.get("angle_name", "") or entry.get("angle_id", "")
        past_text = f"{past_title} {past_theme}"
        past_angle_id = entry.get("angle_id", "")
        past_dataset_id = entry.get("dataset_id", "")
        past_date = entry.get("date", "") or entry.get("posted_at", "")[:10]

        # 1. Exact angle_id match on same dataset in recent window
        if (
            candidate_angle_id
            and candidate_dataset_id
            and candidate_angle_id == past_angle_id
            and candidate_dataset_id == past_dataset_id
        ):
            return DuplicationCheckResult(
                is_duplicate=True,
                similarity_score=1.0,
                threshold=similarity_threshold,
                conflicting_post=entry,
                overlapping_keywords=[candidate_angle_id],
                details=(
                    f"同一データセット（{candidate_dataset_id}）の同一研究アングル（{candidate_angle_id}）が"
                    f"直近（{past_date}）に投稿済みです（重複排除発動）。"
                ),
            )

        # 2. Semantic similarity calculation
        sim_score, shared_kw = compute_theme_similarity(candidate_text, past_text)

        if sim_score > max_sim:
            max_sim = sim_score
            conflicting_entry = entry
            best_overlapping_keywords = sorted(shared_kw)

        # Check threshold exceedance
        same_dataset = bool(
            candidate_dataset_id
            and past_dataset_id
            and candidate_dataset_id == past_dataset_id
        )

        if same_dataset:
            # Stricter criteria for the same dataset: must rotate among distinct research angles
            effective_threshold = similarity_threshold
            is_dup_by_score = sim_score >= effective_threshold
            is_dup_by_keywords = (
                len(shared_kw) >= keyword_overlap_threshold and sim_score >= 0.15
            )
        else:
            # Cross-dataset comparison: detects genuine thematic cliches / concept duplication
            # (e.g. repeated GIGA divide, teacher overtime, gender gap in STEM)
            effective_threshold = max(similarity_threshold, 0.25)
            is_dup_by_score = sim_score >= effective_threshold
            is_dup_by_keywords = len(shared_kw) >= 3 and sim_score >= 0.20

        if is_dup_by_score or is_dup_by_keywords:
            conflict_reason = (
                f"過去記事（{past_date}: 「{past_title}」）とテーマが重複しています "
                f"（類似度: {sim_score:.1%}, 共通概念キーワード: {sorted(shared_kw)}）。"
            )
            return DuplicationCheckResult(
                is_duplicate=True,
                similarity_score=round(sim_score, 3),
                threshold=effective_threshold,
                conflicting_post=entry,
                overlapping_keywords=sorted(shared_kw),
                details=conflict_reason,
            )

    return DuplicationCheckResult(
        is_duplicate=False,
        similarity_score=round(max_sim, 3),
        threshold=similarity_threshold,
        conflicting_post=conflicting_entry if max_sim > 0.05 else None,
        overlapping_keywords=best_overlapping_keywords,
        details=(
            f"直近{len(inspected_entries)}件との最大類似度は {max_sim:.1%} です"
            f"（基準値 {similarity_threshold:.1%} 未満：重複なし確認済）。"
        ),
    )


def select_most_diverse_angle(
    available_angles: List[Any],
    history: List[Dict[str, Any]],
    dataset_id: str,
    recent_n: int = 14,
    similarity_threshold: float = 0.20,
) -> Tuple[Any, DuplicationCheckResult]:
    """
    Selects the most distinct research angle for the given dataset by evaluating
    all available angles against the recent history.

    Priority:
    1. Angles that do NOT duplicate any post in the last `recent_n` window.
       Among these, prefer unposted or least recently used angles.
    2. If all angles have some overlap, pick the angle with the MINIMUM maximum similarity.
    """
    if not available_angles:
        raise ValueError(f"No angles available for dataset '{dataset_id}'")

    if len(available_angles) == 1:
        check = check_theme_duplication(
            candidate_title=getattr(available_angles[0], "title_theme", ""),
            candidate_theme=getattr(available_angles[0], "angle_name", ""),
            candidate_angle_id=getattr(available_angles[0], "angle_id", ""),
            candidate_dataset_id=dataset_id,
            history=history,
            recent_n=recent_n,
            similarity_threshold=similarity_threshold,
        )
        return available_angles[0], check

    # Helper: get last post index for an angle
    def get_last_angle_index(a: Any) -> int:
        target_id = getattr(a, "angle_id", "")
        for idx in range(len(history) - 1, -1, -1):
            entry = history[idx]
            if entry.get("dataset_id") == dataset_id and entry.get("angle_id") == target_id:
                return idx
        return -1

    candidates_eval: List[Tuple[Any, DuplicationCheckResult, int]] = []

    for angle in available_angles:
        title_theme = getattr(angle, "title_theme", "")
        angle_name = getattr(angle, "angle_name", "")
        a_id = getattr(angle, "angle_id", "")

        check = check_theme_duplication(
            candidate_title=title_theme,
            candidate_theme=angle_name,
            candidate_angle_id=a_id,
            candidate_dataset_id=dataset_id,
            history=history,
            recent_n=recent_n,
            similarity_threshold=similarity_threshold,
        )
        last_idx = get_last_angle_index(angle)
        candidates_eval.append((angle, check, last_idx))

    # 1. Non-duplicate angles
    non_dup = [c for c in candidates_eval if not c[1].is_duplicate]
    if non_dup:
        # Sort by: unposted first (last_idx == -1), then smallest last_idx (least recently posted),
        # then smallest similarity_score
        non_dup.sort(key=lambda c: (c[2] != -1, c[2], c[1].similarity_score))
        selected, check_res, _ = non_dup[0]
        logger.info(
            f"Selected non-overlapping angle for '{dataset_id}': '{getattr(selected, 'angle_name', '')}' "
            f"(Max similarity to recent posts: {check_res.similarity_score:.1%})"
        )
        return selected, check_res

    # 2. All angles have some overlap -> pick the one with MINIMUM similarity score
    candidates_eval.sort(key=lambda c: c[1].similarity_score)
    selected, check_res, _ = candidates_eval[0]
    logger.warning(
        f"All angles for '{dataset_id}' had some overlap with recent history. "
        f"Selecting angle with minimal similarity: '{getattr(selected, 'angle_name', '')}' "
        f"(Similarity: {check_res.similarity_score:.1%})"
    )
    return selected, check_res
