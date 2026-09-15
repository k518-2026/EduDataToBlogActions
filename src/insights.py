"""
Educational Commentary and Insights Generator using Google Gemini AI.
Provides expert pedagogical analysis and actionable classroom/policy takeaways.
Includes intelligent template fallback when Gemini API key is not configured.
"""
from dataclasses import dataclass
import json
import logging
import re
from typing import Dict, Optional
import urllib.request

from google import genai
from google.genai import types

from src.analyzer import AnalysisResult
from src.config import Config
from src.fetchers.base import EducationDataset
from src.utils import clean_insight_text, resolve_anthropic_model, resolve_metric_unit

logger = logging.getLogger(__name__)


@dataclass
class EducationalInsights:
    executive_summary: str
    pedagogical_implications: str
    future_challenges_and_policy: str


def parse_insights_json(raw_text: str) -> dict[str, str]:
    """
    Safely parses JSON containing executive_summary, pedagogical_implications,
    and future_challenges_and_policy from raw LLM output.
    Handles markdown codeblocks, control characters, and truncated JSON.
    Never returns raw JSON strings or slices of JSON structures.
    """
    if not raw_text:
        return {}

    text = raw_text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Attempt 1: Direct json.loads with strict=False
    try:
        data = json.loads(text, strict=False)
        if isinstance(data, dict):
            return {
                "executive_summary": clean_insight_text(data.get("executive_summary", "")),
                "pedagogical_implications": clean_insight_text(data.get("pedagogical_implications", "")),
                "future_challenges_and_policy": clean_insight_text(data.get("future_challenges_and_policy", "")),
            }
    except Exception:
        pass

    # Attempt 2: Extract outermost JSON object { ... }
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        try:
            data = json.loads(json_match.group(0), strict=False)
            if isinstance(data, dict):
                return {
                    "executive_summary": clean_insight_text(data.get("executive_summary", "")),
                    "pedagogical_implications": clean_insight_text(data.get("pedagogical_implications", "")),
                    "future_challenges_and_policy": clean_insight_text(data.get("future_challenges_and_policy", "")),
                }
        except Exception:
            pass

    # Attempt 3: Regex extraction for individual fields (handles truncated or broken JSON)
    def extract_field(field_name: str, s: str) -> str:
        pattern = rf'"{field_name}"\s*:\s*"(.*?)(?=(?:"\s*,\s*"[a-zA-Z0-9_]+"\s*:)|(?:"\s*\}})|$)'
        m = re.search(pattern, s, re.DOTALL)
        if m:
            return clean_insight_text(m.group(1))
        return ""

    return {
        "executive_summary": extract_field("executive_summary", text),
        "pedagogical_implications": extract_field("pedagogical_implications", text),
        "future_challenges_and_policy": extract_field("future_challenges_and_policy", text),
    }



class GeminiInsightGenerator:
    """Generates educational insights using Claude, Gemini API, or rule-based templates."""

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
                logger.info(f"Initialized Gemini Client with model {self.gemini_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")

    def generate_insights(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> EducationalInsights:
        """Generates educational insights from statistical analysis results."""
        # 1. Prefer Claude if configured
        if self.anthropic_api_key:
            try:
                logger.info(f"Generating insights with Anthropic Claude ({self.anthropic_model})...")
                return self._generate_with_claude(dataset, analysis)
            except Exception as e:
                logger.warning(f"Claude insight generation failed: {e}. Trying Gemini...")

        # 2. Use Gemini if available
        if self.gemini_client:
            try:
                logger.info(f"Generating insights with Google Gemini ({self.gemini_model})...")
                return self._generate_with_gemini(dataset, analysis)
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to template engine: {e}")

        # 3. Fallback to template engine
        logger.info("Using domain-specific educational insight template fallback.")
        return self._generate_template_fallback(dataset, analysis)

    def _build_insight_prompt(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> str:
        stats_summary = []
        for m, s in analysis.descriptive_stats.items():
            m_unit = resolve_metric_unit(m, dataset.unit)
            stats_summary.append(
                f"- {m}: 平均={s.mean}{m_unit}, 中央値={s.median}{m_unit}, 最小={s.min_val}, 最大={s.max_val}, 標準偏差={s.std}"
            )

        trends_summary = []
        for tr in analysis.trends[:4]:
            grp = f"({tr.group_name}) " if tr.group_name else ""
            tr_unit = resolve_metric_unit(tr.metric, dataset.unit)
            trends_summary.append(
                f"- {grp}{tr.metric}: {tr.start_time}年 {tr.start_val}{tr_unit} → {tr.end_time}年 {tr.end_val}{tr_unit} (変化量: {tr.diff:+.1f}, 変化率: {tr.pct_change:+.1f}%, CAGR: {tr.cagr}%, R²={tr.r_squared})"
            )

        insights_text = "\n".join(analysis.key_insights)

        return f"""あなたは算数・数学教育および情報教育（プログラミング教育・STEAM教育）の世界的専門家・教育統計アナリストです。
以下の公的オープンデータおよび統計分析結果を精読し、教育現場の教員・教育委員会・学習者・保護者に向けて、深く実践的な教育インサイトレポートを作成してください。

### 【データセット情報】
- タイトル: {dataset.title}
- 対象分野: {'算数・数学教育' if dataset.category == 'math' else '情報教育・プログラミング教育'} ({dataset.region})
- 出典: {dataset.source_name} ({dataset.source_url})
- 概要: {dataset.description}

### 【統計分析結果の要約】
主要指標の記述統計:
{chr(10).join(stats_summary)}

経年変化・トレンド:
{chr(10).join(trends_summary) if trends_summary else '単年比較データ'}

自動検出インサイト:
{insights_text}

---
### 【出力フォーマット要件】
以下の3つの項目について、客観的な数値の根拠と教育的な深い洞察を交えて日本語で執筆してください。
1. **executive_summary**: 分析の要約 (約250〜350文字)。データの主要な発見、推移のトレンド、注目すべきポイントを要約。
2. **pedagogical_implications**: 教育現場・指導実践への具体的示唆 (約400〜600文字)。学校現場の授業実践、カリキュラム設計、児童生徒への指導法、ICTや計算ツールの活用法など、明日からの教育に活かせる実践的アドバイス。
3. **future_challenges_and_policy**: 今後の課題と政策・国際的展望 (約300〜450文字)。教育格差の是正、指導力向上、カリキュラム改訂への提言、国際比較から見えてくる日本の強みと課題。
"""

    def _generate_with_gemini(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> EducationalInsights:
        prompt = self._build_insight_prompt(dataset, analysis)

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
                        temperature=0.4,
                        max_output_tokens=4096,
                        response_mime_type="application/json",
                        response_schema=EducationalInsights,
                    ),
                )
                logger.info(f"Successfully generated insights via Gemini ({m})")
                break
            except Exception as e:
                last_error = e
                if "404" in str(e) or "NOT_FOUND" in str(e):
                    logger.warning(f"Gemini model '{m}' returned 404/NOT_FOUND for insights. Trying fallback model...")
                    continue
                raise e

        if response is None:
            raise last_error or RuntimeError("All candidate Gemini models failed for insights")

        raw_text = response.text.strip()
        parsed = parse_insights_json(raw_text)
        fallback = self._generate_template_fallback(dataset, analysis)

        exec_summary = parsed.get("executive_summary") or fallback.executive_summary
        pedagogy = parsed.get("pedagogical_implications") or fallback.pedagogical_implications
        policy = parsed.get("future_challenges_and_policy") or fallback.future_challenges_and_policy

        if not exec_summary or len(exec_summary) < 20:
            logger.warning("Parsed Gemini insights had insufficient executive_summary. Using template fallback.")
            return fallback

        return EducationalInsights(
            executive_summary=clean_insight_text(exec_summary),
            pedagogical_implications=clean_insight_text(pedagogy),
            future_challenges_and_policy=clean_insight_text(policy),
        )

    def _generate_with_claude(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> EducationalInsights:
        prompt = self._build_insight_prompt(dataset, analysis)
        prompt += (
            "\n\n【重要】出力は必ず有効なJSON形式のみとしてください。"
            "キーは 'executive_summary', 'pedagogical_implications', 'future_challenges_and_policy' の3つです。"
            "```json 等のマークダウンコードブロックや前後の解説文は一切含めず、純粋なJSONオブジェクト（{...}）のみを出力してください。"
        )

        resolved_model = resolve_anthropic_model(self.anthropic_api_key, self.anthropic_model)
        logger.info(f"Targeting Anthropic Claude model for insights: '{resolved_model}' (requested: '{self.anthropic_model}')")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "user-agent": "EduDataToBlogActions/1.0",
        }
        payload = {
            "model": resolved_model,
            "max_tokens": 4096,
            "temperature": 0.3,
            "system": "You are an expert Japanese educational policy and statistical analyst. Always respond strictly in valid JSON without markdown fences or preambles.",
            "messages": [{"role": "user", "content": prompt}],
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))

        raw_text = res_data["content"][0]["text"].strip()
        parsed = parse_insights_json(raw_text)
        fallback = self._generate_template_fallback(dataset, analysis)

        exec_summary = parsed.get("executive_summary") or fallback.executive_summary
        pedagogy = parsed.get("pedagogical_implications") or fallback.pedagogical_implications
        policy = parsed.get("future_challenges_and_policy") or fallback.future_challenges_and_policy

        if not exec_summary or len(exec_summary) < 20:
            logger.warning("Parsed Claude insights had insufficient executive_summary. Using template fallback.")
            return fallback

        logger.info(f"Successfully generated educational insights via Claude ({resolved_model})!")
        return EducationalInsights(
            executive_summary=clean_insight_text(exec_summary),
            pedagogical_implications=clean_insight_text(pedagogy),
            future_challenges_and_policy=clean_insight_text(policy),
        )




    def _generate_template_fallback(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> EducationalInsights:
        """Generates rich, statistics-grounded insights when Gemini is unavailable."""
        insights_bullets = "、".join(analysis.key_insights[:2])

        if dataset.category == "math":
            exec_summary = (
                f"本分析では、{dataset.source_name}のオープンデータを基に、算数・数学教育における学力到達度や意識の推移を検証しました。"
                f"分析の結果、{insights_bullets}といった特徴的な傾向が明らかになりました。"
                f"特に知識の定着にとどまらず、数学的な見方・考え方を働かせる思考力や、日常生活と数学を結びつける実用感の醸成が重要な指標となっています。"
            )
            pedagogy = (
                "【授業実践・指導法への示唆】\n"
                "1. 単なる反復練習から「問いを創り出す探究型授業」へのシフト: 計算手順の暗記にとどまらず、なぜその公式が成り立つのかを図解や具体物を用いて対話的に説明する活動を取り入れることが有効です。\n"
                "2. デジタル端末を活用した数学的モデリング: 1人1台端末の表計算ソフトや動的幾何ソフト（GeoGebra等）を活用し、グラフの変化を視覚的に体験させることで、関数や図形領域への苦手意識を軽減できます。\n"
                "3. 自己効力感を高める小さな成功体験の設計: 数学に対する学習意欲・将来の有用性感は学力と密接に連動しています。つまずきやすい児童生徒に対して、スモールステップでの足場かけ（スキャフォールディング）が不可欠です。"
            )
            policy = (
                "【今後の課題と教育政策への提言】\n"
                "国際的な動向および経年データを踏まえると、数学的な応用力・課題解決力の格差解消が喫緊の課題です。"
                "PISA等の国際指標でも示されているように、社会経済的背景にかかわらず全ての児童生徒が質の高い理数教育にアクセスできるよう、"
                "放課後学習支援や個別最適なAI教材の積極的活用、ならびに教員の算数・数学専修指導力の継続的研修が求められます。"
            )
        else:
            exec_summary = (
                f"本分析では、{dataset.source_name}の最新公的統計を活用し、情報教育・プログラミング教育および学校ICT環境の実態を定量的に分析しました。"
                f"データからは、{insights_bullets}が明確に示されています。"
                f"GIGAスクール構想によるインフラ整備が急速に進展した一方、日常的な学びのツールとしての利活用頻度やプログラミング的思考の育成にはなお発展の余地が見られます。"
            )
            pedagogy = (
                "【情報教育・プログラミング指導の実践示唆】\n"
                "1. 「使う」段階から「創り出す・探究する」情報活用能力へ: 端末の調べ学習利用にとどまらず、データを集計・可視化して仮説を検証したり、課題解決のためのアルゴリズムを組み立てるプログラミング体験を各教科横断で組み込むことが推奨されます。\n"
                "2. コンピュテーショナル・シンキングの日常化: プログラミング言語の文法習得を目的化せず、問題を分解し、抽象化し、手順化する思考プロセスを総合的な学習の時間や算数・理科と連動させて指導することが肝要です。\n"
                "3. 教員の伴走支援と校内研修の充実: 教員のICT指導力達成率が向上傾向にある地域ほど児童生徒の活用度も高まる正の循環が確認されています。教員同士が授業実践事例を共有するコミュニティづくりが鍵となります。"
            )
            policy = (
                "【今後の展望と高度IT人材育成への課題】\n"
                "国際的なICTスキル保有率比較や高等教育における進路動向からも、初等中等段階からの体系的な情報教育の重要性が増しています。"
                "今後は、生成AIをはじめとする新技術への情報モラル・リテラシー教育の拡充とともに、"
                "ジェンダーギャップの解消（情報・STEM分野への女子進学支援）や、地域・自治体間のICT利活用格差の是正に注力した政策推進が期待されます。"
            )

        return EducationalInsights(
            executive_summary=exec_summary,
            pedagogical_implications=pedagogy,
            future_challenges_and_policy=policy,
        )
