"""
Educational Commentary and Insights Generator using Google Gemini AI.
Provides expert pedagogical analysis and actionable classroom/policy takeaways.
Includes intelligent template fallback when Gemini API key is not configured.
"""
from dataclasses import dataclass
import logging
from typing import Dict, Optional

from google import genai
from google.genai import types

from src.analyzer import AnalysisResult
from src.config import Config
from src.fetchers.base import EducationDataset

logger = logging.getLogger(__name__)


@dataclass
class EducationalInsights:
    executive_summary: str
    pedagogical_implications: str
    future_challenges_and_policy: str


class GeminiInsightGenerator:
    """Generates educational insights using Gemini API or rule-based templates."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model_name = model_name or Config.GEMINI_TEXT_MODEL
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Gemini Client with model {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")

    def generate_insights(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> EducationalInsights:
        """Generates educational insights from statistical analysis results."""
        if self.client:
            try:
                return self._generate_with_gemini(dataset, analysis)
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to template engine: {e}")

        return self._generate_template_fallback(dataset, analysis)

    def _generate_with_gemini(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> EducationalInsights:
        stats_summary = []
        for m, s in analysis.descriptive_stats.items():
            stats_summary.append(
                f"- {m}: 平均={s.mean}{dataset.unit}, 中央値={s.median}{dataset.unit}, 最小={s.min_val}, 最大={s.max_val}, 標準偏差={s.std}"
            )

        trends_summary = []
        for tr in analysis.trends[:4]:
            grp = f"({tr.group_name}) " if tr.group_name else ""
            trends_summary.append(
                f"- {grp}{tr.metric}: {tr.start_time}年 {tr.start_val}{dataset.unit} → {tr.end_time}年 {tr.end_val}{dataset.unit} (変化量: {tr.diff:+.1f}, 変化率: {tr.pct_change:+.1f}%, CAGR: {tr.cagr}%, R²={tr.r_squared})"
            )

        insights_text = "\n".join(analysis.key_insights)

        prompt = f"""あなたは算数・数学教育および情報教育（プログラミング教育・STEAM教育）の世界的専門家・教育統計アナリストです。
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
以下の3つの項目について、客観的な数値の根拠と教育的な深い洞察を交えて日本語で執筆してください。各項目は見出しを付けず、内容のテキストのみを出力してください。セクション間は `===SECTION_BREAK===` で区切ってください。

1. **エグゼクティブサマリー（分析の要約）** (約250〜350文字):
   データの主要な発見、推移のトレンド、注目すべきポイントを要約。

2. **教育現場・指導実践への具体的示唆** (約400〜600文字):
   学校現場の授業実践、カリキュラム設計、児童生徒への指導法、ICTや計算ツールの活用法など、明日からの教育に活かせる実践的アドバイス。

3. **今後の課題と政策・国際的展望** (約300〜450文字):
   教育格差の是正、指導力向上、カリキュラム改訂への提言、国際比較から見えてくる日本の強みと課題。
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=2048,
            ),
        )

        text = response.text.strip()
        parts = text.split("===SECTION_BREAK===")
        if len(parts) >= 3:
            return EducationalInsights(
                executive_summary=parts[0].strip(),
                pedagogical_implications=parts[1].strip(),
                future_challenges_and_policy=parts[2].strip(),
            )
        else:
            # Fallback parsing
            return EducationalInsights(
                executive_summary=text[:400],
                pedagogical_implications=text[400:1000] if len(text) > 400 else "現場での活用を深める必要があります。",
                future_challenges_and_policy=text[1000:] if len(text) > 1000 else "今後の継続的な調査と支援が求められます。",
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
