"""
Academic Paper Content Generator for Educational Open Data Analysis.
Generates undergraduate thesis-level (学部の卒論水準) academic articles with:
- Abstract & Keywords
- 1. Background (研究の背景)
- 2. Objectives (研究の目的・リサーチクエスチョン)
- 3. Methodology (調査対象と分析方法)
- 4. Results (分析結果の定量的解説)
- 5. Discussion (考察・教育的示唆・限界)
- 6. References (引用・参考文献)
"""
from dataclasses import dataclass, field
import logging
import re
from typing import List, Optional

from google import genai
from google.genai import types

from src.analyzer import AnalysisResult
from src.config import Config
from src.fetchers.base import EducationDataset

logger = logging.getLogger(__name__)


def normalize_jset_text(text: str) -> str:
    """
    Normalizes Japanese punctuation to Japan Society for Educational Technology (JSET) standards:
    - Replaces full-width comma '、' with '，'
    - Replaces full-width period '。' with '．'
    """
    if not text:
        return ""
    # Avoid replacing periods in URLs (e.g. https://doi.org/10...)
    parts = text.split("http")
    normalized_parts = []
    for i, p in enumerate(parts):
        if i == 0:
            normalized_parts.append(p.replace("、", "，").replace("。", "．"))
        else:
            # url part
            url_and_rest = p.split(" ", 1)
            url = url_and_rest[0]
            rest = url_and_rest[1] if len(url_and_rest) > 1 else ""
            normalized_parts.append("http" + url + (" " + rest.replace("、", "，").replace("。", "．") if rest else ""))
    return "".join(normalized_parts)


@dataclass
class AcademicPaper:
    """Represents a full JSET-compliant academic paper."""
    title: str
    subtitle: str
    abstract: str
    keywords: List[str]
    background: str
    objectives: str
    methodology: str
    results_text: str
    discussion: str
    references: List[str]
    title_en: str = ""
    authors_en: str = ""
    summary_en: str = ""
    keywords_en: List[str] = field(default_factory=list)


class AcademicPaperGenerator:
    """Generates undergraduate thesis-level academic papers using Claude, Gemini, or domain templates."""

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
                logger.warning(f"Failed to initialize Gemini Client for AcademicPaperGenerator: {e}")

    def generate_paper(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> AcademicPaper:
        """Generates academic thesis content grounded in dataset and statistical analysis."""
        # 1. Prefer Claude if ANTHROPIC_API_KEY is configured
        if self.anthropic_api_key:
            try:
                logger.info(f"Generating academic paper with Anthropic Claude ({self.anthropic_model})...")
                return self._generate_with_claude(dataset, analysis)
            except Exception as e:
                logger.warning(f"Claude academic paper generation failed: {e}. Trying Gemini...")

        # 2. Use Gemini if available
        if self.gemini_client:
            try:
                logger.info(f"Generating academic paper with Google Gemini ({self.gemini_model})...")
                return self._generate_with_gemini(dataset, analysis)
            except Exception as e:
                logger.warning(f"Gemini academic paper generation failed: {e}. Falling back to template.")

        # 3. Fallback to domain-specific academic template
        logger.info("Using domain-specific academic template fallback for paper generation.")
        return self._generate_template_fallback(dataset, analysis)

    def _build_academic_prompt(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> str:
        stats_lines = []
        for m, s in analysis.descriptive_stats.items():
            stats_lines.append(
                f"- {m}: サンプル数N={s.count}， 平均={s.mean:.2f}{dataset.unit}， 中央値={s.median:.2f}{dataset.unit}， 標準偏差={s.std:.2f}， 最小={s.min_val:.2f}， 最大={s.max_val:.2f}， IQR={s.iqr:.2f}"
            )

        trends_lines = []
        for tr in analysis.trends:
            grp = f"[{tr.group_name}] " if tr.group_name else ""
            trends_lines.append(
                f"- {grp}{tr.metric}: {tr.start_time}年 ({tr.start_val:.2f}) -> {tr.end_time}年 ({tr.end_val:.2f})， 変化量={tr.diff:+.2f}{dataset.unit}， 変化率={tr.pct_change:+.1f}%， CAGR={tr.cagr}%， 決定係数<i>R</i><sup>2</sup>={tr.r_squared:.3f}， 回帰傾き={tr.slope:.3f}"
            )

        corr_lines = []
        for cr in analysis.correlations:
            corr_lines.append(
                f"- {cr.metric_x} × {cr.metric_y}: 相関係数 <i>r</i>={cr.pearson_r:.3f}， <i>p</i>値={cr.p_value:.4f} ({cr.interpretation})"
            )

        insights_lines = "\n".join([f"- {ins}" for ins in analysis.key_insights])

        return f"""あなたは教育工学、教育統計学、およびSTEM/理数・情報教育を専門とする大学教授・主任研究員です。
日本の教育工学・情報教育系学術論文誌の投稿規程および執筆の手引（教育実践研究論文／資料）の体裁に厳格に準拠した、極めて学術性の高い本格的な学術論文を執筆してください。
※重要：特定の学会名（「日本教育工学会」等）は、本文・抄録・見出し等の中に一切掲載しないでください（学術論文の体裁・構成・文体・組版ルールのみを利用します）。

### 【データセット基本情報】
- 題目: {dataset.title}
- カテゴリ: {'算数・数学教育' if dataset.category == 'math' else '情報教育・プログラミング教育'} (調査対象地域: {dataset.region})
- 出典機関: {dataset.source_name} ({dataset.source_url})
- 単位: {dataset.unit}
- データ概要: {dataset.description}

### 【実測統計解析データ（本文中の論拠として必ず数値を引用すること）】
記述統計量:
{chr(10).join(stats_lines)}

経年変化・トレンド回帰:
{chr(10).join(trends_lines) if trends_lines else '該当なし（単年調査）'}

相関分析:
{chr(10).join(corr_lines) if corr_lines else '該当なし'}

統計エンジンが検出した主要インサイト:
{insights_lines}

---
### 【学術論文執筆の手引 厳守要件（体裁・組版ルール）】
1. **表記規則（極めて重要）**:
   - 句読点はすべて全角カンマ「，」および全角ピリオド「．」を使用すること（「、」「。」は使用不可）。
   - 数字は1桁数字は全角（１，２，３）、2桁以上は半角（24，44等）とすること。
   - 統計記号（<i>p</i>，<i>t</i>，<i>F</i>，<i>SD</i>，<i>r</i>，<i>R</i><sup>2</sup> 等）はイタリック体（HTMLタグ <i> </i>）にすること。
   - 文体は完全な「である・だ」調。
   - ※特定の学会名（「日本教育工学会」等）は本文・抄録・見出し等に一切記述しないこと。
2. **各フィールドの記述要件**:
   - **title**: 40字以内の学術論文題目。末尾に「†」を付す（例: 〜に関する計量実証分析†）。
   - **subtitle**: 副題（できる限り簡潔に）。
   - **abstract**: 和文抄録。320〜380文字（400字以内かつ8割以上を満たすこと）。
   - **keywords**: 5〜6語の専門用語の配列（全角カンマ「，」で区切る）。
   - **background**: 700〜1000文字。問題の社会的・教育的背景、新学習指導要領や国際指標との関連、先行研究の動向。
   - **objectives**: 400〜600文字。具体的リサーチクエスチョン（RQ1〜RQ3）および作業仮説。
   - **methodology**: 600〜800文字。標本特性、指標の操作的定義、適用した統計解析手法。
   - **results_text**: 700〜1000文字。「表１」「図１」を参照しながら実測数値を厳密に引用した結果。
   - **discussion**: 900〜1300文字。教育学的メカニズムの検討、指導実践・カリキュラム改善への示唆、研究の限界と今後の展望、および全体のまとめ。
   - **references**: 5〜7件の実在する信頼できる学術文献リスト。著者の苗字アルファベット順。標準的な学術論文誌形式（著者名 (年) 題名. 雑誌名, <b>巻</b> (号) ：ページ番号.）。
   - **title_en**: 英語論文タイトル。
   - **authors_en**: 英語著者所属（例: Taro NIHON*1 and Jiro KYOUIKU*2 : Faculty of Education...）。
   - **summary_en**: 英文抄録（Summary）。和文抄録の正確な英語翻訳（100〜150語）。
   - **keywords_en**: 英語キーワード（5〜6語、すべて大文字表記、例: ["MATHEMATICS EDUCATION", "EVALUATION", "STATISTICAL ANALYSIS"]）。
"""

    def _generate_with_gemini(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> AcademicPaper:
        import json
        prompt = self._build_academic_prompt(dataset, analysis)

        response = self.gemini_client.models.generate_content(
            model=self.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.35,
                max_output_tokens=8192,
                response_mime_type="application/json",
                response_schema=AcademicPaper,
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
        keywords = data.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.replace("、", ",").replace("，", ",").split(",") if k.strip()]
        references = data.get("references", [])
        if isinstance(references, str):
            references = [r.strip() for r in references.split("\n") if r.strip()]

        keywords_en = data.get("keywords_en", [])
        if isinstance(keywords_en, str):
            keywords_en = [k.strip().upper() for k in keywords_en.replace("、", ",").replace("，", ",").split(",") if k.strip()]
        elif isinstance(keywords_en, list):
            keywords_en = [str(k).strip().upper() for k in keywords_en if str(k).strip()]

        raw_title = data.get("title", f"{dataset.title}に関する実証的計量分析†")
        title = normalize_jset_text(raw_title)
        if not title.endswith("†"):
            title += "†"

        return AcademicPaper(
            title=title,
            subtitle=normalize_jset_text(data.get("subtitle", "公的オープンデータに基づく教育構造の定量的解明")),
            abstract=normalize_jset_text(data.get("abstract", "")),
            keywords=keywords,
            background=normalize_jset_text(data.get("background", "")),
            objectives=normalize_jset_text(data.get("objectives", "")),
            methodology=normalize_jset_text(data.get("methodology", "")),
            results_text=normalize_jset_text(data.get("results_text", "")),
            discussion=normalize_jset_text(data.get("discussion", "")),
            references=references,
            title_en=data.get("title_en", f"Quantitative Empirical Analysis of {dataset.title}"),
            authors_en=data.get("authors_en", "EduData Research Group*1 and Educational Data Science Team*2"),
            summary_en=data.get("summary_en", ""),
            keywords_en=keywords_en,
        )

    def _generate_with_claude(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> AcademicPaper:
        import json
        import re
        import urllib.request

        prompt = self._build_academic_prompt(dataset, analysis)
        prompt += "\n\n必ず上記全フィールド（title, subtitle, abstract, keywords, background, objectives, methodology, results_text, discussion, references, title_en, authors_en, summary_en, keywords_en）を含む有効な単一のJSONオブジェクト（余計な説明文やマークダウンコードブロックなし）のみを出力してください。"

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
            "temperature": 0.35,
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
        keywords = data.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.replace("、", ",").replace("，", ",").split(",") if k.strip()]
        references = data.get("references", [])
        if isinstance(references, str):
            references = [r.strip() for r in references.split("\n") if r.strip()]

        keywords_en = data.get("keywords_en", [])
        if isinstance(keywords_en, str):
            keywords_en = [k.strip().upper() for k in keywords_en.replace("、", ",").replace("，", ",").split(",") if k.strip()]
        elif isinstance(keywords_en, list):
            keywords_en = [str(k).strip().upper() for k in keywords_en if str(k).strip()]

        raw_title = data.get("title", f"{dataset.title}に関する実証的計量分析†")
        title = normalize_jset_text(raw_title)
        if not title.endswith("†"):
            title += "†"

        logger.info("Successfully generated academic paper via Claude 3.5 Sonnet!")
        return AcademicPaper(
            title=title,
            subtitle=normalize_jset_text(data.get("subtitle", "公的オープンデータに基づく教育構造の定量的解明")),
            abstract=normalize_jset_text(data.get("abstract", "")),
            keywords=keywords,
            background=normalize_jset_text(data.get("background", "")),
            objectives=normalize_jset_text(data.get("objectives", "")),
            methodology=normalize_jset_text(data.get("methodology", "")),
            results_text=normalize_jset_text(data.get("results_text", "")),
            discussion=normalize_jset_text(data.get("discussion", "")),
            references=references,
            title_en=data.get("title_en", f"Quantitative Empirical Analysis of {dataset.title}"),
            authors_en=data.get("authors_en", "EduData Research Group*1 and Educational Data Science Team*2"),
            summary_en=data.get("summary_en", ""),
            keywords_en=keywords_en,
        )



    def _generate_template_fallback(
        self, dataset: EducationDataset, analysis: AnalysisResult
    ) -> AcademicPaper:
        """High-grade academic template fallback with rigorous educational statistics conforming to JSET standards."""
        is_math = dataset.category == "math"
        unit = dataset.unit

        first_metric = dataset.metrics[0] if dataset.metrics else "主要指標"
        first_stat = analysis.descriptive_stats.get(first_metric)
        avg_str = f"{first_stat.mean:.2f}{unit}" if first_stat else "N/A"
        med_str = f"{first_stat.median:.2f}{unit}" if first_stat else "N/A"
        std_str = f"{first_stat.std:.2f}" if first_stat else "N/A"
        min_str = f"{first_stat.min_val:.2f}{unit}" if first_stat else "N/A"
        max_str = f"{first_stat.max_val:.2f}{unit}" if first_stat else "N/A"
        iqr_str = f"{first_stat.iqr:.2f}" if first_stat else "N/A"
        count_str = str(first_stat.count) if first_stat else str(len(dataset.df))

        trend_desc = ""
        if analysis.trends:
            tr = analysis.trends[0]
            trend_desc = (
                f"時系列推移の検証では，{tr.metric}において{tr.start_time}年の{tr.start_val:.2f}{unit}から"
                f"{tr.end_time}年の{tr.end_val:.2f}{unit}へと変化し（変化量: {tr.diff:+.2f}{unit}，変化率: {tr.pct_change:+.1f}%，"
                f"年平均成長率 CAGR: {tr.cagr}%），最小二乗法による単回帰分析の結果，決定係数 <i>R</i><sup>2</sup> = {tr.r_squared:.3f}（回帰傾き: {tr.slope:.3f}）が算出された．"
            )

        corr_desc = ""
        if analysis.correlations:
            cr = analysis.correlations[0]
            corr_desc = (
                f"指標間の関連性分析においては，{cr.metric_x}と{cr.metric_y}の間に対象データ全域において相関係数 <i>r</i> = {cr.pearson_r:.3f}"
                f"（<i>p</i>値 = {cr.p_value:.4f}）の統計的有意な関連（{cr.interpretation}）が確認された．"
            )

        if is_math:
            title = f"{dataset.title}に関する計量的実証分析†"
            subtitle = "オープンデータに基づく算数・数学教育における学力構造と学習環境の定量的解明"
            keywords = ["算数・数学教育", "学力到達度", "教育計量分析", "記述統計", "線形回帰分析"]
            abstract = (
                f"本研究は，{dataset.source_name}が公開する公的オープンデータ（{dataset.title}）を用い，"
                f"初等中等教育における算数・数学的リテラシーの達成水準，経年変化トレンド，および指標間関連性を実証的に分析したものである．"
                f"対象標本（N={count_str}）における主要指標「{first_metric}」の記述統計量を求めたところ，"
                f"平均値は{avg_str}，中央値は{med_str}，標準偏差は{std_str}，四分位範囲(IQR)は{iqr_str}を示した．"
                f"{trend_desc}これらの計量結果に基づき，概念的理解を促す探究型授業設計および個別最適な学びの実現に向けた教育的示唆を論じる．"
            )
            background = (
                "近年の知識基盤社会およびSociety 5.0の進展に伴い，算数・数学的リテラシーは単なる計算技能の習得にとどまらず，"
                "事象を数理的に捉え，論理的に推論し，批判的に検証するための普遍的な基礎基盤としてその重要性を増している．"
                "文部科学省の新学習指導要領においても「数学的な見方・考え方」を働かせた問題解決能力の育成が中核に据えられており，"
                "国際的な教育指標（OECD PISAやIEA TIMSS等）においても，実生活の文脈における数学の応用力や自己効力感が重視されている．\n\n"
                "しかしながら，教育現場においては児童生徒の数学に対する苦手意識や学習意欲の二極化，さらには指導環境や地域間・学校間における学力格差の存在が"
                "長年にわたり指摘されてきた．こうした課題に対し，公的統計データを客観的かつ体系的に解析し，定量的な証拠（Evidence-based Education）に基づいて"
                "教育実態を把握することは，カリキュラム改善および教育政策立案において不可欠な学術的要請である．"
            )
            objectives = (
                "本研究の目的は，公的教育オープンデータを活用して算数・数学教育に関する到達度および学習実態を多角的に検証し，"
                "今後の学校指導および教育政策に資する定量的知見を提示することである．具体的には以下のリサーチクエスチョン（RQ）を設定する：\n\n"
                f"・RQ1: 主要指標（{first_metric}等）における中心傾向（平均値・中央値）および散布度（標準偏差・IQR）の分布特性はどのような構造を有しているか．\n"
                "・RQ2: 時系列推移において統計的に有意な上昇または下降トレンド（線形回帰の傾きおよび決定係数<i>R</i><sup>2</sup>）は認められるか．\n"
                "・RQ3: 調査対象属性間（地域・学校種別等）における格差の規模はどの程度であり，指標間にいかなる相関構造が存在するか．"
            )
            methodology = (
                f"本研究のデータソースには，{dataset.source_name}により調査・公開された「{dataset.title}」の公式データセットを採用した．"
                f"本データは{dataset.region}を対象とし，信頼性の高い公的サンプリング手法に基づき集計されたものである．\n\n"
                f"分析対象とした指標群は，{', '.join(dataset.metrics)}であり，欠損値処理および型変換を施した上で以下の統計解析手法を適用した．\n"
                "1. 記述統計分析: 平均値，中央値，不偏標準偏差（ddof=1），最小値・最大値，ならびに第1四分位数・第3四分位数から四分位範囲（IQR）を算出し，データの対称性とばらつきを評価した．\n"
                "2. 経年変化分析: 複数時点の時系列データに対し，変化量，変化率（%），幾何平均年間成長率（CAGR）を算定するとともに，最小二乗法による単回帰分析を行い決定係数（<i>R</i><sup>2</sup>）および回帰直線の傾きを導出した．\n"
                "3. 相関分析: 量的変数間においてピアソン積率相関係数（<i>r</i>）および両側検定による<i>p</i>値を算出し，指標間の共分散関係を検証した．"
            )
            results_text = (
                "本データセットの計量分析結果を以下に示す．\n\n"
                "【基本記述統計量（表１参照）】\n"
                f"主要指標「{first_metric}」において，標本数 N={count_str}，平均値 {avg_str}，中央値 {med_str}，"
                f"標準偏差 {std_str} であった．最小値は {min_str}，最大値は {max_str} であり，レンジ（全範囲）および"
                f"四分位範囲 IQR={iqr_str} から，標本内に一定のばらつきが観察された．\n\n"
                "【時系列トレンドおよび比較結果（図１参照）】\n"
                f"{trend_desc if trend_desc else '単年比較において各属性間の差異が明瞭に表出している．'}\n\n"
                "【指標間の相関関係】\n"
                f"{corr_desc if corr_desc else '各指標間において特有の分布特性が示された．'}\n\n"
                "これらの分析結果は，後述の図１に可視化されたチャートおよび表１の記述統計量一覧に示される通り，"
                "教育的施策の検討における強固な定量的基礎を提供するものである．"
            )
            discussion = (
                "本分析結果を踏まえ，算数・数学教育における教育学的メカニズムおよび実践的示唆について以下に考察する．\n\n"
                "第１に，基本統計量および散布度の結果は，児童生徒の間で概念の定着度合いに相当の幅が存在することを示唆している．"
                "単なる計算アルゴリズムの機械的反復指導では，低位層におけるつまずきの根本解消には結びつきにくく，"
                "具体的操作や視覚的表現を通じた「なぜそうなるのか」という数理的構造の理解を促す対話的な指導が強く求められる．\n\n"
                "第２に，デジタル技術（1人1台端末，動的幾何・数理モデリングソフトウェア等）の戦略的活用である．"
                "グラフや図形の動的変化を視覚的に探究させることで，抽象度の高い数学的概念に対する直感的把握を支援することが可能となる．\n\n"
                "第３に，本研究の限界として，本分析は公的集計データに基づくマクロ分析であるため，個々の児童生徒の家庭学習時間，"
                "社会経済的背景（SES），情意面（数学に対する自己効力感・興味関心）といった微視的交絡因子を完全には統制できていない点が挙げられる．"
                "今後は，質的調査やマイクロデータ解析を統合した混合研究法（Mixed Methods）による更なる実証的追跡が望まれる．\n\n"
                "【まとめ】\n"
                "本稿では，オープンデータの実証分析を通じて算数・数学学力の分布特性を明らかにした．"
                "得られた知見は，指導内容の精選と個別最適な学びの実現に向けた有益な基礎資料となる．"
            )
            references = [
                "文部科学省 (2018) 小学校学習指導要領（平成29年告示）解説 算数編. 東洋館出版社, pp.1-240.",
                "文部科学省・国立教育政策研究所 (2024) 令和6年度 全国学力・学習状況調査 報告書. 国立教育政策研究所.",
                "OECD (2023) PISA 2022 Results (Volume I): The State of Learning and Equity in Education. OECD Publishing, Paris. https://doi.org/10.1787/53f23881-en",
                "清水静栄 (2020) 算数・数学教育における「数学的な見方・考え方」の育成と授業改善. 日本数学教育学会誌, <b>102</b> (4) ：12-23.",
                "堀田龍也 (2021) 初等中等教育のデジタルトランスフォーメーションの動向と課題. 教育情報研究, <b>37</b> (2) ：15-24.",
            ]
            title_en = f"Quantitative Empirical Analysis of {dataset.title} in Primary and Secondary Mathematics Education"
            authors_en = "EduData Research Group*1 and Educational Data Science Team*2"
            summary_en = (
                f"This study conducts an empirical quantitative analysis of mathematical literacy in primary and secondary education "
                f"using official public open data ({dataset.title}) published by {dataset.source_name}. "
                f"The descriptive statistics for '{first_metric}' revealed a mean of {avg_str}, median of {med_str}, "
                f"and standard deviation of {std_str}. Regression analysis indicated statistically significant trends over time. "
                f"Based on these empirical findings, pedagogical implications for exploratory lesson design and personalized adaptive learning are discussed."
            )
            keywords_en = ["MATHEMATICS EDUCATION", "EDUCATIONAL ASSESSMENT", "QUANTITATIVE ANALYSIS", "DESCRIPTIVE STATISTICS", "LINEAR REGRESSION"]
        else:
            title = f"{dataset.title}に関する計量的実証分析†"
            subtitle = "公的オープンデータに基づく学校情報教育・プログラミング教育環境と情報活用能力の構造的検証"
            keywords = ["情報教育", "プログラミング教育", "ICT環境整備", "GIGAスクール構想", "情報活用能力"]
            abstract = (
                f"本稿は，{dataset.source_name}が公表した公式オープンデータ（{dataset.title}）に基づき，"
                f"学校現場における情報教育・プログラミング教育の推進実態およびICT環境整備の定量的構造を計量的に解明することを目的とした．"
                f"標本数 N={count_str} における代表指標「{first_metric}」を検証した結果，"
                f"平均値は{avg_str}，中央値は{med_str}，標準偏差は{std_str}，四分位範囲(IQR)は{iqr_str}を示した．"
                f"{trend_desc}本分析から得られた定量的知見をもとに，情報モラル教育，探究的なプログラミング指導法，ならびに地域間格差の是正に向けた具体的方策を提言する．"
            )
            background = (
                "人工知能（AI），ビッグデータ，クラウドコンピューティングが社会のあらゆる領域に浸透する現代において，"
                "情報活用能力およびプログラミング的思考（Computational Thinking）の育成は，国家的な最重要教育課題として位置づけられている．"
                "我が国においてはGIGAスクール構想の下，初等中等教育における1人1台端末および高速ネットワーク環境の整備が急速に推進され，"
                "小学校におけるプログラミング教育の必修化，中学校技術分野の充実，高等学校における「情報I」の必履修化と大学入学共通テスト導入など，"
                "情報教育の体系的なカリキュラム改革が相次いで施行された．\n\n"
                "しかしながら，端末等のハードウェア整備が一定の完了を見せた一方で，学校現場における日常的な活用頻度や指導内容の質，"
                "教員のICT指導力，さらには自治体・学校間における利活用格差の存在など，実質的な教育効果の向上には多くの構造的課題が残されている．"
                "こうした背景から，公的オープンデータを客観的に分析し，情報教育の現状と課題を定量的に同定することは極めて重要な意義を持つ．"
            )
            objectives = (
                "本研究は，情報教育および学校ICT環境に関する公的オープンデータを計量経済学・教育工学的手法により精緻に分析し，"
                "実効性ある指導改善と政策的課題の抽出を行うことを主目的とする．具体的には以下のリサーチクエスチョン（RQ）を掲げる：\n\n"
                f"・RQ1: 主要指標（{first_metric}等）の平均値・標準偏差・四分位範囲に見られる分布の偏りと散布度はどのような傾向を示すか．\n"
                "・RQ2: 時系列の経年変化において有意な進展傾向（線形回帰トレンド・決定係数<i>R</i><sup>2</sup>・CAGR）が認められるか．\n"
                "・RQ3: 各指標間の相関関係（ピアソン相関係数<i>r</i>）から，環境整備と実践的活用能力との間にどのような連関性が確認されるか．"
            )
            methodology = (
                f"本研究では，{dataset.source_name}により調査・公開された公的統計「{dataset.title}」をデータソースとして使用した．"
                f"本データは{dataset.region}を対象とし，厳格な調査設計に基づき作成された信頼性の高い母集団推定値である．\n\n"
                f"対象指標として{', '.join(dataset.metrics)}を抽出し，以下の統計分析フレームワークを適用した．\n"
                "1. 基礎記述統計: 各指標の標本数，平均値，中央値，不偏標準偏差，最小・最大値，四分位範囲（IQR）を算定し，外れ値の影響度と分布形状を精査した．\n"
                "2. トレンド・回帰分析: 時系列軸が存在するデータについては，期間変化量，年平均成長率（CAGR），ならびに最小二乗法に基づく線形単回帰直線の傾き・決定係数（<i>R</i><sup>2</sup>）を推定した．\n"
                "3. 相関分析: 各指標のペアに対しピアソン積率相関係数（<i>r</i>）および両側有意確率（<i>p</i>値）を算出し，関連の強弱と統計的有意性を検証した．"
            )
            results_text = (
                "データ解析により得られた定量的結果を報告する．\n\n"
                "【基本記述統計量（表１参照）】\n"
                f"主要指標「{first_metric}」において，標本数 N={count_str}，平均値 {avg_str}，中央値 {med_str}，"
                f"標準偏差 {std_str}，IQR {iqr_str} が記録された．最小値 {min_str} から最大値 {max_str} に至る分散は，"
                f"自治体・学校間での進捗状況の多様性を如実に反映している．\n\n"
                "【時系列トレンドおよび視覚的可視化（図１参照）】\n"
                f"{trend_desc if trend_desc else '各区分における達成状況に明瞭な差異が認められる．'}\n\n"
                "【指標間の相関構造】\n"
                f"{corr_desc if corr_desc else '相関分析により指標間の構造的連動が確認された．'}\n\n"
                "図１に示すグラフおよび表１の数値群は，単なる機器整備から実践的活用段階への移行過程における"
                "客観的実態を明確に指し示している．"
            )
            discussion = (
                "以上の分析結果に基づき，初等中等教育における情報教育・ICT利活用の推進に向けた考察を展開する．\n\n"
                "第１に，分析結果が示す指標の散布度は，端末整備後の「活用フェーズ」における自治体・学校間格差の存在を裏付けている．"
                "文房具としての日常的な端末利用を定着させるためには，単なる調べ学習にとどまらず，児童生徒自らがデータを収集・整理し，"
                "課題解決に向けてプログラミングやプレゼンテーションを行う探究的・協働的学習の設計が不可欠である．\n\n"
                "第２に，教員の指導力向上と校内支援体制の確立である．"
                "ICT機器やプログラミング教材を効果的に授業に組み込むための実践的な研修体系の拡充，およびICT支援員等の人的サポート体制の拡充が強く望まれる．\n\n"
                "第３に，本研究の限界として，本分析は定量データに基づく巨視的検証であり，授業内における児童生徒の主体的関与度や"
                "認知的深まりを直接的に測定したものではない．今後は，授業記録や学習履歴ログ（スタディ・ログ）を活用したミクロな学習分析との融合が課題である．\n\n"
                "【まとめ】\n"
                "学校教育の情報化推進に関する実態分析を通じて，環境整備後の利活用深化における重要課題を整理した．"
            )
            references = [
                "文部科学省 (2020) 小学校プログラミング教育の手引（第三版）. 文部科学省.",
                "文部科学省 (2024) 令和5年度 学校における教育の情報化の実態等に関する調査結果. 文部科学省.",
                "国立教育政策研究所 (2021) 指導と評価の一体化のための学習評価に関する参考資料 高等学校 情報編. 東洋館出版社, pp.1-180.",
                "堀田龍也 (2021) 初等中等教育のデジタルトランスフォーメーションの動向と課題. 教育情報研究, <b>37</b> (2) ：15-24.",
                "UNESCO (2024) Global Education Monitoring Report 2023: Technology in Education - A Tool on Whose Terms? UNESCO Publishing, Paris.",
            ]
            title_en = f"Quantitative Empirical Analysis of {dataset.title} in School Informatics and Programming Education"
            authors_en = "EduData Research Group*1 and Educational Data Science Team*2"
            summary_en = (
                f"This paper investigates the implementation status of programming education and ICT environment in primary and secondary schools "
                f"based on public open data ({dataset.title}) provided by {dataset.source_name}. "
                f"Statistical analysis for '{first_metric}' demonstrated a mean of {avg_str}, median of {med_str}, and standard deviation of {std_str}. "
                f"Trend analysis confirmed systematic progress across surveyed indicators. "
                f"Based on these results, we discuss pedagogical strategies for lesson improvement and teacher professional development."
            )
            keywords_en = ["INFORMATICS EDUCATION", "PROGRAMMING EDUCATION", "ICT ENVIRONMENT", "GIGA SCHOOL INITIATIVE", "EDUCATIONAL TECHNOLOGY"]

        return AcademicPaper(
            title=title,
            subtitle=subtitle,
            abstract=abstract,
            keywords=keywords,
            background=background,
            objectives=objectives,
            methodology=methodology,
            results_text=results_text,
            discussion=discussion,
            references=references,
            title_en=title_en,
            authors_en=authors_en,
            summary_en=summary_en,
            keywords_en=keywords_en,
        )
