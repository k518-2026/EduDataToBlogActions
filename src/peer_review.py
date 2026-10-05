"""
Strict Academic Peer Review Report Generator.
Acts as a senior peer reviewer / editorial committee member of an educational technology / informatics
academic journal, providing rigorous, constructive, and uncompromising scholarly critiques.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
import urllib.request

from google import genai
from google.genai import types

from src.academic_contexts import get_academic_context
from src.academic_paper import AcademicPaper
from src.analyzer import AnalysisResult, is_collinear_or_redundant_pair
from src.config import Config
from src.fetchers.base import EducationDataset
from src.utils import LLMGenerationError, extract_anthropic_text, resolve_anthropic_model
from src.utils_date import get_jst_now

logger = logging.getLogger(__name__)


DEFAULT_AI_REVIEW_DISCLOSURE = (
    "本査読報告書は，学術論文執筆を学ぶ学生や若手研究者への教育支援（批判的推敲プロセスの模擬体験）を目的として，"
    "大規模言語モデル・生成AI（Anthropic Claude / Google Gemini）を活用して自動生成された模擬査読レポートです．"
    "教育統計学・教育工学の厳格な学術基準（マクロ集計データの制約，生態学的誤謬の回避，交絡因子の統制，論理的整合性等）"
    "に準拠した指摘を行っていますが，実際の論文修正や教育現場への適用にあたっては，指導教員等の専門的助言とともに批判的に吟味してください．"
)


@dataclass
class PeerReviewReport:
    """Represents a rigorous academic peer review report."""
    paper_title: str
    category: str
    decision: str                                 # e.g. "条件付採録（Major Revision）"
    scores: Dict[str, Tuple[str, str]]           # criterion -> (grade, comment)
    overall_critique: str                        # 総合講評
    major_revisions: List[str]                   # 主要修正要求事項（方法論・統計・理論）
    minor_revisions: List[str]                   # 軽微な修正事項（表現・注記・表記）
    questions_to_authors: List[str]              # 著者への試問・確認事項
    ai_disclosure_evaluation: str                # 生成AI利用開示に関する評価
    review_date: str = field(default_factory=lambda: get_jst_now().strftime("%Y年%m月%d日"))
    ai_review_disclosure: str = DEFAULT_AI_REVIEW_DISCLOSURE


class PeerReviewGenerator:
    """Generates rigorous academic peer review reports using Gemini, Claude, or domain templates."""

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        gemini_model: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        anthropic_model: Optional[str] = None,
    ):
        self.gemini_api_key = (gemini_api_key or Config.GEMINI_API_KEY).strip()
        self.gemini_model = gemini_model or Config.GEMINI_TEXT_MODEL
        self.anthropic_api_key = (anthropic_api_key or Config.ANTHROPIC_API_KEY).strip()
        self.anthropic_model = anthropic_model or Config.ANTHROPIC_MODEL

        self.gemini_client = None
        if self.gemini_api_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client for PeerReviewGenerator: {e}")

    def audit_paper_integrity(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
    ) -> List[Dict[str, str]]:
        """
        Rigorously inspects the paper and underlying calculations for fatal methodological / statistical flaws:
        1. Part-Whole / Ratio Artifacts (e.g. Total A+B vs Ratio A/(A+B), or component couplings).
        2. Statistical Contradictions (e.g. r = 1.00, p < .001 but claiming 'no correlation' or vice versa).
        3. Tautological multiple regression or extreme multicollinearity (VIF > 50).
        """
        issues: List[Dict[str, str]] = []

        # 1. Part-Whole / Ratio Artifacts
        checked_pairs = set()
        all_corr_pairs = []
        for cr in analysis.correlations:
            p_v = getattr(cr, "p_value", getattr(cr, "p_val", 0.0))
            all_corr_pairs.append((cr.metric_x, cr.metric_y, cr.pearson_r, p_v))
        for nc in analysis.no_correlations:
            p_v = getattr(nc, "p_val", getattr(nc, "p_value", 0.0))
            all_corr_pairs.append((nc.metric_x, nc.metric_y, nc.pearson_r, p_v))

        for col_x, col_y, r_val, p_val in all_corr_pairs:
            pair_key = tuple(sorted([col_x, col_y]))
            if pair_key in checked_pairs:
                continue
            checked_pairs.add(pair_key)

            if is_collinear_or_redundant_pair(col_x, col_y):
                issues.append({
                    "category": "FATAL_PART_WHOLE_ARTIFACT",
                    "title": f"数理的アーティファクト・比率擬似相関（「{col_x}」×「{col_y}」）",
                    "desc": (
                        f"指標「{col_x}」と「{col_y}」の相関（r = {r_val:+.3f}）を分析しているが、"
                        "一方が全体量（A+B）であり他方が構成比（A/(A+B)）または構成要素である。"
                        "これはPearson（1897）が警告した比率擬似相関（spurious correlation of ratios）および"
                        "部分-全体交絡（part-whole correlation）の典型例であり、数理的必然（見かけ上の相関）を"
                        "実質的な教育学的連動として論じることは学術的誤謬である。学術推論として成立しない。"
                    ),
                })

        # 2. Contradictory Inferences (checked at sentence level to avoid cross-pair false positives)
        full_text = f"{paper.title}。\n{paper.subtitle}。\n{paper.abstract}\n{paper.results_text}\n{paper.discussion}"
        sentences = [s.strip() for s in re.split(r"[。．\n]+", full_text) if s.strip()]
        null_claim_phrases = ["相関が認められず", "相関は認められず", "無相関", "独立している", "独立した要因", "連動性が存在せず"]
        checked_contradictions = set()
        for nc in analysis.no_correlations:
            pair_key = tuple(sorted([nc.metric_x, nc.metric_y]))
            if abs(nc.pearson_r) >= 0.40 and (nc.p_val < 0.05 or nc.bf10 >= 3.0):
                has_sentence_contradiction = any(
                    (nc.metric_x in sent and nc.metric_y in sent and any(w in sent for w in null_claim_phrases))
                    for sent in sentences
                )
                if has_sentence_contradiction and pair_key not in checked_contradictions:
                    checked_contradictions.add(pair_key)
                    p_fmt = "< .001" if nc.p_val < 0.001 else f"= {nc.p_val:.3f}"
                    issues.append({
                        "category": "FATAL_CONTRADICTION",
                        "title": f"計算結果と本文解釈の破綻的矛盾（「{nc.metric_x}」×「{nc.metric_y}」）",
                        "desc": (
                            f"指標「{nc.metric_x}」と「{nc.metric_y}」の間で統計的に有意な相関"
                            f"（r = {nc.pearson_r:+.2f}, p {p_fmt}, BF₁₀ = {nc.bf10:.1f}）が算出されているにもかかわらず、"
                            "本文中において『相関が認められず』『真の独立性』と正反対の結論を述べている。"
                            "計算結果と著者の主張が致命的に矛盾しており、学術論文としての論理的一貫性を根本から喪失している。"
                        ),
                    })

        for cr in analysis.correlations:
            pair_key = tuple(sorted([cr.metric_x, cr.metric_y]))
            p_v = getattr(cr, "p_value", getattr(cr, "p_val", 1.0))
            bf_v = getattr(cr, "bf10", 1.0) or 1.0
            if abs(cr.pearson_r) >= 0.40 and (p_v < 0.05 or bf_v >= 3.0):
                has_sentence_contradiction = any(
                    (cr.metric_x in sent and cr.metric_y in sent and any(w in sent for w in null_claim_phrases))
                    for sent in sentences
                )
                if has_sentence_contradiction and pair_key not in checked_contradictions:
                    checked_contradictions.add(pair_key)
                    p_fmt = "< .001" if p_v < 0.001 else f"= {p_v:.3f}"
                    issues.append({
                        "category": "FATAL_CONTRADICTION",
                        "title": f"計算結果と本文解釈の破綻的矛盾（「{cr.metric_x}」×「{cr.metric_y}」）",
                        "desc": (
                            f"指標「{cr.metric_x}」と「{cr.metric_y}」の間で統計的に有意な相関"
                            f"（r = {cr.pearson_r:+.2f}, p {p_fmt}, BF₁₀ = {bf_v:.1f}）が算出されているにもかかわらず、"
                            "本文中において『相関が認められず』『真の独立性』と正反対の結論を述べている。"
                            "計算結果と著者の主張が致命的に矛盾しており、学術論文としての論理的一貫性を根本から喪失している。"
                        ),
                    })

        # 3. Tautological Regression / Mathematical Identity Models
        p_method = getattr(analysis, "primary_method", "correlation")
        if analysis.multiple_regression and p_method in ("multiple_regression", "correlation"):
            mr = analysis.multiple_regression
            is_tautology = mr.r_squared > 0.998 and any(
                is_collinear_or_redundant_pair(mr.y_metric, x_var) for x_var in mr.x_metrics
            )
            if is_tautology:
                issues.append({
                    "category": "FATAL_TAUTOLOGICAL_REGRESSION",
                    "title": f"恒等式の重回帰モデル（目的変数: {mr.y_metric}）",
                    "desc": (
                        f"目的変数「{mr.y_metric}」に対する重回帰モデルにおいて、説明変数との間に数学的恒等関係が存在し（R² = {mr.r_squared:.3f}）、"
                        "目的変数の定義式を重回帰で再計算しているに過ぎない。実質的な予測モデルとして成立しない。"
                    ),
                })

        return issues

    def _enforce_rejection_for_fatal_flaws(
        self,
        report: PeerReviewReport,
        audit_issues: List[Dict[str, str]],
    ) -> PeerReviewReport:
        """Enforces a strict '不採録（Reject）' decision when fatal flaws exist."""
        if not audit_issues:
            return report

        report.decision = "不採録（Reject）"
        report.scores["信頼性・統計的妥当性"] = (
            "D",
            "数理的アーティファクト（比率擬似相関・部分-全体交絡）または統計量と本文解釈の致命的矛盾が検出され、学術的妥当性を著しく欠いているため。",
        )
        report.scores["論理的一貫性・構成"] = (
            "D+",
            "計算された相関係数や統計モデルの性質と本文の主張が背馳しており、論理的一貫性が破綻しているため。",
        )

        fatal_critique_lines = [
            "【査読判定：不採録（Reject）— 方法論的・統計的致命的欠陥による却下】",
            "本稿はオープンデータを活用した教育計量分析の試みとして執筆されているが、審査の結果、"
            "学術論文として公刊を認めることが到底不可能な以下の重大な方法論的欠陥（Fatal Flaws）が確認されたため、"
            "本誌掲載論文としては【不採録（Reject）】と判定する。",
            "",
            "＜検出された致命的欠陥＞",
        ]
        for idx, iss in enumerate(audit_issues, 1):
            fatal_critique_lines.append(f"{idx}. 【{iss['title']}】: {iss['desc']}")

        fatal_critique_lines.append("")
        fatal_critique_lines.append(
            "以上の欠陥は単なる表現の修正や注記の追記によって解消可能なものではなく、"
            "研究デザイン、指標選定、および統計モデルの抜本的再構築を要求するものである。"
        )

        report.overall_critique = "\n".join(fatal_critique_lines) + "\n\n" + report.overall_critique

        major_fixes = []
        for iss in audit_issues:
            major_fixes.append(
                f"【研究デザインの全面再構築】：{iss['title']}を解消するため、単一の全体量とその構成要素・構成比の相関やトートロジー回帰を即座に破棄し、概念的に独立した指標間の関係性を検証する研究枠組みへ全面改訂すること。"
            )
        report.major_revisions = major_fixes + report.major_revisions
        return report

    def generate_review(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
    ) -> PeerReviewReport:
        """Generates a rigorous peer review report with strict rejection standards."""
        # 0. Perform strict scientific integrity audit
        audit_issues = self.audit_paper_integrity(
            paper, dataset, analysis, selected_angle=selected_angle
        )

        report = None
        errors = []
        # 1. Prefer Claude if ANTHROPIC_API_KEY is configured
        if self.anthropic_api_key:
            try:
                logger.info(f"Generating academic peer review with Anthropic Claude ({self.anthropic_model})...")
                report = self._generate_with_claude(
                    paper, dataset, analysis, selected_angle=selected_angle, audit_issues=audit_issues
                )
            except Exception as e:
                logger.warning(f"Claude peer review generation failed: {e}. Trying Gemini...")
                errors.append(f"Claude: {e}")

        # 2. Use Gemini if available
        if not report and self.gemini_client:
            try:
                logger.info(f"Generating academic peer review with Gemini ({self.gemini_model})...")
                report = self._generate_with_gemini(
                    paper, dataset, analysis, selected_angle=selected_angle, audit_issues=audit_issues
                )
            except Exception as e:
                logger.warning(f"Gemini peer review generation failed: {e}")
                errors.append(f"Gemini: {e}")

        # 3. No template text is ever published: fail loudly
        if not report:
            raise LLMGenerationError(
                "査読報告を生成できませんでした（テンプレートでは代替しません）: "
                + (" / ".join(errors) if errors else "ANTHROPIC_API_KEY も GEMINI_API_KEY も未設定")
            )

        # 4. Enforce strict rejection if fatal flaws exist
        if audit_issues:
            report = self._enforce_rejection_for_fatal_flaws(report, audit_issues)

        return report

    def _build_review_prompt(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
        audit_issues: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        ctx = selected_angle or get_academic_context(dataset.id, dataset.category)

        audit_section = ""
        if audit_issues:
            audit_lines = ["### ⚠️【事前査読監査による致命的欠陥（Fatal Flaws）検出通知】", "自動査読監査エンジンにより以下の重大な方法論的・数理的欠陥が検出されています："]
            for idx, iss in enumerate(audit_issues, 1):
                audit_lines.append(f"{idx}. 【{iss['title']}】: {iss['desc']}")
            audit_lines.append("\n※査読判定の必須指示：")
            audit_lines.append("上記のような弁護の余地のない致命的欠陥が認められる原稿に対して、安易な「採録」や「条件付採録」を与えることは査読者として学術誌の信頼性を著しく損ないます。")
            audit_lines.append("査読者として学術的真理に妥協することなく、必ず【不採録（Reject）】と判定してください。")
            audit_lines.append("また、総合講評（overall_critique）および主要修正要求（major_revisions）において、数理的アーティファクトや論理矛盾を厳正かつ容赦なく断罪してください。\n")
            audit_section = "\n".join(audit_lines)

        metrics_str = "，".join(dataset.metrics)
        k_rows = len(dataset.df)

        return f"""あなたは教育工学・情報教育・教育統計学を専門とする学術論文誌の「シニア査読委員（非常に厳格で学術的妥当性に妥協のないベテラン査読者）」です。
以下の学術論文（ショートレター）原稿を厳正かつ批判的に審査し、学会公式の「査読結果通知書・査読報告書（Peer Review Report）」を作成してください。

{audit_section}
※査読判定の基準（学術的真理と方法論の厳正な査定）：
- 査読判定は以下の4区分から、論文の学術的品質・計算の妥当性・論理的整合性に基づき客観的かつ厳格に判定してください：
  1. 【不採録（Reject）】: 致命的な方法論的欠陥（比率擬似相関、部分-全体交絡、データセットに存在しない指標を分析したとする虚偽・乖離、計算結果と解釈の破綻的矛盾、重大な多重共線性・恒等式回帰等）が存在し、抜本的な研究デザイン再構築が必要な場合。
  2. 【条件付採録（Major Revision）】: 基本データ・分析および指標間の整合性に一定の価値があるが、交絡因子の未統制、生態学的誤謬、集計標本数の制約、理論的裏付けの深化など大幅な改稿と再査読を要する場合。
  3. 【条件付採録（Minor Revision）】: 分析および結論は概ね妥当で、軽微な表現・注記・体裁修正のみで採録可能な場合。
  4. 【採録（Accept）】: 修正不要でそのまま公刊に値する場合。

※特に以下の学術的弱点・批判点を鋭く論じてください：
  1. 【数理的アーティファクト・比率擬似相関】: 全体量（A+B）と構成比（A/(A+B)）の相関など、部分-全体交絡や数式上の見かけの連動を教育学的知見と誤認していないか。
  2. 【データ指標と計算結果・主張の一致】: 元データの収録指標（{metrics_str}）および相関係数・p値・ベイズファクターの計算結果と、本文のRQ・結論が正しく整合しているか（矛盾や強弁がないか）。
  3. 【生態学的誤謬（Ecological Fallacy）】: 自治体・学校種・国別のマクロ集計データ（集計単位数 K={k_rows}）から、個々の児童生徒・教員の認知・心理メカニズムを推論する際の論理的飛躍と限界。
  4. 【相関関係と因果関係の混同】: 指標間の統計的関連性について、未観測の交絡因子（家庭のSES、制度的要因等）が統制されていない点。
  5. 【データセット固有の学術課題】: 『{ctx.academic_topic}』（理論枠組み: {ctx.theoretical_framework}）に関して、本稿の分析や考察における限界や未解明点（{ctx.core_research_problems}）を厳しく追究する点。

### 【審査対象論文 情報】
- 論文題目: {paper.title}
- 副題: {paper.subtitle}
- 元データ収録指標（K={k_rows}）: {metrics_str}
- 抄録: {paper.abstract}
- リサーチクエスチョン: {paper.objectives}
- 分析手法: {paper.methodology}
- 結果記述: {paper.results_text}
- 考察記述: {paper.discussion}
- 参考文献数: {len(paper.references)}本
- 対象学術主題: {ctx.academic_topic}
- 依拠すべき理論枠組み: {ctx.theoretical_framework}

### 【出力JSONフォーマット】
以下のキーを持つ厳密なJSONオブジェクトを出力してください：
{{
  "paper_title": "{paper.title}",
  "category": "生成AI論文",
  "decision": "不採録（Reject） / 条件付採録（Major Revision） / 条件付採録（Minor Revision） / 採録（Accept） のいずれか",
  "scores": {{
    "独創性・新規性": ["評定（A〜D）", "寸評"],
    "有用性・教育的貢献": ["評定（A〜D）", "寸評"],
    "信頼性・統計的妥当性": ["評定（A〜D）", "寸評（致命的欠陥がある場合はD判定）"],
    "論理的一貫性・構成": ["評定（A〜D）", "寸評"],
    "表現・体裁・引用規範": ["評定（A〜D）", "寸評"]
  }},
  "overall_critique": "（350〜500文字の総合所見。致命的欠陥がある場合は不採録の理由を厳しく明記）",
  "major_revisions": [
    "（主要修正要求事項1）",
    "（主要修正要求事項2）",
    "（主要修正要求事項3）"
  ],
  "minor_revisions": [
    "（軽微な修正事項1）",
    "（軽微な修正事項2）"
  ],
  "questions_to_authors": [
    "（著者への試問1）",
    "（著者への試問2）"
  ],
  "ai_disclosure_evaluation": "（付記における生成AI利用開示の透明性についての査読者評価）"
}}
"""

    def _generate_with_gemini(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
        audit_issues: Optional[List[Dict[str, str]]] = None,
    ) -> PeerReviewReport:
        prompt = self._build_review_prompt(
            paper, dataset, analysis, selected_angle=selected_angle, audit_issues=audit_issues
        )

        candidate_models = [self.gemini_model, "gemini-3.6-flash", "gemini-2.5-pro", "gemini-1.5-flash"]
        seen = set()
        models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

        response = None
        last_error = None
        for m in models_to_try:
            try:
                response = self.gemini_client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=4096,
                        response_mime_type="application/json",
                    ),
                )
                logger.info(f"Successfully generated peer review via Gemini ({m})")
                break
            except Exception as e:
                last_error = e
                if "404" in str(e) or "NOT_FOUND" in str(e):
                    logger.warning(f"Gemini model '{m}' returned 404/NOT_FOUND for peer review. Trying fallback model...")
                    continue
                raise e

        if response is None:
            raise last_error or RuntimeError("All candidate Gemini models failed for peer review")

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()

        data = json.loads(raw_text)
        scores_raw = data.get("scores", {})
        formatted_scores = {}
        for k, v in scores_raw.items():
            if isinstance(v, list) and len(v) >= 2:
                formatted_scores[k] = (str(v[0]), str(v[1]))
            elif isinstance(v, tuple) and len(v) >= 2:
                formatted_scores[k] = (str(v[0]), str(v[1]))
            else:
                formatted_scores[k] = ("B", str(v))

        return PeerReviewReport(
            paper_title=data.get("paper_title", paper.title),
            category=data.get("category", "生成AI論文"),
            decision=data.get("decision", "不採録（Reject）" if audit_issues else "条件付採録（Major Revision）"),
            scores=formatted_scores,
            overall_critique=data.get("overall_critique", ""),
            major_revisions=data.get("major_revisions", []),
            minor_revisions=data.get("minor_revisions", []),
            questions_to_authors=data.get("questions_to_authors", []),
            ai_disclosure_evaluation=data.get("ai_disclosure_evaluation", ""),
            ai_review_disclosure=data.get("ai_review_disclosure", DEFAULT_AI_REVIEW_DISCLOSURE),
        )

    def _generate_with_claude(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
        audit_issues: Optional[List[Dict[str, str]]] = None,
    ) -> PeerReviewReport:
        prompt = self._build_review_prompt(
            paper, dataset, analysis, selected_angle=selected_angle, audit_issues=audit_issues
        )
        resolved_model = resolve_anthropic_model(self.anthropic_api_key, self.anthropic_model)
        logger.info(f"Targeting Anthropic Claude model for peer review: '{resolved_model}' (requested: '{self.anthropic_model}')")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "user-agent": "EduDataToBlogActions/1.0",
        }
        payload = {
            "model": resolved_model,
            "max_tokens": 16000,
            "system": "You are a senior academic reviewer for an educational research journal. Review thoroughly and provide critical scholarly evaluations.",
            "messages": [{"role": "user", "content": prompt}],
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=600) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))

        raw_text = extract_anthropic_text(res_data)
        json_match = re.search(r"\{[\s\S]*\}", raw_text)
        if json_match:
            raw_text = json_match.group(0)

        data = json.loads(raw_text)

        raw_scores = data.get("scores", {})
        formatted_scores: Dict[str, Tuple[str, str]] = {}
        for k, v in raw_scores.items():
            if isinstance(v, list) and len(v) >= 2:
                formatted_scores[k] = (str(v[0]), str(v[1]))
            elif isinstance(v, tuple) and len(v) >= 2:
                formatted_scores[k] = (str(v[0]), str(v[1]))
            else:
                formatted_scores[k] = ("B", str(v))

        logger.info("Successfully generated academic peer review via Anthropic Claude!")
        return PeerReviewReport(
            paper_title=data.get("paper_title", paper.title),
            category=data.get("category", "生成AI論文"),
            decision=data.get("decision", "不採録（Reject）" if audit_issues else "条件付採録（Major Revision）"),
            scores=formatted_scores,
            overall_critique=data.get("overall_critique", ""),
            major_revisions=data.get("major_revisions", []),
            minor_revisions=data.get("minor_revisions", []),
            questions_to_authors=data.get("questions_to_authors", []),
            ai_disclosure_evaluation=data.get("ai_disclosure_evaluation", ""),
            ai_review_disclosure=data.get("ai_review_disclosure", DEFAULT_AI_REVIEW_DISCLOSURE),
        )

    def _generate_template_fallback(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
        audit_issues: Optional[List[Dict[str, str]]] = None,
    ) -> PeerReviewReport:
        """Domain-specific academic peer review fallback with rigorous scholarly critique tailored to dataset."""
        ctx = selected_angle or get_academic_context(dataset.id, dataset.category)

        decision = "不採録（Reject）" if audit_issues else "条件付採録（Major Revision）"
        stat_grade = "D" if audit_issues else "B-"
        stat_critique = (
            "数理的アーティファクト（比率擬似相関・部分-全体交絡）または統計量と本文解釈の致命的矛盾が検出され、学術的妥当性を著しく欠いているため。"
            if audit_issues
            else (
                "図１および図２において95%信頼区間（95% CI）を算出して推計精度を明示し，頻度論的p値に加えてJZSベイズファクター（BF₁₀）による証拠強度を併記した点は評価できる．"
                "一方で，公的集計値（マクロデータ）を用いているため，集計単位の相関から個々の児童生徒の認知的メカニズムを推論する際の"
                "「生態学的誤謬（Ecological Fallacy）」のリスクが懸念され，家庭のSES等の交絡因子が未統制である限界の明記が不可欠である．"
            )
        )

        scores = {
            "独創性・新規性": (
                "B",
                "公的オープンデータを時系列トレンドおよび相関の双方から多角的に分析したアプローチは評価できるが、"
                "利用した指標自体は公表統計の再集計にとどまり、独自の理論枠組みや新規概念の創出には至っていない．",
            ),
            "有用性・教育的貢献": (
                "B" if audit_issues else "B+",
                "教育行政におけるEBPM（証拠に基づく政策立案）に向けた定量的モニタリングの試みは理解できるが、"
                "方法論的妥当性を欠く分析結果に基づく提言は教育政策・現場指導に誤認を招く恐れがある．" if audit_issues else
                "教育行政におけるEBPM（証拠に基づく政策立案）や指導改善に向けた定量的ベンチマークを提供する点で有益である．"
                "しかしながら、現場への教育的示唆が「探究型授業へのシフト」等の総花的な言説にとどまっており、より具体的な実践条件の明示が望まれる．",
            ),
            "信頼性・統計的妥当性": (
                stat_grade,
                stat_critique,
            ),
            "論理的一貫性・構成": (
                "D+" if audit_issues else "A-",
                "算出された相関係数や統計モデルの性質と本文の結論が背馳しており、論理的一貫性を喪失している．" if audit_issues else
                "生成AI論文としての構成要件を遵守し、RQ1・RQ2の設定から分析結果、考察に至る対応関係は明瞭である．"
                "先行研究の知見との共通点・相違点を対比させた考察の構成も学術的に評価できる．",
            ),
            "表現・体裁・引用規範": (
                "B+" if audit_issues else "A",
                "句読点（，．）、数字表記、外国人の大文字姓＋and表記、参考文献のアルファベット順一括配列および全角2文字ぶら下げインデントなど、"
                "学会執筆の手引に概ね準拠している．",
            ),
        }

        ai_disclosure_evaluation = (
            "【生成AI利活用に関する開示（付記）についての査読所見】: "
            "本稿末尾に設置された付記において、オープンデータの利用元、Python解析エンジンの算出プロセス、"
            "大規模言語モデル（Anthropic Claude / Google Gemini）による文章生成の経緯、および教育現場の実情に応じた批判的吟味の推奨が明瞭に開示されていることを確認した。"
            "学術誌における研究倫理指針およびAI利活用透明性ガイドラインに十分に準拠した模範的な開示姿勢であると評価する。"
        )

        overall_critique = ctx.fallback_review_critique
        major_revisions = list(ctx.fallback_major_revisions)

        return PeerReviewReport(
            paper_title=paper.title,
            category="生成AI論文",
            decision=decision,
            scores=scores,
            overall_critique=overall_critique,
            major_revisions=major_revisions,
            minor_revisions=ctx.fallback_minor_revisions,
            questions_to_authors=ctx.fallback_questions_to_authors,
            ai_disclosure_evaluation=ai_disclosure_evaluation,
            ai_review_disclosure=DEFAULT_AI_REVIEW_DISCLOSURE,
        )
