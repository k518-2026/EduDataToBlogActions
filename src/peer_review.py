"""
Strict Academic Peer Review Report Generator.
Acts as a senior peer reviewer / editorial committee member of an educational technology / informatics
academic journal, providing rigorous, constructive, and uncompromising scholarly critiques.
"""
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import re
from typing import Dict, List, Optional, Tuple
import urllib.request

from google import genai
from google.genai import types

from src.academic_contexts import get_academic_context
from src.academic_paper import AcademicPaper
from src.analyzer import AnalysisResult
from src.config import Config
from src.fetchers.base import EducationDataset
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

    def generate_review(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
    ) -> PeerReviewReport:
        """Generates a rigorous peer review report."""
        # 1. Prefer Claude if ANTHROPIC_API_KEY is configured
        if self.anthropic_api_key:
            try:
                logger.info(f"Generating academic peer review with Anthropic Claude ({self.anthropic_model})...")
                return self._generate_with_claude(paper, dataset, analysis)
            except Exception as e:
                logger.warning(f"Claude peer review generation failed: {e}. Trying Gemini...")

        # 2. Use Gemini if available
        if self.gemini_client:
            try:
                logger.info(f"Generating academic peer review with Gemini ({self.gemini_model})...")
                return self._generate_with_gemini(paper, dataset, analysis)
            except Exception as e:
                logger.warning(f"Gemini peer review generation failed: {e}. Falling back to domain template.")

        # 3. Fallback to domain-specific peer review template
        logger.info("Using domain-specific academic peer review template fallback.")
        return self._generate_template_fallback(paper, dataset, analysis)

    def _build_review_prompt(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
    ) -> str:
        ctx = get_academic_context(dataset.id, dataset.category)

        return f"""あなたは教育工学・情報教育・教育統計学を専門とする学術論文誌の「シニア査読委員（非常に厳格で学術的妥当性に妥協のないベテラン査読者）」です。
以下の学術論文（ショートレター）原稿を厳正かつ批判的に審査し、学会公式の「査読結果通知書・査読報告書（Peer Review Report）」を作成してください。

※査読姿勢の指針：
- 公的オープンデータを活用した計量分析（EBPM）の試みについては一定の敬意を払いつつも、学術論文としての「方法論的厳密さ」「統計的妥当性」「因果推論の慎重さ」に対しては極めて厳しい視点で課題を指摘してください。
- 総合判定は安易な「採録（Accept）」とはせず、学術的課題を真摯に突きつける【「条件付採録（Major Revision）」】としてください。
- 特に以下の学術的弱点・批判点を鋭く論じてください：
  1. 【生態学的誤謬（Ecological Fallacy）】: 自治体・学校種別のマクロ集計データから、個々の児童生徒の認知・心理メカニズムを推論する際の論理的飛躍と限界。
  2. 【相関関係と因果関係の混同】: 端末活用率や好意度と学力正答率の連動性について、交絡因子（家庭の社会経済的背景 SES、学習時間、指導体制等）が統制されていない点。
  3. 【教育現場への示唆の解像度】: 「探究型授業へのシフト」「個別最適な学び」等の提言が総花的な教育論にとどまり、分析結果から直接導かれる具体的手順・条件の検討が不足している点。
  4. 【データセット固有の学術課題】: 『{ctx.academic_topic}』（理論枠組み: {ctx.theoretical_framework}）に関して、本稿の分析や考察における限界や未解明点（{ctx.core_research_problems}）を厳しく追究する点。

### 【審査対象論文 情報】
- 論文題目: {paper.title}
- 副題: {paper.subtitle}
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
  "category": "ショートレター",
  "decision": "条件付採録（Major Revision）",
  "scores": {{
    "独創性・新規性": ["B", "公的オープンデータを時系列・相関の複合観点から可視化した点は評価できるが、既存公表集計値の再整理にとどまり、独自の理論モデルや新規指標の創出には至っていない。"],
    "有用性・教育的貢献": ["B+", "EBPM推進や教育施策のモニタリングとして有益な知見を含むが、指導現場への提言がやや一般的・総花的な教育言説にとどまっており、実践への具体的手順の解像度向上が求められる。"],
    "信頼性・統計的妥当性": ["B-", "図１・図２において95%信頼区間（95% CI）の誤差棒および信頼区間帯を描画して推計の不確実性を明示した点は評価できるが、マクロ集計値の相関から個人の認知的変容を推論する際の生態学的誤謬（Ecological Fallacy）や、未統制の交絡因子（SES等）に関する議論が不足している。"],
    "論理的一貫性・構成": ["A-", "RQ1/RQ2の設定から結果・考察に至る対応関係、および先行研究との共通点・相違点の対比構成は明瞭であり、ショートレターとしての骨格は整っている。"],
    "表現・体裁・引用規範": ["A", "学会執筆要項に厳格に準拠し、数字表記、参考文献のアルファベット順一括記載、2文字ぶら下げインデント、生成AI利用開示付記が適切に整えられている。"]
  }},
  "overall_critique": "（300〜450文字の総合所見。論文の意義を認めつつ、方法論的限界と加筆・修正の必要性を厳しく指摘する文章）",
  "major_revisions": [
    "（主要修正要求事項1：生態学的誤謬と集計データの限界明記）",
    "（主要修正要求事項2：相関関係と因果関係の峻別、交絡因子の統制に関する議論）",
    "（主要修正要求事項3：教育現場への具体的指導提言の解像度向上）"
  ],
  "minor_revisions": [
    "（軽微な修正事項1：図表キャプションや単位表記の明確化）",
    "（軽微な修正事項2：本文中の教育専門用語の操作的定義）"
  ],
  "questions_to_authors": [
    "（著者への試問1：分析結果の一般化可能性についての見解）",
    "（著者への試問2：非線形なトレンド変化についての教育学的解釈）"
  ],
  "ai_disclosure_evaluation": "（付記における生成AI利用開示の透明性、倫理的配慮、批判的吟味の推奨についての査読者評価）"
}}
"""

    def _generate_with_gemini(
        self,
        paper: AcademicPaper,
        dataset: EducationDataset,
        analysis: AnalysisResult,
    ) -> PeerReviewReport:
        prompt = self._build_review_prompt(paper, dataset, analysis)
        response = self.gemini_client.models.generate_content(
            model=self.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=4096,
                response_mime_type="application/json",
            ),
        )
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
            category=data.get("category", "ショートレター"),
            decision=data.get("decision", "条件付採録（Major Revision）"),
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
    ) -> PeerReviewReport:
        prompt = self._build_review_prompt(paper, dataset, analysis)
        prompt += "\n\n必ず指定された全フィールド（paper_title, category, decision, scores, overall_critique, major_revisions, minor_revisions, questions_to_authors, ai_disclosure_evaluation）を含む有効な単一のJSONオブジェクト（余計な説明文やマークダウンコードブロックなし）のみを出力してください。"

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "user-agent": "EduDataToBlogActions/1.0",
        }
        payload = {
            "model": self.anthropic_model,
            "max_tokens": 4096,
            "temperature": 0.3,
            "messages": [{"role": "user", "content": prompt}],
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))

        raw_text = res_data["content"][0]["text"].strip()
        json_match = re.search(r"\{[\s\S]*\}", raw_text)
        if json_match:
            raw_text = json_match.group(0)

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

        logger.info("Successfully generated academic peer review via Anthropic Claude 3.5 Sonnet!")
        return PeerReviewReport(
            paper_title=data.get("paper_title", paper.title),
            category=data.get("category", "ショートレター"),
            decision=data.get("decision", "条件付採録（Major Revision）"),
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
    ) -> PeerReviewReport:
        """Domain-specific academic peer review fallback with rigorous scholarly critique tailored to dataset."""
        ctx = get_academic_context(dataset.id, dataset.category)

        scores = {
            "独創性・新規性": (
                "B",
                "公的オープンデータを時系列トレンドおよび相関の双方から多角的に分析したアプローチは評価できるが、"
                "利用した指標自体は公表統計の再集計にとどまり、独自の理論枠組みや新規概念の創出には至っていない．",
            ),
            "有用性・教育的貢献": (
                "B+",
                "教育行政におけるEBPM（証拠に基づく政策立案）や指導改善に向けた定量的ベンチマークを提供する点で有益である．"
                "しかしながら、現場への教育的示唆が「探究型授業へのシフト」等の総花的な言説にとどまっており、より具体的な実践条件の明示が望まれる．",
            ),
            "信頼性・統計的妥当性": (
                "B-",
                "図１および図２において95%信頼区間（95% CI）を算出し，誤差棒および信頼区間帯として可視化した点は推計精度の担保として評価できる．"
                "一方で，公的集計値（マクロデータ）を用いているため，集計単位の相関から個々の児童生徒の認知的メカニズムを推論する際の"
                "「生態学的誤謬（Ecological Fallacy）」のリスクが懸念され，家庭のSES等の交絡因子が未統制である限界の明記が不可欠である．",
            ),
            "論理的一貫性・構成": (
                "A-",
                "ショートレターとしての構成要件を遵守し、RQ1・RQ2の設定から分析結果、考察に至る対応関係は明瞭である．"
                "先行研究の知見との共通点・相違点を対比させた考察の構成も学術的に評価できる．",
            ),
            "表現・体裁・引用規範": (
                "A",
                "句読点（，．）、数字表記、外国人の大文字姓＋and表記、参考文献のアルファベット順一括配列および全角2文字ぶら下げインデントなど、"
                "学会執筆の手引に厳格に準拠している．生成AI利用開示も適切に付記されている．",
            ),
        }

        ai_disclosure_evaluation = (
            "【生成AI利活用に関する開示（付記）についての査読所見】: "
            "本稿末尾に設置された付記において、オープンデータの利用元、Python解析エンジンの算出プロセス、"
            "大規模言語モデル（Anthropic Claude / Google Gemini）による文章生成の経緯、および教育現場の実情に応じた批判的吟味の推奨が明瞭に開示されていることを確認した。"
            "学術誌における研究倫理指針およびAI利活用透明性ガイドラインに十分に準拠した模範的な開示姿勢であると高く評価する。"
            "なお、AI生成文特有の一般的な美辞麗句や過度な教育的断定を排し、著者自身の批判的推敲が全編に行き届いていることを確認した。"
        )

        return PeerReviewReport(
            paper_title=paper.title,
            category="ショートレター",
            decision="条件付採録（Major Revision）",
            scores=scores,
            overall_critique=ctx.fallback_review_critique,
            major_revisions=ctx.fallback_major_revisions,
            minor_revisions=ctx.fallback_minor_revisions,
            questions_to_authors=ctx.fallback_questions_to_authors,
            ai_disclosure_evaluation=ai_disclosure_evaluation,
            ai_review_disclosure=DEFAULT_AI_REVIEW_DISCLOSURE,
        )
