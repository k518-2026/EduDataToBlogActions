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
    counter_intuitive_finding: str = ""


def parse_insights_json(raw_text: str) -> dict[str, str]:
    """
    Safely parses JSON containing executive_summary, counter_intuitive_finding,
    pedagogical_implications, and future_challenges_and_policy from raw LLM output.
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
                "counter_intuitive_finding": clean_insight_text(data.get("counter_intuitive_finding", "")),
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
                    "counter_intuitive_finding": clean_insight_text(data.get("counter_intuitive_finding", "")),
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
        "counter_intuitive_finding": extract_field("counter_intuitive_finding", text),
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
        self,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
        past_topics: Optional[List[Dict[str, str]]] = None,
    ) -> EducationalInsights:
        """Generates educational insights from statistical analysis results."""
        # 1. Prefer Claude if configured
        if self.anthropic_api_key:
            try:
                logger.info(f"Generating insights with Anthropic Claude ({self.anthropic_model})...")
                return self._generate_with_claude(
                    dataset, analysis, selected_angle=selected_angle, past_topics=past_topics
                )
            except Exception as e:
                logger.warning(f"Claude insight generation failed: {e}. Trying Gemini...")

        # 2. Use Gemini if available
        if self.gemini_client:
            try:
                logger.info(f"Generating insights with Google Gemini ({self.gemini_model})...")
                return self._generate_with_gemini(
                    dataset, analysis, selected_angle=selected_angle, past_topics=past_topics
                )
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to template engine: {e}")

        # 3. Fallback to template engine
        logger.info("Using domain-specific educational insight template fallback.")
        return self._generate_template_fallback(dataset, analysis, selected_angle=selected_angle)

    def _build_insight_prompt(
        self,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
        past_topics: Optional[List[Dict[str, str]]] = None,
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

        angle_section = ""
        if selected_angle:
            a_name = getattr(selected_angle, "angle_name", "")
            a_fw = getattr(selected_angle, "theoretical_framework", "")
            a_probs = getattr(selected_angle, "core_research_problems", "")
            a_fmetrics = getattr(selected_angle, "focus_metrics", [])
            f_str = ", ".join(a_fmetrics) if a_fmetrics else "全般"
            angle_section = f"""
### 【本レポート固有の研究アングル・焦点（最重要）】
- 今回の分析アングル: {a_name}
- 適用する理論的枠組み: {a_fw}
- 固有の課題意識・対立点: {a_probs}
- 重点分析対象指標: {f_str}
必ず上記のアングル・理論的枠組み・重点指標を主軸に据えて分析・論述を行ってください。
"""

        dedup_section = ""
        if past_topics:
            past_titles = [
                f"- {p.get('title', '')}（アングル: {p.get('angle_name', '一般')}）"
                for p in past_topics if p.get('title')
            ]
            if past_titles:
                dedup_section = f"""
### 【過去の投稿内容との重複排除・新規性担保の厳格指示】
本システムでは直近で以下のレポート・論文が既に公開されています：
{chr(10).join(past_titles)}
読者にとって単調で重複した印象を与えないよう、上記過去レポートと同一の論点・結論・改善提案を繰り返すことを【厳格に禁止】します。
今回の固有アングル（{getattr(selected_angle, 'angle_name', '') or '新規視点'}）に立脚した、全く新しい切り口からインサイトを導出してください。
"""

        return f"""あなたは算数・数学教育および情報教育（プログラミング教育・STEAM教育）の世界的専門家・教育統計アナリストです。
以下の公的オープンデータおよび統計分析結果を精読し、教育現場の教員・教育委員会・学習者・保護者に向けて、通り一遍の教科書的な解説ではなく、【常識や直観を覆す意外な発見・教育的パラドックス】を前面に押し出した深く刺激的な教育インサイトレポートを作成してください。

### 【データセット情報】
- タイトル: {dataset.title}
- 対象分野: {'算数・数学教育' if dataset.category == 'math' else '情報教育・プログラミング教育'} ({dataset.region})
- 出典: {dataset.source_name} ({dataset.source_url})
- 概要: {dataset.description}
{angle_section}
{dedup_section}
### 【統計分析結果の要約】
主要指標の記述統計:
{chr(10).join(stats_summary)}

経年変化・トレンド:
{chr(10).join(trends_summary) if trends_summary else '単年比較データ'}

自動検出インサイト:
{insights_text}

---
### 【執筆方針：単調さを打破し「意外性」と「知見の深さ」を最大化する要件】
★【紋切り型の一般論・予定調和の完全禁止】:
「ICTの普及が進んでいる」「個別最適な学びが重要である」「日々の復習が大切である」といった、どのデータにも当てはまる陳腐で単調な定型文は【一切禁止】します。
必ず本データの実測値（乖離、格差、頭打ち、逆転現象、情意と学力の不均衡など）に着目し、以下の「意外性」を軸に論述してください：
1. **常識・直観を覆す逆説（パラドックス）の提示**:
   「一見すると順調に見える数値の裏で何が停滞しているのか？」「普及率の向上とは裏腹に、なぜ学習意欲や活用頻度の格差が拡大しているのか？」「学力が高いのに嫌いが増える／端末があるのに使われないという皮肉な実態」など、読者がハッと息を呑む意外な盲点に光を当ててください。
2. **目から鱗の授業改善アプローチ**:
   「単に端末を使わせる」「単に計算練習を反復する」といった安易なアドバイスではなく、現場の教員が「その視点は盲点だった！」と感嘆するような、逆転の発想・エラーを活かした深い探究の授業設計を提案してください。
3. **政策や制度の意図せざる副作用（Unintended Consequences）への警鐘**:
   単なる制度の推進を礼賛するのではなく、一律推進が生み出す新たな心理的負担や隠れた格差など、政策の死角を鋭く突いてください。

---
### 【出力フォーマット要件】
以下の4つの項目について、客観的な実測数値を必ず引用し、読者の知的好奇心を刺激する意外性のある日本語で執筆してください。
1. **executive_summary**: 分析の全体要約 (約280〜380文字)。「一見すると〜と思われがちだが、データからは意外にも…」というように、直観や通説とのギャップ・主要なパラドックスから書き始め、実測数値とともに要約。
2. **counter_intuitive_finding**: 【データが暴く意外な事実・常識の逆説】(約300〜450文字)。「一般には〇〇と思われがちだが、データが示す実態は…」「普及率100%の裏に潜む意外な格差」「高得点層ほど陥る意欲の逆転現象」など、通説や直観を覆す驚きの発見を数値とともに解説。
3. **pedagogical_implications**: 教育現場・指導実践への具体的示唆 (約450〜650文字)。現場の思い込みや盲点を突く意外な指導アプローチ、つまずきやすい概念的落とし穴の逆転克服法、手作業とデジタルの予期せぬ相乗効果など、明日からの授業を劇的に変える実践的知見。
4. **future_challenges_and_policy**: 今後の課題と政策・国際的展望 (約320〜480文字)。表面的な成功の陰に隠れた意図せざる副作用、制度的形骸化の罠、国際比較から浮き彫りになる日本の意外な強みと死角。
"""

    def _generate_with_gemini(
        self,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
        past_topics: Optional[List[Dict[str, str]]] = None,
    ) -> EducationalInsights:
        prompt = self._build_insight_prompt(
            dataset, analysis, selected_angle=selected_angle, past_topics=past_topics
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
        fallback = self._generate_template_fallback(dataset, analysis, selected_angle=selected_angle)

        exec_summary = parsed.get("executive_summary") or fallback.executive_summary
        paradox = parsed.get("counter_intuitive_finding") or fallback.counter_intuitive_finding
        pedagogy = parsed.get("pedagogical_implications") or fallback.pedagogical_implications
        policy = parsed.get("future_challenges_and_policy") or fallback.future_challenges_and_policy

        if not exec_summary or len(exec_summary) < 20:
            logger.warning("Parsed Gemini insights had insufficient executive_summary. Using template fallback.")
            return fallback

        return EducationalInsights(
            executive_summary=clean_insight_text(exec_summary),
            counter_intuitive_finding=clean_insight_text(paradox),
            pedagogical_implications=clean_insight_text(pedagogy),
            future_challenges_and_policy=clean_insight_text(policy),
        )

    def _generate_with_claude(
        self,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
        past_topics: Optional[List[Dict[str, str]]] = None,
    ) -> EducationalInsights:
        prompt = self._build_insight_prompt(
            dataset, analysis, selected_angle=selected_angle, past_topics=past_topics
        )
        prompt += (
            "\n\n【重要】出力は必ず有効なJSON形式のみとしてください。"
            "キーは 'executive_summary', 'counter_intuitive_finding', 'pedagogical_implications', 'future_challenges_and_policy' の4つです。"
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
            "system": "You are an expert Japanese educational policy and statistical analyst specializing in uncovering surprising data paradoxes. Always respond strictly in valid JSON without markdown fences or preambles.",
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
        fallback = self._generate_template_fallback(dataset, analysis, selected_angle=selected_angle)

        exec_summary = parsed.get("executive_summary") or fallback.executive_summary
        paradox = parsed.get("counter_intuitive_finding") or fallback.counter_intuitive_finding
        pedagogy = parsed.get("pedagogical_implications") or fallback.pedagogical_implications
        policy = parsed.get("future_challenges_and_policy") or fallback.future_challenges_and_policy

        if not exec_summary or len(exec_summary) < 20:
            logger.warning("Parsed Claude insights had insufficient executive_summary. Using template fallback.")
            return fallback

        logger.info(f"Successfully generated educational insights via Claude ({resolved_model})!")
        return EducationalInsights(
            executive_summary=clean_insight_text(exec_summary),
            counter_intuitive_finding=clean_insight_text(paradox),
            pedagogical_implications=clean_insight_text(pedagogy),
            future_challenges_and_policy=clean_insight_text(policy),
        )

    def _generate_template_fallback(
        self,
        dataset: EducationDataset,
        analysis: AnalysisResult,
        selected_angle: Optional[Any] = None,
    ) -> EducationalInsights:
        """Generates rich, statistics-grounded insights when Gemini is unavailable."""
        insights_bullets = "、".join(analysis.key_insights[:2])
        angle_note = f"（研究視点: {selected_angle.angle_name}）" if selected_angle and getattr(selected_angle, "angle_name", None) else ""

        if dataset.category == "math":
            exec_summary = (
                f"本分析では{angle_note}、{dataset.source_name}の公的統計に基づき、算数・数学教育における学力到達度と情意指標の推移動態を精緻に検証しました。"
                f"データからは、{insights_bullets}という顕著な傾向が示されています。"
                f"一見すると高学力が維持されているように映るものの、単なる計算手順の習熟と、数学的探究心や自己効力感との間には深刻な乖離が生じている実態が浮き彫りとなりました。"
            )
            counter_intuitive = (
                "【常識とデータの逆説：学力世界トップクラスに潜む自己効力感の急落】\n"
                "一般には『問題が解けて成績が優秀であるほど、その教科が好きになり自信を持つ』と考えられがちです。"
                "しかし統計データが突きつける現実は正反対のパラドックスを示しています。我が国の児童生徒は国際的にも極めて高い平均正答率を維持しているにもかかわらず、"
                "学年が上がるにつれて『算数・数学が楽しい』『自分は数学が得意だ』と肯定する割合が劇的に急落します。"
                "正解を出すことへの外在的プレッシャーが、かえって失敗を恐れる心理を生み、探究への内発的動機を阻害しているという意外な構造的課題がデータから浮かび上がっています。"
            )
            pedagogy = (
                "【現場の盲点を突く授業実践・指導アプローチ】\n"
                "1. 『正解への近道』ではなく『あえて誤答を味わう』逆転の授業設計: 素早い正解を称賛する指導から脱却し、典型的なつまずきや多様な別解をクラス全体で比較・吟味する活動を取り入れることで、失敗を恐れない探究的マインドセットを育みます。\n"
                "2. 動的ツールを用いた数学的モデリングと直観の裏切り体験: 1人1台端末のGeoGebraや表計算ソフトを活用し、『直観と計算結果が食い違う瞬間』を意図的に演出することで、公式の受動的暗記から主体的探究へ意識を転換させます。\n"
                "3. スモールステップとメタ認知の統合的支援: つまずきを抱える児童生徒に対し、単なるドリル反復ではなく『どこで思考が止まったか』を自己言語化させる足場かけ（スキャフォールディング）を行い、有能感の回復を促進します。"
            )
            policy = (
                "【今後の課題と教育政策への提言】\n"
                "国際指標や経年変化が示す通り、表面的な平均点の向上に安心し、見落とされがちな情意の格差や思考の二極化を是正することが喫緊の課題です。"
                "テスト対策に偏重した指導体制を見直し、探究型学習の評価基準の明確化や、教員がゆとりを持って個別最適な対話指導を行える指導体制の拡充が強く求められます。"
            )
        else:
            exec_summary = (
                f"本分析では、{dataset.source_name}の最新公的統計を活用し、情報教育・プログラミング教育および学校ICT環境の実態を多角的に分析しました。"
                f"データからは、{insights_bullets}が明確に裏付けられています。"
                f"GIGAスクール構想によりハードウェア環境は全国的に充足されたものの、ツールを『文房具として探究に活かす』深度には学校種・自治体間で予期せぬ二極化が進行しています。"
            )
            counter_intuitive = (
                "【常識とデータの逆説：端末配備率100%が覆い隠す『利活用の二極化』】\n"
                "1人1台端末の配備が完了したことで、『学校教育のデジタル化は達成された』と認識されがちです。"
                "しかし実態データを精緻に分析すると、単なる調べ学習やドリル反復にとどまる学校と、プログラミングや協働データ分析を日常的に実践する学校との間で、"
                "かつてない『利活用深度の新たな格差』が急拡大しています。インフラの充足が、かえって教員の指導力や学校現場の授業デザイン格差を鮮明にするという皮肉な現実が浮き彫りとなっています。"
            )
            pedagogy = (
                "【現場の盲点を突く情報教育・プログラミング指導の実践示唆】\n"
                "1. 『操作の習得』から『課題解決のアルゴリズム構築』への転換: アプリの基本操作や文法記憶を目的化せず、身近な学校・地域課題を解決するための手順を生徒自身にモデリング・自動化させる実践を組み込みます。\n"
                "2. エラーログを学びに変えるデバッグ文化の醸成: プログラミングにおけるエラー（バグ）を『失敗』ではなく『思考を深める最大の好機』と位置づけ、他者と協働して原因を究明するデバッグ体験を通じて計算論的思考を鍛えます。\n"
                "3. 教員間実践コミュニティによる伴走支援: 突出した一部の先進教員に依存する体制を脱し、日常授業での小さなICT活用アイデアを校内で日常的に共有する仕組みづくりが不可欠です。"
            )
            policy = (
                "【今後の展望と高度IT人材育成への課題】\n"
                "高等教育における情報・STEM系進路への接続や国際比較の観点からも、形式的な端末利用を超えた本質的リテラシーの育成が不可欠です。"
                "生成AI時代における情報モラル・データリテラシー教育の抜本的強化とともに、地域間・学校間の指導体制格差を埋める専門指導員の重点配置が強く求められます。"
            )

        return EducationalInsights(
            executive_summary=exec_summary,
            counter_intuitive_finding=counter_intuitive,
            pedagogical_implications=pedagogy,
            future_challenges_and_policy=policy,
        )
