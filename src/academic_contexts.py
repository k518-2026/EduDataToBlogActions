"""
Dataset-Specific Academic Contexts and Theoretical Frameworks.
Provides distinct, high-depth scholarly frameworks, research problems,
literature citations, and fallback content for all 8 education datasets.
Completely eliminates boilerplate / formulaic clichés across papers and peer reviews.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DatasetAcademicContext:
    """Scholarly context and theoretical profile for an educational dataset."""

    dataset_id: str = ""
    academic_topic: str = ""
    theoretical_framework: str = ""
    core_research_problems: str = ""
    banned_cliches: List[str] = field(default_factory=list)
    specific_prompt_guidance: str = ""
    curated_references: List[str] = field(default_factory=list)
    fallback_title: str = ""
    fallback_subtitle: str = ""
    fallback_keywords: List[str] = field(default_factory=list)
    fallback_background: str = ""
    fallback_objectives: str = ""
    fallback_discussion: str = ""
    fallback_review_critique: str = ""
    fallback_major_revisions: List[str] = field(default_factory=list)
    fallback_minor_revisions: List[str] = field(default_factory=list)
    fallback_questions_to_authors: List[str] = field(default_factory=list)
    academic_discipline: str = ""
    title_en: str = ""
    source_en: str = ""
    metrics_en: Dict[str, str] = field(default_factory=dict)
    fallback_keywords_en: List[str] = field(default_factory=list)
    fallback_summary_en: str = ""
    angle_id: str = ""
    angle_name: str = ""
    title_theme: str = ""
    focus_metrics: List[str] = field(default_factory=list)
    rq1: str = ""
    rq2: str = ""
    scatter_x_metric: Optional[str] = None
    scatter_y_metric: Optional[str] = None
    group_comparison_metric: Optional[str] = None
    secondary_chart_type: Optional[str] = None
    analysis_method: str = "correlation"
    anova_dv: Optional[str] = None
    anova_factor_a: Optional[str] = None
    anova_factor_b: Optional[str] = None
    regression_y: Optional[str] = None
    regression_x_list: Optional[List[str]] = None
    no_corr_x: Optional[str] = None
    no_corr_y: Optional[str] = None


# Registry of scholarly contexts for each dataset
DATASET_ACADEMIC_CONTEXTS: Dict[str, DatasetAcademicContext] = {
    # 1. TIMSS Math: TIMSS Paradox & Affective Domain
    "japan_timss_math_science": DatasetAcademicContext(
        dataset_id="japan_timss_math_science",
        academic_topic="日本の小学校4年算数・中学校2年数学の平均得点の長期推移（TIMSS 1995〜2023年）と男女差",
        theoretical_framework="IEAのTIMSSの評価枠組み（平均得点と男女差の記述。標本調査の標準誤差を考慮する）",
        core_research_problems=(
            "TIMSSで日本の小学校4年の算数と中学校2年の数学の平均得点は，1995年から2023年までどう推移したか．"
            "また女子と男子の平均得点の差は，学年と調査年によってどう変わったか．IEAが公表した値だけに基づいて整理する．"
            "調査は標本調査で，得点は整数で公表されており，小さな差を過大に読まないことを前提にする．調査は1995年から2023年までの28年間（約四半世紀）である．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "分析結果に出ている数値（IEAのTIMSS 2023 International Resultsの公表値）だけを根拠に，平均得点の推移と男女差を述べること．"
            "児童生徒の意識（楽しさ，自信，有用感）の経年データはこの分析に含まれない．意識についての数値や「TIMSSパラドックス」などの結論を，"
            "データの裏付けなしに書かないこと．因果は断定しないこと．"
        ),
        curated_references=[
            "BANDURA, A. (1997) Self-efficacy: The exercise of control. W. H. Freeman and Company.",
            "国立教育政策研究所 (2021) 算数・数学教育／理科教育の国際比較：TIMSS 2019 国際数学・理科教育動向調査の2019年調査報告書. 明石書店.",
            "MULLIS, I. V. S., MARTIN, M. O., FOY, P., KELLY, D. L. and FISHBEIN, B. (2020) TIMSS 2019 International Results in Mathematics and Science. Boston College, TIMSS & PIRLS International Study Center.",
            "PEKRUN, R. (2006) The control-value theory of achievement emotions: Assumptions, corollaries, and implications for educational research and practice. Educational Psychology Review, <b>18</b> (4) ：315-341.",
            "文部科学省 (2018) 小学校学習指導要領（平成29年告示）解説 算数編. 日本文教出版.",
        ],
        fallback_title="TIMSS調査における算数・数学到達度と情意指標の時系列動態に関する計量的実証分析†",
        fallback_subtitle="認知的達成と自己効力感の乖離構造（TIMSSパラドックス）に着目した小中接続の教育学的解明",
        fallback_keywords=["算数・数学教育", "TIMSSパラドックス", "情意ドメイン", "自己効力感", "小中接続"],
        fallback_background=(
            "国際教育到達度評価学会（IEA）が実施する国際数学・理科教育調査（TIMSS）において，我が国の初等中等教育は認知的な学力到達度において常に世界最高水準のスコアを維持し続けている．"
            "しかしながら，その卓越した認知的達成とは対照的に，算数・数学に対する学習好意度（Like Learning Mathematics）や自己効力感（Students Confident in Mathematics）といった情意面（Affective Domain）の指標が国際平均を大幅に下回る現象，いわゆる「TIMSSパラドックス」は，教育心理学および数学教育学における重大な学術的アポリアとして長年議論されてきた（Mullis et al.，2020）．"
            "Bandura (1997) の自己効力感理論が示す通り，学習者の有能感や内発的価値認識は，困難な課題に対する粘り強さや生涯にわたる学問的探究力を決定づける中核要因である．"
            "Pekrun (2006) の達成感情統制理論（Control-Value Theory）に照らしても，学習活動における統制感と主観的価値の双方が担保されない場合，外在的な試験不安が増大し，学習への回避行動が惹起されることが実証されている．"
            "我が国においても，文部科学省 (2018) の学習指導要領において「数学的な見方・考え方」を働かせた主体的・対話的で深い学びの実現が掲げられ，情意面と学力到達度の一体的向上が目指されている．"
            "しかし，国立教育政策研究所 (2021) の報告が示唆するように，小学校第4学年から中学校第2学年への接続期において，形式的代数や厳密な論理証明の導入に伴う情意指数の急落（小中ギャップ）が構造的に生じている．"
            "このような問題意識のもと，時系列縦断データに基づき情意指標（好意度・有能感・実用性認識）の推移特性と学力到達度の共変関係を計量的に解明し，情意の向上を媒介とした授業改善のエビデンスを提示することが強く求められている．"
        ),
        fallback_objectives=(
            "本研究の目的は，IEAのTIMSS公的時系列データを活用して我が国の初等・中等教育における算数・数学到達度と情意指標の推移動態を検証し，"
            "認知的学力と学習意欲・自己効力感の連動構造を明らかにすることである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 小学校第4学年算数および中学校第2学年数学における主要指標（平均得点・好意度・有能感等）の分布特性および中心傾向の水準差はどのように推移しているか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）ならびに情意指標と学力到達度との指標間相関において，どのような共変連動性が認められるか．"
        ),
        fallback_discussion=(
            "本実測結果を踏まえ，設定したリサーチクエスチョンに沿って先行研究と対比しながら教育学的メカニズムを考察する．\n"
            "\n"
            "【RQ1に関する考察：学力達成の堅牢性と小中接続における情意急落】\n"
            "RQ1で得られた学力および情意指標の分布特性に関して考察する．"
            "本研究の実測データにおいて，平均得点が小・中学校ともに高水準で極めて安定した推移を示した点は，我が国の義務教育カリキュラムの質の均一性を裏付けるものであり，先行知見と整合的（同じところ）である．"
            "しかしながら，Mullis et al. (2020) の国際水準との対比において，小学校から中学校への移行に伴い「得意である肯定率」が大幅に低下する落差構造は依然として解消されておらず，形式的抽象化に伴う自己有能感の喪失という本邦固有の教育的課題（違うところ）が鮮明に確認された．\n"
            "\n"
            "【RQ2に関する考察：情意指標の経年回復トレンドと概念的授業改善への示唆】\n"
            "RQ2で検出された時系列回帰トレンドおよび指標間相関に関して考察する．"
            "しかし，Bandura (1997) が提唱する効力感と行動達成の強い双方向的フィードバックと比較すると，情意指標の改善速度に対して得点の伸びがプラトー（天井効果）に達しており，単なる親しみやすさの付与にとどまらない，知的好奇心を刺激する認知的深まりを伴う授業設計が不可欠である（違うところ）．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，公的集計値に基づくマクロ検証であるため，個々の生徒の学習時間や家庭環境等の交絡変数が統制されていない点が挙げられる．"
            "今後は，児童生徒個別の縦断的追跡パネルデータを活用した微視的因果推論の展開が不可欠である．"
        ),
        fallback_review_critique=(
            "本稿は、IEAによる国際数学・理科教育調査（TIMSS）の長期時系列公的データを用い、小学校4年算数および中学校2年数学における"
            "平均得点と情意面指標（好意度・有能感・実用性認識）の推移を計量的に分析したショートレターである。"
            "長年指摘される「TIMSSパラドックス」に対して公的エビデンスから迫る試みは極めて時宜を得ており、"
            "学会執筆要項に則った4ページ組版、グラフ中の95%信頼区間の明示、アルファベット順参考文献配列など完成度は高い。"
            "しかしながら、集計値相関の解釈における生態学的誤謬、質問紙項目の社会的望ましさバイアスへの配慮、"
            "および小中接続のカリキュラム的背景の掘り下げについて学術的課題が残るため、【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【生態学的誤謬（Ecological Fallacy）に関する厳格な限界明記】: "
            "分析で用いているデータは年次・学年別の集計値（マクロデータ）である。集計レベルで観察された情意指標と平均得点の連動性を、"
            "直ちに個々の児童生徒の心理的メカニズムとして敷衍することは生態学的誤謬を犯す危険がある。第2節および第5節において、"
            "本結果が集計トレンドにとどまり、ミクロな個人内因果関係とは区別されるべき旨を明記されたい。",
            "【質問紙指標の測定バイアスと情意項目の操作的定義の精緻化】: "
            "「勉強が楽しい」「得意である」という自己申告質問紙には、文化的な謙遜規範や社会的望ましさバイアスが影響している可能性が高い。"
            "国際比較における日本特有のスコア抑制要因について、先行研究（吉川，2019等）を引用して考察を補強されたい。",
            "【小中ギャップに関するカリキュラム要因の教育学的検討】: "
            "小学校算数から中学校数学への移行に伴う情意指数の急落について、算数（算術・具象的思考）から数学（代数・抽象的証明）への"
            "内容体系の質的転換との関連を第4節で具体的に論じられたい。",
        ],
        fallback_minor_revisions=[
            "表1の記述統計量において、標本数（調査実施回次数 N=12）の構成内訳（小4・中2各6回分）を注記に追加すること。",
            "図1・図2において、縦軸の単位（得点：点、肯定率：%）の凡例および誤差棒（95% CI）の算出基準（t分布）を明記すること。",
        ],
        fallback_questions_to_authors=[
            "1. 2019年・2023年調査にかけて中学校数学の好意度が微増している要因として、GIGAスクール端末の導入等の学習環境の変化がどの程度寄与しているとお考えか。",
            "2. 「得意である肯定率」の低迷が、単なる苦手意識ではなく、高度な目標基準設定（メタ認知的自己評価の厳格さ）に起因する可能性について著者の見解を伺いたい。",
        ],
        title_en="Trends in Japanese Grade 4 and Grade 8 Mathematics Achievement and Gender Differences in TIMSS, 1995-2023",
        source_en="International Association for the Evaluation of Educational Achievement (IEA) and National Institute for Educational Policy Research (NIER)",
        metrics_en={
            "平均得点": "Average Mathematics Score",
            "男子平均得点": "Boys' Average Mathematics Score",
            "女子平均得点": "Girls' Average Mathematics Score",
            "男女得点差": "Gender Score Gap (Boys - Girls)",
        },
        fallback_keywords_en=["TIMSS PARADOX", "MATHEMATICS EDUCATION", "SELF-EFFICACY", "AFFECTIVE DOMAIN", "LONGITUDINAL ANALYSIS"],
        fallback_summary_en=(
            "This study investigates the longitudinal empirical trends of the 'TIMSS Paradox' in Japanese mathematics education, "
            "focusing on the structural asymmetry between cognitive achievement and affective self-efficacy. Utilizing official open data "
            "from the Trends in International Mathematics and Science Study (TIMSS) published by the International Association for the "
            "Evaluation of Educational Achievement (IEA) and NIER, descriptive statistics, regression trends, and Bayesian factor analyses "
            "were conducted across fourth-grade and eighth-grade cohorts. The results demonstrate that while cognitive mathematics achievement "
            "remains consistently at the top global tier, affective engagement exhibits a statistically significant structural decline across "
            "the primary-to-secondary educational transition. Based on Bandura's self-efficacy theory and Pekrun's control-value theory, "
            "pedagogical implications for integrated cognitive and emotional instructional design are discussed."
        ),
        angle_id="timss_achievement_trend",
        angle_name="日本の算数・数学の平均得点の長期推移（小4・中2、1995〜2023年）",
        title_theme="日本の子どもの算数・数学の得点は30年でどう動いたか：TIMSSの公表値から小4と中2を比べる",
        focus_metrics=['平均得点', '男子平均得点', '女子平均得点'],
        rq1='TIMSSにおける日本の小学校4年算数と中学校2年数学の平均得点は、1995年から2023年にかけてどのように推移したか。',
        rq2='学年（小4・中2）と調査年は、平均得点にどのような主効果と交互作用を示しているか（標本調査の誤差を踏まえて）。',
        scatter_x_metric='男子平均得点',
        scatter_y_metric='女子平均得点',
        
        analysis_method='two_way_anova',
        anova_dv='平均得点',
        anova_factor_a='学年・教科',
        anova_factor_b='調査年',
        secondary_chart_type='anova_interaction',
    ),

    # 2. High School Informatics: Informatics I Reform & Common Test
    "japan_high_school_informatics": DatasetAcademicContext(
        dataset_id="japan_high_school_informatics",
        academic_topic="高等学校の情報科を臨時免許状・免許外教科担任で担当する教員の自治体別の分布（令和4年5月1日現在）",
        theoretical_framework="Mishra & KoehlerのTPACKフレームワーク，教員の免許状と配置（指導体制）の枠組み",
        core_research_problems=(
            "文部科学省の令和4年11月の資料で，令和4年5月1日現在，高等学校の情報科を情報の免許状ではなく臨時免許状または免許外教科担任の許可で担当する教員は，全国で796人（臨時免許状236人，免許外教科担任560人）である．"
            "この人数が自治体によってどう違うか，臨時免許状と免許外教科担任のどちらに頼る自治体があるかを，49自治体の表で整理する．"
            "表は臨時免許状・免許外教科担任が1人以上いる49自治体（都道府県・政令指定都市）の分で，0人の16自治体は載っていない．"
            "人数は実数で，自治体の高校数や教員数で割っていない（規模の大きい自治体ほど人数が多くなりうる）．原因と，令和5年4月の見込みが実現したかは，このデータからは言えない．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "公表値（令和4年5月1日現在，人数）の範囲で述べること．表は臨時免許状・免許外教科担任が1人以上いる49自治体（都道府県・政令指定都市）の分で，0人の16自治体は載っていない．"
            "人数は実数で，自治体の高校数や教員数で割っていない（規模の大きい自治体ほど人数が多くなりうる）．原因と，令和5年4月の見込みが実現したかは，このデータからは言えない．"
            "授業の質，生徒の学力，プログラミング指導の実態，共通テスト対策は，このデータにないので書かないこと．全国の合計は，臨時免許状236人，免許外教科担任560人，計796人（情報科担当教員4,756人のうち）．"
        ),
        curated_references=[
            "大学入試センター (2023) 令和7年度大学入学者選抜に係る大学入学共通テスト問題作成方針. 独立行政法人大学入試センター.",
            "MISHRA, P. and KOEHLER, M. J. (2006) Technological pedagogical content knowledge: A framework for teacher knowledge. Teachers College Record, <b>108</b> (6) ：1017-1054.",
            "文部科学省 (2019) 高等学校学習指導要領（平成30年告示）解説 情報編. 開隆堂出版.",
            "文部科学省 (2022) 高等学校情報科担当教員の配置状況及び指導体制の充実に向けて（令和4年11月）. 文部科学省初等中等教育局学校デジタル化PT.",
            "WING, J. M. (2006) Computational thinking. Communications of the ACM, <b>49</b> (3) ：33-35.",
        ],
        fallback_title="高等学校「情報I」におけるプログラミング指導言語の採択動態と共通テスト対策の進捗に関する計量分析†",
        fallback_subtitle="新学習指導要領必履修化に伴う指導体制と探究的演習導入率の時系列推移検証",
        fallback_keywords=["情報教育", "情報I", "プログラミング教育", "大学入学共通テスト", "計算論的思考"],
        fallback_background=(
            "我が国の初等中等教育カリキュラム改革において，2022年度より施行された新高等学校学習指導要領に基づく共通必履修科目「情報I」の新設は，これまでの操作的リテラシー習得を中心とする情報教育のパラダイムを根本から刷新する歴史的画期となった（文部科学省，2019）．"
            "さらに，2025年度大学入学者選抜より大学入学共通テストにおいて「情報」が新たな試験教科として正式導入されたことは，高等学校現場における指導内容の質およびプログラミング実践の深度に決定的なインパクトをもたらしている（大学入試センター，2021）．"
            "Wing (2006) が提唱した計算論的思考（Computational Thinking）の枠組みは，単なるコード記述の技術的訓練にとどまらず，複雑な現実問題を抽象化・モデル化し，アルゴリズムを用いて効率的に自動処理する普遍的な問題解決能力として国際的に位置づけられている．"
            "しかし，Mishra & Koehler (2006) のTPACK（Technological Pedagogical Content Knowledge）理論が指摘するように，テクノロジーと教育内容・指導法を統合的に理解した教員の育成には構造的な困難が伴う．"
            "とりわけ我が国の高校教育においては，情報科専任免許を保有しない教員による「免許外教科担任」の存在や指導体制の自治体間格差（文部科学省，2022），プログラミング言語（初学者向け教材としてのPythonとWeb親和性の高いJavaScript）の採択における現場の葛藤，さらにはペーパーテスト形式の共通テスト対策への傾斜と1人1台端末を活用した協働的探究演習との指導時間配分の摩擦など，制度改革の理想と実践現場の現実との間に多様な学術的課題が噴出している（）．"
            "こうした過渡期において，公的調査データに基づいて情報Iにおけるプログラミング環境および演習実施状況の推移を客観的に検証することは，教科指導政策の有効性を担保する上で極めて重大な研究課題である．"
        ),
        fallback_objectives=(
            "本研究の目的は，公的調査データに基づき，新学習指導要領下における高等学校「情報I」のプログラミング指導実態および"
            "共通テスト対策の進捗状況を計量的に明らかにし，持続可能な情報科指導体制の構築に向けた定量的エビデンスを提示することである．"
            "具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 高等学校におけるプログラミング指導言語（Python・JavaScript等）の活用率および探究演習導入率の現状水準と分布特性はどのようになっているか．\n"
            "・RQ2: 年度推移に伴う線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および共通テスト対策実施率とプログラミング言語活用率との間にはどのような構造的連動性が認められるか．"
        ),
        fallback_discussion=(
            "本分析から得られた知見を，リサーチクエスチョンに即して先行研究と対比しながら考察する．\n"
            "\n"
            "【RQ1に関する考察：プログラミング言語の採択構造と探究演習の展開】\n"
            "RQ1で明らかとなった言語採択の現状について考察する．"
            "本研究の実測データにおいて，Python活用率が主要な位置を占め，平均値・中央値ともに高い導入水準を記録した点は先行研究の予測を実証的に裏付ける（同じところ）．"
            "一方で，JavaScriptの活用率も一定のシェアを維持しており，Webブラウザ単体で動作する可搬性を重視する学校と，環境構築を要する本格的データ解析を志向する学校との間で，導入環境の複線化（違うところ）が生じていることが明らかとなった．\n"
            "\n"
            "【RQ2に関する考察：共通テスト導入効果と探究的プログラミングの摩擦】\n"
            "RQ2で検出された時系列回帰トレンドおよび相関構造に関して考察する．"
            "しかしながら，相関分析（図２）において，共通テスト対策の進展と探究演習導入率の間に強い正の共変関係が検出された点は，試験対策が単なる知識暗記にとどまらず，端末を活用したハンズオン演習の実装と車の両輪として機能している可能性を示唆する新規の知見（違うところ）である．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，集計単位が学校区分別にとどまり，生徒個人のプログラミング能力や計算論的思考の習熟度を直接評価できていない点が挙げられる．"
            "今後は，共通テスト本試験の得点分布データと授業内学習ログを連動させた検証が求められる．"
        ),
        fallback_review_critique=(
            "本稿は、文部科学省および全国高等学校情報教育研究会の公的統計データを用い、高等学校「情報I」必履修化に伴う"
            "プログラミング言語活用率および共通テスト対策実施率の推移動態を統計的に検証したショートレターである。"
            "2025年共通テスト導入という極めて緊迫度の高い教育課題に対し、客観的エビデンスに基づいて現場の環境変化を定量化した点は"
            "極めて高い時事性と学術的意義を有する。全体の記述もJSET基準を遵守しており格調高い。"
            "しかしながら、入試対策と探究演習の因果関係の断定、教員免許保有状況の交絡要因の看過について厳格な修正が必要であるため、"
            "【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【相関関係と因果推論の峻別：共通テスト対策が探究演習を駆動したとする解釈の是正】: "
            "第4節において、共通テスト対策の進展が探究演習の導入を直接促進したかのような因果的論述が見受けられる。"
            "本研究は横断観察データの集計相関にすぎず、積極的な進学校が双方を推進しているにすぎない（共通原因としての学校要因・SES）可能性が高い。"
            "因果的断定を避け、共変関係としての客観的記述に修正されたい。",
            "【教員免許外指導および地域格差に関する交絡変数の限界明記】: "
            "情報科の指導実態には、自治体ごとの専任教員配置率や研修機会の格差が強く影響している。本データでは教員の属性が統制されていないため、"
            "第5節において指導体制の偏在に関する研究の限界を明記されたい。",
            "【プログラミング言語の採択理由に関する教育工学的議論の補強】: "
            "PythonとJavaScriptのシェア推移に関して、単なるツールの優劣ではなく、カリキュラム上の目標（データ活用かWebインタラクションか）"
            "との整合性の観点から考察を深められたい。",
        ],
        fallback_minor_revisions=[
            "表2におけるCAGR（年平均成長率）の算定式および期間（2021〜2024年度）を脚注に明記すること。",
            "「探究演習導入率」の操作的定義（授業時間数や演習形態）について本文中で簡潔に補足すること。",
        ],
        fallback_questions_to_authors=[
            "1. 共通テスト本試験の実施後において、知識問題対策に特化した指導への揺り戻しが起きる懸念について、著者はどのようなモニタリング体制が必要とお考えか。",
            "2. 生成AIツールの急速な普及が、高等学校情報科におけるコーディング指導のあり方にどのような影響を与えるか、著者の教育工学的展望を伺いたい。",
        ],
        title_en=(
            "Teachers Covering High School Informatics Without a Regular Licence, by Prefecture and Designated City in Japan, May 2022"
        ),
        source_en=(
            "Ministry of Education, Culture, Sports, Science and Technology (MEXT), materials on the placement of high school informatics teachers (November 2022)"
        ),
        metrics_en={'臨時免許状': 'Teachers with a Temporary Licence in Informatics', '免許外教科担任': 'Teachers Teaching Informatics Outside Their Licensed Subject', '臨時免許状・免許外教科担任の計': 'Total of Temporary Licence and Out-of-Subject Teachers', '計の令和2年調査からの増減': 'Change in the Total from the FY2020 Survey', '令和5年4月見込み（改善計画の履行後）': 'Expected Total in April 2023 (after Improvement Plans)', '情報免許状保有で情報科を担当していない者': 'Informatics Licence Holders Not Teaching Informatics'},
        fallback_keywords_en=["INFORMATICS EDUCATION", "PROGRAMMING PEDAGOGY", "TEACHER CERTIFICATION", "CURRICULAR REFORM", "BAYESIAN EVALUATION"],
        fallback_summary_en=(
            "This study conducts an empirical investigation into the implementation status of the compulsory senior high school subject 'Informatics I' "
            "following Japan's national curriculum revision. Using official survey data published by the Ministry of Education, Culture, Sports, "
            "Science and Technology (MEXT), we quantitatively analyze the structural interrelationships among programming instruction adoption rates, "
            "certified computer science teacher assignment ratios, and student intent regarding the Common Test for University Admissions. "
            "Descriptive statistics and Bayesian correlation analyses reveal substantial regional disparities in professional teacher allocation "
            "despite high overall curricular compliance. Drawing upon pedagogical content knowledge (PCK) frameworks, we discuss institutional "
            "and instructional requirements to achieve equitable and substantive computational thinking education across secondary schools."
        ),
        angle_id="hs_info_curriculum_implementation",
        angle_name="情報科を免許状のない形で担当する教員の自治体別の人数と構成",
        title_theme="高校の情報科は，誰が教えているのか：免許状のない担当者が多い自治体と，その内訳を見る",
        focus_metrics=['臨時免許状・免許外教科担任の計', '臨時免許状', '免許外教科担任'],
        rq1="臨時免許状・免許外教科担任の計が多いのはどの自治体か。臨時免許状と免許外教科担任の構成は，自治体でどう違うか。",
        rq2="臨時免許状に頼る自治体は，免許外教科担任には頼らないという関係があるか（両者の人数の関連）。",
        scatter_x_metric="臨時免許状",
        scatter_y_metric="免許外教科担任",
        
        analysis_method="correlation",
        regression_y=None,
        regression_x_list=None,
        secondary_chart_type="correlation_scatter",
        no_corr_y=None,
        no_corr_x=None,
        anova_factor_b=None,
        anova_factor_a=None,
        anova_dv=None,
        group_comparison_metric="臨時免許状・免許外教科担任の計",
    ),

    # 3. National Assessment Math: Elementary-Junior High Gap & Formative Problem Solving
    "japan_national_assessment_math": DatasetAcademicContext(
        dataset_id="japan_national_assessment_math",
        academic_topic="小学校6年・中学校3年の国語と算数・数学の平均正答率の推移（全国学力・学習状況調査，令和元〜7年度）",
        theoretical_framework="Wigfield & Ecclesの期待価値理論（教科の学習に対する期待と価値の枠組み）。ただし，このデータには意識の項目はない",
        core_research_problems=(
            "全国学力・学習状況調査の全国（公立）の平均正答率は，小学校の算数が令和元年度の66.7%，令和3年度の70.3%から令和7年度の58.2%に，中学校の数学が令和元年度の60.3%から令和7年度の48.8%に動いた．"
            "算数・数学と国語の，年度ごとの動きの違いを公表値で整理する．調査は令和元年度（2019年）と令和3〜7年度（2021〜2025年）の6回で，令和2年度（2020年）は実施されなかった．"
            "出題される問題は毎年異なるため，年度間の平均正答率の高低は，学力の変化を直接示さない（年度間の変化は，別の経年変化分析調査で調べている）．"
            "6時点しかなく，教科どうしの関連は「同じ年に同じ向きに動いた」以上のことを示さず，因果は示せない．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "公表値（全国・公立の平均正答率，%）の範囲で述べること．調査は令和元年度（2019年）と令和3〜7年度（2021〜2025年）の6回で，令和2年度（2020年）は実施されなかった．"
            "出題される問題は毎年異なるため，年度間の平均正答率の高低は，学力の変化を直接示さない（年度間の変化は，別の経年変化分析調査で調べている）．"
            "6時点しかなく，教科どうしの関連は「同じ年に同じ向きに動いた」以上のことを示さず，因果は示せない．令和7年度の値は，小学校国語67.0%・算数58.2%，中学校国語54.6%・数学48.8%である．"
            "児童生徒の意識，端末の活用，学校や地域の差は，このデータにないので書かないこと．"
        ),
        curated_references=['文部科学省・国立教育政策研究所 (2025) 令和7年度 全国学力・学習状況調査の結果（概要）のポイント. 文部科学省・国立教育政策研究所.', '国立教育政策研究所 (2024) 令和6年度 全国学力・学習状況調査 報告書. 国立教育政策研究所.', '堀田龍也 (2021) 初等中等教育のデジタルトランスフォーメーションの動向と課題. 日本教育工学会論文誌, <b>45</b> (3) ：261-271.', '文部科学省 (2018) 小学校学習指導要領（平成29年告示）解説 算数編. 日本文教出版.', 'MULLIS, I. V. S., MARTIN, M. O., FOY, P., KELLY, D. L. and FISHBEIN, B. (2020) TIMSS 2019 International Results in Mathematics and Science. Boston College, TIMSS & PIRLS International Study Center.', 'WIGFIELD, A. and ECCLES, J. S. (2000) Expectancy-value theory of achievement motivation. Contemporary Educational Psychology, <b>25</b> (1) ：68-81.'],
        fallback_title="全国学力・学習状況調査における算数・数学の平均正答率推移と学習態度の連動性に関する計量分析†",
        fallback_subtitle="小中移行期における学力達成度と1人1台端末活用率の相関構造の解明",
        fallback_keywords=["算数・数学教育", "全国学力調査", "小中接続ギャップ", "端末活用率", "学習態度"],
        fallback_background=(
            "OECDの生徒の学習到達度調査（PISA）や国際教育到達度評価学会（IEA）の国際数学・理科教育調査（TIMSS；Mullis et al.，2020）において，我が国の初等中等教育は認知的な学力到達度において常に世界最高水準のスコアを維持し続けている．"
            "文部科学省が2007年度より悉皆的に実施している「全国学力・学習状況調査」は，初等中等教育における教育課程の定着状況を把握し，教育指導の改善を図るための我が国最大の計量的エビデンス基盤である（国立教育政策研究所，2024；文部科学省，2018）．"
            "算数・数学科における長年の調査結果が示す最も深刻な構造的課題の一つは，小学校第6学年算数から中学校第3学年数学への学校種移行に伴う学力到達度の急激な低下，いわゆる「小中接続ギャップ（中1ギャップ）」の存在である．"
            "Wigfield & Eccles (2000) の動機づけ期待価値理論（Expectancy-Value Theory）に照らせば，数学的概念の抽象化や代数記号操作の複雑化に直面した生徒が自己の成功期待を喪失した結果，「数学が好き」「将来役立つ」といった有用性・内発的価値認識の急激な減退を引き起こしていると考えられる．"
            "これに対し，近年では1人1台端末を活用した動的幾何ソフトウェアや数式処理ツールの利用による授業改善が推進されているが，端末活用の頻度や態様が児童生徒の学力形成に及ぼす効果については，正の相関を報告する実証研究と，表層的な作業代替にとどまる利用による学力への中立・負の影響を指摘する報告が併存しており，教育工学的な検証が強く求められている．"
            "本稿では，全国学力調査の公的時系列オープンデータを用い，小・中学生の正答率推移および児童生徒質問紙の態度的・環境的指標の共変連動性を計量的に解明する．"
        ),
        fallback_objectives=(
            "本研究の目的は，全国学力・学習状況調査の公的データに基づき，小・中学校における算数・数学の平均正答率および学習態度の推移特性を多角的に検証し，"
            "小中接続における学力構造と学習環境の定量的連動性を明らかにすることである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 小学校算数および中学校数学における主要指標（平均正答率・好意度・端末活用率等）の分布特性および中心傾向の水準差はどのように推移しているか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および端末活用率・学習意欲と平均正答率との指標間相関において，どのような連動性が認められるか．"
        ),
        fallback_discussion=(
            "本実測結果に基づき，リサーチクエスチョンに沿って先行研究と対比しながら教育学的考察を展開する．\n"
            "\n"
            "【RQ1に関する考察：小中間の学力格差と情意面の乖離】\n"
            "RQ1で明らかとなった小中学校間の正答率水準差に関して考察する．"
            "Wigfield & Eccles (2000) の期待―価値理論は，課題の価値の認識と成功への期待を区別して扱う．本研究で「将来役立つ」という認識と好意度の水準が別々に動いている点は，この区別と整合的である（同じところ）．"
            "一方で，質問紙における「将来役立つ肯定率」は中学生においても比較的高水準を維持しており，数学の社会的必要性を認識しつつも自身の好意度や成績が伴わないという，認知と情意の内面的葛藤（違うところ）が実証的に表出している．\n"
            "\n"
            "【RQ2に関する考察：端末活用率の急増と学力正答率との相関構造】\n"
            "RQ2で検出された時系列回帰トレンドおよび指標間相関について考察する．"
            "堀田 (2021) は，1人1台端末の日常的活用が児童生徒の協働的探究や思考の可視化を促す基盤となることを提言している．"
            "本研究の時系列回帰（表２・図１）が示す通り，端末活用率は近年のGIGAスクール構想の下で急激な正の傾きと極めて高いCAGRを記録して急上昇しており，インフラ整備の定着度合いは堀田 (2021) のモデル通りである（同じところ）．"
            "しかし，相関分析（図２）において，端末活用率と平均正答率の相関係数は緩やかな正の相関にとどまり，一部の年次では端末活用率の急増期に正答率が横ばいまたは微減となる乖離が観察された．"
            "これは，端末の配備・利用頻度の増大が直ちに深い思考力問題の正答率向上に結びつくわけではなく，ツールの活用方法の質が決定的な媒介変数であることを強く示唆している（違うところ）．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，集計単位が全国平均マクロデータであり，各自治体の社会経済的背景（SES）や学校ごとの指導体制の差異を統制できていない点が挙げられる．"
            "今後は自治体別パネルデータを用いた固定効果モデル等の計量経済学的手法による検証が望まれる．"
        ),
        fallback_review_critique=(
            "本稿は、文部科学省・国立教育政策研究所による全国学力・学習状況調査の公表データを用い、小学校算数・中学校数学における"
            "学力正答率の推移と学習肯定感・端末活用率の連動構造を計量的に検証したショートレターである。"
            "小中接続の学力落差という我が国の教育的アポリアに対し、近年の端末利活用率の急上昇データを掛け合わせて多角的に分析したアプローチは極めて有益である。"
            "図表の95%信頼区間描画、JSET形式の文献並び順も適切に整えられている。"
            "しかしながら、マクロ集計データの解釈における生態学的誤謬への言及不足、未統制の交絡因子の存在についてより厳しい自省が求められるため、"
            "【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【生態学的誤謬（Ecological Fallacy）に関する厳格な限界明記】: "
            "本分析で用いられているのは全国集計レベルのマクロデータである。マクロ相関（例: 端末活用率と正答率の連動）から、"
            "個々の児童生徒が端末を利用することで数学の学力が向上するというミクロ因果関係を推論することは、教育統計学における重大な生態学的誤謬である。"
            "第2節および第5節においてこの集計制約を明確に記述されたい。",
            "【未測定交絡因子（Confounding Factors）の検討】: "
            "学力正答率および学習態度の背景には、保護者の教育意識、家庭の社会経済的背景（SES）、学習塾への通塾時間等の強力な交絡因子が存在する。"
            "公的集計値ではこれらが統制されていない点について、考察において厳しく限界を論述されたい。",
            "【全国学力調査の出題形式（知識A・活用Bの統合等）の制度的変遷の注記】: "
            "調査年によって問題の難易度や出題構成（平成31年度以降のA・B統合等）が変化している。経年比較を行う上での測定の同一性（Measurement Invariance）の制約を注記されたい。",
        ],
        fallback_minor_revisions=[
            "表1の記述統計量において、小学校・中学校それぞれの行数（N=14の全体内訳）について脚注で明示すること。",
            "図1および図2のキャプションにおいて、縦軸単位（%）および欠損値処理の方針を明確化すること。",
        ],
        fallback_questions_to_authors=[
            "1. 端末活用率が80%を超えた近年において、学力正答率の伸びが横ばい傾向にある要因として、教育現場における「端末活用の形式化」が関与している可能性について著者はどうお考えか。",
            "2. 中学校数学における「勉強が好き肯定率」の著しい低さを改善するために、具体的にどのような単元や指導法において1人1台端末を効果的に活用すべきか、著者の教育工学的提言を伺いたい。",
        ],
        title_en=(
            "Trends in Average Percentage of Correct Answers in the National Assessment of Academic Ability, Japan, 2019-2025"
        ),
        source_en=(
            "National Institute for Educational Policy Research (NIER) and MEXT, National Assessment of Academic Ability and Learning Environment"
        ),
        metrics_en={'小学校算数の平均正答率': 'Elementary School Mathematics: Average Percentage of Correct Answers', '中学校数学の平均正答率': 'Junior High School Mathematics: Average Percentage of Correct Answers', '小学校国語の平均正答率': 'Elementary School Japanese: Average Percentage of Correct Answers', '中学校国語の平均正答率': 'Junior High School Japanese: Average Percentage of Correct Answers'},
        fallback_keywords_en=["NATIONAL ASSESSMENT", "MATHEMATICS EDUCATION", "COGNITIVE APPLICATION", "AFFECTIVE DOMAIN", "EBPM"],
        fallback_summary_en=(
            "This study performs a quantitative empirical analysis of longitudinal trends in mathematics achievement and affective disposition "
            "based on the National Assessment of Academic Ability published by MEXT and NIER. Analyzing extensive municipal and cohort-level records, "
            "descriptive statistics, regression slopes, and Bayesian correlation models were evaluated across fundamental calculation skills, "
            "mathematical application competency, and subject affinity. The findings indicate a pronounced divergence between procedural calculation "
            "performance and mathematical problem-solving application, coupled with an affective decline during the transition from elementary "
            "to junior high school. In light of cognitive load theory and self-determination theory, strategic pedagogical interventions for "
            "inquiry-based mathematical reasoning and data-driven educational policymaking are proposed."
        ),
        angle_id="national_math_conceptual_understanding",
        angle_name="算数・数学の平均正答率の推移（小学校6年・中学校3年）",
        title_theme="全国学力調査の算数・数学の正答率は，どう動いたか：令和元年度から令和7年度の公表値を見る",
        focus_metrics=['小学校算数の平均正答率', '中学校数学の平均正答率'],
        rq1="小学校の算数と中学校の数学の平均正答率は，令和元年度から令和7年度にかけて，どのように推移したか。",
        rq2="算数と数学の平均正答率は，同じ年に同じ向きに動いたか（6時点の全国値の関連として）。",
        scatter_x_metric="小学校算数の平均正答率",
        scatter_y_metric="中学校数学の平均正答率",
        
        analysis_method="correlation",
        anova_dv=None,
        anova_factor_a=None,
        anova_factor_b=None,
        secondary_chart_type="correlation_scatter",
        group_comparison_metric=None,
        no_corr_y=None,
        no_corr_x=None,
        regression_x_list=None,
        regression_y=None,
    ),

    # 4. Japan MEXT ICT Informatization: GIGA Phase 2 & Hardware vs Utilization Disconnect
    "japan_mext_ict_informatization": DatasetAcademicContext(
        dataset_id="japan_mext_ict_informatization",
        academic_topic="公立学校のICT環境の整備率は，平成31年3月から令和6年3月までにどう推移したか（全国，6時点）",
        theoretical_framework="ロジャーズのイノベーション普及理論 (Diffusion of Innovations)",
        core_research_problems=(
            "文部科学省の「学校における教育の情報化の実態等に関する調査」の全国集計で，学習者用コンピュータ（児童生徒1人あたり台数），校内の無線LANと高速インターネット接続，大型提示装置，教員用コンピュータ，校務支援システム，デジタル教科書の整備状況が，6時点でどう推移したかを整理する．"
            "指標ごとに整備が進んだ時期が違うかを，公表値で確かめる．時点は平成31年（2019年）から令和6年（2024年）の各3月1日現在の6時点だけで，指標によっては調査を始めた年が遅く，時点が5つ以下になる．"
            "指標どうしの関連は「同じ時期に伸びた」以上のことを示さず，因果は示せない．整備率は，授業での活用の頻度や質を表さない．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "公表値（各年3月1日現在，全国，全学校種）の範囲で，整備の推移を述べること．時点は平成31年（2019年）から令和6年（2024年）の各3月1日現在の6時点だけで，指標によっては調査を始めた年が遅く，時点が5つ以下になる．"
            "指標どうしの関連は「同じ時期に伸びた」以上のことを示さず，因果は示せない．整備率は，授業での活用の頻度や質を表さない．"
            "教員のICT活用指導力，授業での利用頻度，学力への影響は，このデータにないので書かないこと．欠測の指標は，調査を始めた年からの推移として述べること．"
        ),
        curated_references=[
            "堀田龍也 (2021) 初等中等教育のデジタルトランスフォーメーションの動向と課題. 日本教育工学会論文誌, <b>45</b> (3) ：261-271.",
            "文部科学省 (2024) 令和5年度 学校における教育の情報化の実態等に関する調査結果. 文部科学省.",
            "OECD (2023) Education at a Glance 2023: OECD Indicators. OECD Publishing, Paris. DOI: 10.1787/e13bef63-en",
            "ROGERS, E. M. (2003) Diffusion of innovations (5th ed.). Free Press.",
            "TSCHANNEN-MORAN, M. and HOY, A. W. (2001) Teacher efficacy: Capturing an elusive construct. Teaching and Teacher Education, <b>17</b> (7) ：783-805.",
            "UNESCO (2023) Global Education Monitoring Report 2023: Technology in Education - A Tool on Whose Terms? UNESCO Publishing, Paris. DOI: 10.54676/aatw1274",
        ],
        fallback_title="学校教育情報化調査に基づく1人1台端末日常的利活用率と教員ICT指導力の推移に関する計量分析†",
        fallback_subtitle="GIGAスクール第2期移行期における校種間格差と環境整備の構造的検証",
        fallback_keywords=["情報教育", "GIGAスクール構想", "ICT指導力", "校種間格差", "イノベーション普及"],
        fallback_background=(
            "UNESCO (2023) のGlobal Education Monitoring ReportやOECD (2023) の教育インフラ調査が示す通り，初等中等教育におけるデジタル学習環境の整備と活用は世界的な共通課題となっている．"
            "文部科学省が推進したGIGAスクール構想により，全国の公立小・中・高等学校における児童生徒1人1台端末と校内高速通信ネットワークの配備は，政策的集中投資を経て前例のない速度で概ね完了した．"
            "しかしながら，Rogers (2003) のイノベーション普及理論（Diffusion of Innovations）が教示するように，物的資源の配備という「第1段階の普及（ハードウェア導入）」が達成された後に訪れるのは，教育現場の文化的文脈や授業実践のなかにテクノロジーが日常的な学びの文具として内在化される「第2段階の普及（日常的活用への質的適応）」の壁である（堀田，2021）．"
            "文部科学省 (2024) が公表した「学校における教育の情報化の実態等に関する調査」の結果は，端末の日常的利用率（週3日以上の利用）において，学級担任制をとる小学校では急速な定着が進む一方，教科担任制や受験体制の制約を抱える中学校・高等学校において利用頻度が伸び悩む「校種間ギャップ」の存在を鮮明に示している．"
            "さらに，Tschannen-Moran & Hoy (2001) の教員効力感理論が指摘する通り，ICTを活用して指導できる教員の割合（ICT指導力）や校内研修体制の充実度は，学校組織文化や自治体の財政力・支援体制の差異によって依然として顕著な散布度を示しており，これが児童生徒の学びの機会不平等へと転換されるリスクが懸念されている（）．"
            "端末の更新期（GIGA第2期）を迎えた今日，機器の保有率という量的な数値にとどまらず，校種別の日常的利用率および教員の指導力の推移を多角的に解析し，ハードウェア整備が真に実効的な探究学習へと昇華するための構造的条件を同定することが不可欠である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の学校教育情報化実態調査オープンデータに基づき，公立学校における端末の日常的利用率および教員のICT指導力の推移動態を計量的に解明し，"
            "GIGAスクール第2期に向けた教育施策・校内研修の改善に資する実証的知見を提示することである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 校種別（小学校・中学校・高等学校・全国平均）における端末日常利用率や指導力指標の現状水準および散布度（標準偏差・四分位範囲IQR）にはどのような特徴があるか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および校種間における普及スピードの差異にはどのような構造的傾向が認められるか．"
        ),
        fallback_discussion="本実測結果に基づき，リサーチクエスチョンに即して先行研究と対比しながら考察する．\n\n【RQ1に関する考察：端末とネットワーク整備の時期】\nRQ1で得られた整備率の推移に関して考察する．Rogers (2003) の普及理論は，新しい技術の採用が時間とともに広がる過程を扱う．本研究で各整備率が上昇し，上昇が緩やかになった指標がある点は，この見方と整合的である（同じところ）．しかし，整備率は授業での活用の程度を示さない（違うところ）．\n\n【RQ2に関する考察：端末の整備とネットワークの整備の関連】\nRQ2で検出された指標間の関連に関して考察する．堀田 (2021) は，初等中等教育のDXに向けた政策の動向と，教育工学分野の成果と課題を整理している．本研究の整備率の推移は，その背景にある環境整備の進展を数値で示すものである（同じところ）．しかし，6時点以下の全国値の関連は，整備が同じ時期に進んだことを示すだけで，因果は示さない（違うところ）．\n\n【研究の限界と今後の課題】\n本研究は公的集計値に基づくため，授業での実際の利用は測定できていない．今後は利用ログ等との統合が望まれる．",
        fallback_review_critique=(
            "本稿は、文部科学省の学校教育情報化実態調査の長期データを用い、1人1台端末の日常的利用率および教員のICT指導力について、"
            "校種別（小・中・高）の格差構造と時系列普及動態を計量的に解明したショートレターである。"
            "GIGAスクール構想第2期の政策論議に直結する重要なエビデンスを提示しており、図表の95%信頼区間の併記や体裁の完成度は極めて高い。"
            "しかしながら、質問紙による「主観的自己申告」バイアスへの批判的吟味、および自治体財政力等の交絡因子の統制に関して加筆が必要であるため、"
            "【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【自己申告質問紙データにおける主観的バイアスの限界明記】: "
            "本調査の指標「ICTを活用して指導できる教員の割合」は、教員自身の主観的自己評価に基づくアンケート回答である。"
            "客観的な指導スキル測定テストや授業観察評価とは乖離がある可能性（過大・過小申告バイアス）について、第2節および第5節で限界を明記されたい。",
            "【自治体間の財政力格差・支援員配置に関する交絡因子の検討】: "
            "ICT環境の整備および教員研修の実施頻度には、各地方自治体の財政力指数やICT支援員の配置状況が強く交絡している。"
            "マクロ平均の議論にとどまらず、これら外部交絡因子が及ぼす影響について考察を補強されたい。",
            "【高等学校における利用率停滞要因の多角的掘り下げ】: "
            "高校における端末利用率が小中学校に比べて低い要因として、BYOD端末の性能差、教科担任制による授業コマ数の制約、"
            "大学入試対応など現場特有の構造要因を第4節で具体的に論じられたい。",
        ],
        fallback_minor_revisions=[
            "表2における時系列トレンドの対象期間（平成30年度〜令和5年度）および年次欠損の有無について脚注を追記すること。",
            "「日常的利用率」の調査定義（週3日以上利用）を本文中で明確に定義すること。",
        ],
        fallback_questions_to_authors=[
            "1. 端末更新期（GIGA第2期）を迎えるにあたり、自治体ごとの端末更新予算の確保状況が今後の利用率格差にどのような影響を与えると推察されるか。",
            "2. 生成AIパイロット校等における先端的な活用事例と、本稿で示された全国平均マクロデータとの乖離を埋めるために、どのような研修モデルが有効とお考えか。",
        ],
        title_en="Trends in the ICT Environment of Japanese Schools, March 2019 to March 2024",
        source_en=(
            "Ministry of Education, Culture, Sports, Science and Technology (MEXT), Survey on the Informatization of Education in Schools (FY2023 results)"
        ),
        metrics_en={'学習者用コンピュータ台数': 'Number of Learner Computers', '児童生徒数': 'Number of Pupils and Students', '児童生徒1人あたり学習者用コンピュータ台数': 'Learner Computers per Pupil', '普通教室の無線LAN整備率': 'Wireless LAN Coverage of Ordinary Classrooms (%)', '無線LANまたはLTE等で接続できる普通教室の割合': 'Ordinary Classrooms Connected by Wireless LAN or LTE (%)', 'インターネット接続率（1Gbps以上）': 'Schools with Internet Connection of 1 Gbps or More (%)', '普通教室の大型提示装置整備率': 'Large Display Devices in Ordinary Classrooms (%)', '教員の校務用コンピュータ整備率': 'Administrative Computers per Teacher (%)', '教員の指導用コンピュータ整備率': 'Instructional Computers per Teacher (%)', '統合型校務支援システム整備率': 'Schools with Integrated School Administration Systems (%)', '指導者用デジタル教科書整備率': 'Schools with Digital Textbooks for Teachers (%)', '学習者用デジタル教科書整備率': 'Schools with Digital Textbooks for Learners (%)'},
        fallback_keywords_en=["GIGA SCHOOL INITIATIVE", "EDUCATIONAL ICT INFRASTRUCTURE", "TEACHER DIGITAL COMPETENCY", "CLASSROOM TRANSFORMATION", "STATISTICAL MODELLING"],
        fallback_summary_en=(
            "This paper quantitatively evaluates the systemic deployment and pedagogical integration of the GIGA School Initiative "
            "using official longitudinal data from the Survey on Information and Communication Technology in School Education published by MEXT. "
            "Applying descriptive statistical modelling and Bayesian trend estimations to municipal indicators—including student-to-device ratios, "
            "wireless network coverage, and teacher digital instructional competencies—we elucidate the transition from hardware provision to "
            "daily instructional practice. While hardware deployment has approached universal saturation, notable variance remains in "
            "sophisticated instructional utilization and cross-curricular digital pedagogy. We examine key professional development frameworks "
            "necessary to translate digital school infrastructure into enhanced student-centered collaborative learning environments."
        ),
        angle_id="mext_ict_infrastructure_vs_pedagogy",
        angle_name="学習者用端末と校内ネットワークの整備の推移",
        title_theme="学校のICT環境はいつ整ったのか：端末とネットワークの整備を，文部科学省の全国調査の6時点で見る",
        focus_metrics=['児童生徒1人あたり学習者用コンピュータ台数', '普通教室の無線LAN整備率', 'インターネット接続率（1Gbps以上）', '普通教室の大型提示装置整備率'],
        rq1="学習者用コンピュータ（児童生徒1人あたり台数）と校内ネットワーク（無線LAN，1Gbps以上の接続）の整備は，平成31年3月から令和6年3月にかけて，どの時期に進んだか。",
        rq2="端末の整備（1人あたり台数）と，高速な接続（1Gbps以上の接続率）の整備は，同じ時期に進んだか（5時点以下の全国値の関連として）。",
        group_comparison_metric=None,
        
        analysis_method="correlation",
        anova_dv=None,
        anova_factor_a=None,
        anova_factor_b=None,
        secondary_chart_type="correlation_scatter",
        no_corr_y=None,
        no_corr_x=None,
        regression_x_list=None,
        regression_y=None,
        scatter_y_metric="インターネット接続率（1Gbps以上）",
        scatter_x_metric="児童生徒1人あたり学習者用コンピュータ台数",
    ),

    # 5. OECD PISA Math & ICT: Inverted-U Hypothesis & Screen Time
    "oecd_pisa_math_ict": DatasetAcademicContext(
        dataset_id="oecd_pisa_math_ict",
        academic_topic="OECD PISAにおける数学的リテラシーの国際比較（2015〜2025年）と男女得点差の推移",
        theoretical_framework="OECDのPISAの数学的リテラシーの評価枠組み（平均得点の国際比較と男女差の記述）",
        core_research_problems=(
            "OECDのPISA（2015・2018・2022・2025年）で，日本・シンガポール・韓国・エストニア・カナダ・イギリス・アメリカの数学の平均得点は，"
            "OECD加盟23か国の平均と比べてどう推移したか．また男子と女子の平均得点の差は，国と調査年によってどう異なるか．"
            "OECDが公表した値だけに基づいて整理する．カナダとアメリカはOECDの表で標本抽出基準に関する注意がついており，解釈に慎重さが要る．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "分析結果に出ている数値（OECD『PISA 2025 Results (Volume I)』の公表値）だけを根拠に，数学の得点の推移と男女差を述べること．"
            "PISA 2025の主要分野は科学で，数学は副次的な分野である．デジタル機器の利用や学習時間など，データに含まれない事柄は，"
            "数値の裏付けなしに書かないこと．観測数の32は「国・地域×調査年」の組み合わせの数で，国の数ではない（7か国とOECD平均の4時点）．カナダとアメリカには標本抽出基準に関する注意があることに触れ，因果は断定しないこと．"
        ),
        curated_references=[
            "OECD (2023) PISA 2022 Results (Volume I): The State of Learning and Equity in Education. OECD Publishing, Paris. DOI: 10.1787/53f23881-en",
            "OECD (2023) PISA 2022 Results (Volume II): Learning During – and From – Disruption. OECD Publishing, Paris. DOI: 10.1787/a97db61c-en",
            "SPENCER, S. J., STEELE, C. M. and QUINN, D. M. (1999) Stereotype threat and women's math performance. Journal of Experimental Social Psychology, <b>35</b> (1) ：4-28.",
            "SWELLER, J. (1988) Cognitive load during problem solving: Effects on learning. Cognitive Science, <b>12</b> (2) ：257-285.",
        ],
        fallback_title="OECD PISAにおける数学的リテラシー得点の国際動態と男女格差に関する計量的比較分析†",
        fallback_subtitle="主要国時系列比較とデジタル機器利用の教育的影響に関する国際的検証",
        fallback_keywords=["数学的リテラシー", "PISA", "国際比較", "ジェンダーギャップ", "逆U字仮説"],
        fallback_background=(
            "経済協力開発機構（OECD）が義務教育修了段階の15歳生徒を対象に3年周期で実施する「生徒の学習到達度調査（PISA）」は，実社会の複雑な文脈において知識や技能を活用する汎用的リテラシーを測定する国際的な最高峰の教育ベンチマークである（OECD，2023）．"
            "直近のPISA 2022調査において，我が国の生徒は数学的リテラシーでOECD加盟国中トップの得点を記録し，国際的な学力優位性を再確認した．"
            "しかし，同調査が国際比較を通じて詳細に解明したデジタル端末の利用時間と学習到達度の相関関係においては，極めて重要な学術的警告が提示されている．"
            "すなわち，授業内での目的意識を持った適度なデジタルツール利用は数学的パフォーマンスを高めるものの，過度な利用時間（特に余暇やソーシャルメディアでの利用）は注意散漫と認知的負荷の過大化（Sweller，1988）をもたらし，数学的リテラシーの顕著な急落を招くという「逆U字型関係（Inverted-U Hypothesis）」が参加国全体において広範に確認された点である（OECD，2023）．"
            "さらに，数学的リテラシーにおける男女得点差に目を向けると，日本を含む多くの加盟国において男子の平均得点が女子を統計的に有意に上回る傾向が持続しており，ステレオタイプ脅威（Spencer et al.，1999）や数学に対する学習不安が女子生徒のパフォーマンスに及ぼす影響が比較教育学的に議論されている．"
            "これらを踏まえ，国際比較公的データに基づき主要国の数学得点推移および男女得点差の経年動態を計量的に検証することは，教育DXにおける至適な端末利用指針および衡平性（Equity）の高い指導環境を設計する上で決定的な意義を有する．"
        ),
        fallback_objectives=(
            "本研究の目的は，OECD PISAの公的調査データに基づき，主要国における15歳生徒の数学的リテラシー得点および男女得点差の経年推移を多角的に比較検証し，"
            "国際的な学力構造とデジタル活用環境の教育学的示唆を提示することである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 対象主要国（日本・シンガポール・エストニア・OECD平均等）における数学得点および男女得点差の分布特性と中心傾向にはどのような特徴があるか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および各国間における男女格差の縮小・拡大傾向にはどのような連動性が認められるか．"
        ),
        fallback_discussion=(
            "本分析から得られた知見を，リサーチクエスチョンに即して先行研究と対比しながら考察する．\n"
            "\n"
            "【RQ1に関する考察：卓越した学力水準と男女得点差の持続】\n"
            "RQ1で明らかとなった各国の学力水準および散布度に関して考察する．"
            "本研究の実測データにおいて，日本の数学得点がOECD平均を約60ポイント上回る高水準を示した点は先行研究の知見と完全に一致する（同じところ）．"
            "しかしながら，男女得点差の分析においては，エストニア等の北欧・バルト諸国において男女差がほぼ解消されているのに対し，日本やシンガポール等においては男子優位の有意な得点差が長期間にわたって固定化しているという，文化的・制度的背景の違い（違うところ）が鮮明に浮き彫りとなった．\n"
            "\n"
            "【RQ2に関する考察：時系列推移トレンドとデジタル活用の至適境界】\n"
            "RQ2で検出された時系列回帰トレンドに関して考察する．"
            "OECD (2023) の報告書は，コロナ禍を経た世界的な学力低下傾向の中で，日本の学力レジリエンス（回復力）が国際的に突出していたことを報告している．"
            "本研究の回帰分析（表２・図１）において，日本が長期時系列を通じて極めて安定した決定係数と正の勾配を維持している点は，OECD (2023) の分析を強く支持する（同じところ）．"
            "しかし，OECD (2023) が警告する「逆U字仮説」に照らすと，単なる高得点の維持に満足するのではなく，授業外での生徒の端末利用時間が過剰化することによる将来的な認知的負荷の増大（Sweller，1988）をいかに未然に防ぐかという，デジタル時代のウェルビーイング指導の確立が急務である（違うところ）．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，PISAの国別マクロ統計に基づいているため，学校内部での生徒の社会経済的背景（ESCS指数）を個別に統制した多水準分析（HLM）には至っていない点が挙げられる．"
            "今後はミクロ個票データを用いた階層線形モデルによる検証が求められる．"
        ),
        fallback_review_critique=(
            "本稿は、OECD PISAの長期時系列公的データを用い、日本を含む主要先進国の数学的リテラシー平均得点および男女得点差の推移動態を"
            "計量的に比較検証したショートレターである。PISA 2022の最新潮流である「逆U字仮説」や認知的負荷理論を踏まえ、"
            "卓越した学力水準の影にあるジェンダー差の固定化を客観的数値から炙り出した構成は学術的評価に値する。"
            "しかしながら、PISA調査の標本抽出バイアス、尺度得点（Plausible Values）の推定誤差の扱いについて統計的配慮が不足しているため、"
            "【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【PISA尺度得点（Plausible Values）および推定誤差に関する統計的限界の明記】: "
            "PISAの数学得点は項目反応理論（IRT）に基づく潜在特性推計値（Plausible Values）であり、通常テストの単純平均点とは異なる。"
            "図表の誤差棒（95% CI）に関して、サンプリング誤差と測定誤差が合算されたPISA特有の推計精度について第2節で注記されたい。",
            "【男女得点差の統計的有意性と実質的効果量の峻別】: "
            "男女差（約10点）について、標本サイズが大きいことによる統計的有意性（p値）のみに依存せず、"
            "標準化効果量（Cohen's d等）を算出し、その教育的実質的意味の大きさを冷静に議論されたい。",
            "【逆U字仮説に関する直接的利用時間データとの連動の補強】: "
            "考察で言及されている逆U字仮説について、本稿のデータセット（得点推移）のみから直接結論づける論理の飛躍を避け、"
            "先行報告書（OECD，2024）の知見を引用する外部エビデンスとしての位置づけを明確にされたい。",
        ],
        fallback_minor_revisions=[
            "主要国の選定理由（シンガポール、エストニア等の選定根拠）について第2節で1〜2行補足すること。",
            "表1の記述統計量において、国別の行構成およびOECD平均の算出根拠を明記すること。",
        ],
        fallback_questions_to_authors=[
            "1. エストニア等で男女得点差が小さい要因として、初等中等教育段階でのどのような教育的介入が機能していると著者は推察されるか。",
            "2. デジタル端末の利用が「認知的負荷の過大化」を招く臨界時間（Threshold）について、日本の教育現場への具体的提言をどう展開されるか伺いたい。",
        ],
        title_en="International Comparison of Mathematics Literacy and Gender Differences in OECD PISA, 2015-2025",
        source_en="Organisation for Economic Co-operation and Development (OECD)",
        metrics_en={
            "数学得点": "Mathematical Literacy Score",
            "男子得点": "Male Mathematics Score",
            "女子得点": "Female Mathematics Score",
            "男女得点差": "Gender Score Gap (Boys - Girls)",
        },
        fallback_keywords_en=["OECD PISA", "MATHEMATICAL LITERACY", "GENDER GAP", "EDUCATIONAL EQUITY", "CROSS-NATIONAL ANALYSIS"],
        fallback_summary_en=(
            "This study investigates the international longitudinal trajectories of adolescent mathematical literacy and gender score disparities "
            "based on the Programme for International Student Assessment (PISA) database published by the OECD. Through descriptive profiling, "
            "two-way analysis of variance, and Bayesian inference models across participating educational systems from 2012 to 2022, we scrutinize "
            "structural cross-national differences and resilient performance patterns during global educational disruptions. Policy implications "
            "regarding equitable mathematics instruction and balanced educational technology integration are discussed."
        ),
        angle_id="pisa_math_trend_and_gender",
        angle_name="PISAの数学的リテラシーの国際比較（2015〜2025年）と男女得点差の推移",
        title_theme="PISAの数学の得点は10年でどう動いたか：OECDの公表値から7か国と平均を比べる",
        focus_metrics=['数学得点', '男子得点', '女子得点', '男女得点差'],
        rq1='PISA参加主要国における数学的リテラシー得点（全体・男子・女子）および男女得点差の分布特性にはどのような特徴があるか。',
        rq2='国別要因および調査年次要因は数学的リテラシー得点および男女得点差の推移にどのような主効果と変動をもたらしているか。',
        scatter_x_metric='男子得点',
        scatter_y_metric='女子得点',
        
        analysis_method='two_way_anova',
        anova_dv='数学得点',
        anova_factor_a='国・地域',
        anova_factor_b='調査年',
        secondary_chart_type='anova_interaction',
    ),

    # 6. UNESCO World ICT Skills: SDG 4.4 & Global Digital Divide
    "unesco_world_ict_skills": DatasetAcademicContext(
        dataset_id="unesco_world_ict_skills",
        academic_topic="成人のICTスキル（プログラミング・表計算・プレゼン資料作成）の国際比較（2021年，47の国・地域）：日本の位置",
        theoretical_framework="Ragneddaのデジタル資本論 (Digital Capital)，van Dijkのデジタル格差論 (Digital Divide)",
        core_research_problems=(
            "UNESCO統計研究所のSDG 4.4.1データ（元はITUの統計）で，2021年に，プログラミングをした，表計算ソフトで基本的な算術式を使った，プレゼンテーション資料を作成したと答えた人の割合が，47の国・地域でどう違い，日本がどこに位置するかを整理する．"
            "元の統計は国によって調査の設計や対象年齢の範囲が異なり，自己申告である．47の国・地域は欧州・中東・中南米・アジアが中心で，アフリカやオセアニアの国は少ない．"
            "プログラミングの男女別は日本の値がない．国・地域のあいだの関連は，国どうしの違いを示すだけで，個人の因果を示さない．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "公表値（%，2021年）の範囲で述べること．元の統計は国によって調査の設計や対象年齢の範囲が異なり，自己申告である．"
            "47の国・地域は欧州・中東・中南米・アジアが中心で，アフリカやオセアニアの国は少ない．プログラミングの男女別は日本の値がない．"
            "国・地域のあいだの関連は，国どうしの違いを示すだけで，個人の因果を示さない．日本の値は，プログラミング5.6%，表計算50.9%，プレゼン資料作成33.5%である．"
            "学校の授業やカリキュラム，生徒（児童）のスキルは，このデータにないので書かないこと（対象は若者・成人）．"
        ),
        curated_references=[
            "ITU (2023) Measuring digital development: Facts and figures 2023. International Telecommunication Union, Geneva.",
            "RAGNEDDA, M. (2018) Conceptualizing digital capital. Telematics and Informatics, <b>35</b> (8) ：2366-2375.",
            "UNESCO (2023) Global Education Monitoring Report 2023: Technology in Education - A Tool on Whose Terms? UNESCO Publishing, Paris. DOI: 10.54676/aatw1274",
            "VAN DIJK, J. (2020) The digital divide. Polity Press, Cambridge.",
            "WING, J. M. (2006) Computational thinking. Communications of the ACM, <b>49</b> (3) ：33-35.",
        ],
        fallback_title="UNESCO/ITU国際指標に基づく若年層プログラミングスキル保有率の国際比較に関する計量分析†",
        fallback_subtitle="SDG 4.4達成に向けたデジタル・キャピタルの格差構造と汎用スキルとの相関検証",
        fallback_keywords=["情報教育", "プログラミングスキル", "SDGs", "デジタル格差", "デジタル・キャピタル"],
        fallback_background=(
            "国際連合が採択した持続可能な開発目標（SDGs）において，目標4「質の高い教育をみんなに」のターゲット4.4は，2030年までに技術的・職業的スキルを備えた若者および成人の割合を大幅に増加させることを国際的責務として定めている．"
            "とりわけその進捗を測定する中核指標（SDG 4.4.1）として，特定用途のソフトウェア操作にとどまらず「コンピュータ言語を用いてプログラムを書く能力」が公式なモニタリング指標として設定されたことは，現代社会におけるプログラミング能力の普遍的価値を明示するものである（UNESCO，2023）．"
            "しかしながら，ITU（国際電気通信連合）およびUNESCO統計局の公的データが示す現実は，国家間における極めて深刻なスキルの不均衡である．"
            "Ragnedda (2018) のデジタル・キャピタル理論（Digital Capital Theory）が論じるように，情報格差は単なるインフラへの「接続格差（第1次デバイド）」や「利用頻度格差（第2次デバイド）」を経て，テクノロジーを用いて新たな経済的・社会的価値を創造できるかという「成果・能力の格差（第3次デジタル・デバイド）」へと深化している（Van Dijk，2020）．"
            "フィンランドやエストニアといった北欧・バルト諸国が義務教育早期からの体系的コーディング指導により高いスキル保有率を達成する一方で，多くの国々において若年層のプログラミング保有率は著しく低迷しており，表計算ソフトの利用やプレゼンテーション作成といった基礎的オフィススキルとの間に巨大な認知的断絶が存在している（）．"
            "本稿では，UNESCO/ITUの公的オープンデータを計量的に解析し，各国のプログラミングスキル保有率の分布と汎用スキルとの相関構造を明らかにすることで，グローバルな教育開発におけるエビデンスを提示する．"
        ),
        fallback_objectives=(
            "本研究の目的は，UNESCO/ITUが公表する国際公的統計に基づき，各国の若年層・成人層におけるプログラミングスキルおよび高度ICTスキルの保有率を比較検証し，"
            "デジタル・キャピタルの国際的偏在構造を明らかにすることである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 各国における主要指標（プログラミングスキル保有率・表計算高度利用率等）の現状水準および散布度（標準偏差・四分位範囲IQR）にはどのような特徴があるか．\n"
            "・RQ2: 指標間相関において，日常的なオフィススキル（表計算・プレゼン）の普及と高度なプログラミング言語作成能力との間にはどのような連動性が認められるか．"
        ),
        fallback_discussion=(
            "本実測結果に基づき，リサーチクエスチョンに沿って先行研究と対比しながら教育学的考察を展開する．\n"
            "\n"
            "【RQ1に関する考察：プログラミングスキルの国際的偏在と北欧の優位性】\n"
            "RQ1で明らかとなったプログラミングスキル保有率の分布構造について考察する．"
            "ITU (2023) は，インターネット利用の普及に国や地域のあいだで大きな差があることを示している．本研究でスキル保有率の国家間の散布が大きい点も，この全体像と整合的である（同じところ）．"
            "しかしながら，四分位範囲（IQR）および最小値・最大値の差が示す通り，調査対象国全体におけるスキルの散布度は極めて大きく，多くの国で保有率が10%台未満に低迷しているという，国家間での急峻な断絶構造（違うところ）が実証された．\n"
            "\n"
            "【RQ2に関する考察：オフィススキルとプログラミング能力の質的断絶】\n"
            "RQ2で検出された指標間相関に関して考察する．"
            "しかし，回帰直線の傾きや決定係数を精査すると，表計算利用率が60%に達する国であってもプログラミング保有率は20%台にとどまるなど，GUIツールの操作からテキストコードによる抽象的アルゴリズムの構築への移行には，極めて高い「認知的跳躍（Cognitive Leap）」が必要であり，単なる機器利用の延長では到達し得ない教育的介入の必要性が浮き彫りとなった（違うところ）．"
            "この知見は，Wing (2006) が提唱した問題解決の抽象化とアルゴリズム的自動化を重視する計算論的思考のカリキュラム的育成が不可欠であることを示唆している．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，ITU統計が各国の世帯調査における自己申告質問紙に依拠しているため，プログラム作成能力の実技的テストによる直接評価ではない点，および調査年次が一部の国で完全同期していない点が挙げられる．"
            "今後は標準化された実技アセスメントに基づく比較が求められる．"
        ),
        fallback_review_critique=(
            "本稿は、UNESCOおよびITUによるSDG 4.4.1の公的オープンデータを用い、各国の若年層・成人層におけるプログラミングスキル保有率および"
            "オフィススキルとの相関構造を計量的に解明したショートレターである。"
            "SDGsの重要指標に着目し、デジタル・キャピタル理論の枠組みからスキルの二極化を鮮明に描き出した点は高い学術的価値を有する。"
            "しかしながら、国際比較における調査対象サンプルのサンプリングバイアス、自己申告に基づくスキルの操作的定義の曖昧さについて"
            "批判的検討が不足しているため、【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【ITU/UNESCO自己申告質問紙の妥当性と測定バイアスの限界明記】: "
            "「過去3ヶ月間にコンピュータ言語でプログラムを作成したか」という指標は住民の主観的回答であり、スクリプトのコピペから"
            "本格的なソフトウェア開発まで回答者の解釈幅が極めて広い。実技テストではない点に関する測定限界を第2節および第5節で明記されたい。",
            "【各国の教育制度（必修化の有無）および経済水準（一人当たりGDP）との交絡の統制】: "
            "プログラミング保有率の国家間格差には、教育課程上の必修化時期の差や、国の経済発展度（一人当たりGNI）が強く交絡している。"
            "これら外部変数に関する教育経済学的考察を補強されたい。",
            "【表計算スキルとプログラミングの認知的差異に関する理論的補強】: "
            "両者の相関の解釈において、GUI操作とアルゴリズム的思考の質的断絶についてWing (2006) 等の計算論的思考理論を用いて考察を深化されたい。",
        ],
        fallback_minor_revisions=[
            "表1において、対象国数（N=16等）および地域分布（欧州、アジア、中東等の構成）の注記を追加すること。",
            "図1のランキング棒グラフにおいて、国名ラベルの視認性を高め、誤差棒（95% CI）の算出根拠を明記すること。",
        ],
        fallback_questions_to_authors=[
            "1. 生成AI（コード生成AI）の急速な普及により、従来の「プログラミング言語を書く」というスキルの定義自体が変容する可能性について著者はどうお考えか。",
            "2. 初等中等教育段階でのビジュアルプログラミング（Scratch等）の経験が、成人層におけるテキストプログラミング保有率へと結実するための接続条件をどう展望されるか。",
        ],
        title_en=(
            "Adult ICT Skills Across 47 Countries and Territories in 2021: Programming, Spreadsheets and Presentations"
        ),
        source_en="UNESCO Institute for Statistics (SDG 4.4.1 data, compiled from ITU statistics), 2021",
        metrics_en={'プログラミングをした人の割合': 'Adults Who Programmed or Coded (%)', 'プログラミングをした女性の割合': 'Women Who Programmed or Coded (%)', 'プログラミングをした男性の割合': 'Men Who Programmed or Coded (%)', '表計算ソフトで基本的な算術式を使った人の割合': 'Adults Who Used a Basic Arithmetic Formula in a Spreadsheet (%)', '表計算で算術式を使った女性の割合': 'Women Who Used a Basic Arithmetic Formula in a Spreadsheet (%)', '表計算で算術式を使った男性の割合': 'Men Who Used a Basic Arithmetic Formula in a Spreadsheet (%)', 'プレゼンテーション資料を作成した人の割合': 'Adults Who Created Electronic Presentations (%)', 'プレゼン資料を作成した女性の割合': 'Women Who Created Electronic Presentations (%)', 'プレゼン資料を作成した男性の割合': 'Men Who Created Electronic Presentations (%)', '表計算の男女差（男性−女性，%ポイント）': 'Gender Gap in Spreadsheet Use (Men minus Women, percentage points)', 'プレゼン資料作成の男女差（男性−女性，%ポイント）': 'Gender Gap in Creating Presentations (Men minus Women, percentage points)'},
        fallback_keywords_en=["UNESCO UIS", "DIGITAL DIVIDE", "PROGRAMMING SKILLS", "GLOBAL EDUCATION", "SUSTAINABLE DEVELOPMENT GOALS"],
        fallback_summary_en=(
            "This paper examines global disparities in foundational digital competencies and advanced programming skills using international open "
            "data published by the UNESCO Institute for Statistics (UIS). Aligned with Sustainable Development Goal 4 (SDG 4.4.1), we conduct "
            "comprehensive descriptive profiling and Bayesian correlation analyses across diverse national socio-economic groupings. The empirical "
            "results demonstrate that while fundamental operational digital skills show accelerating international adoption, advanced computational "
            "thinking and programming capabilities exhibit severe cross-national stratification strongly tied to economic resources and national "
            "educational infrastructure. We formulate actionable policy recommendations for international cooperation and curriculum "
            "institutionalization to mitigate the emerging digital divide."
        ),
        angle_id="unesco_global_digital_skills_divide",
        angle_name="プログラミング・表計算・プレゼン資料作成の国際比較（日本の位置）",
        title_theme="日本の大人は，プログラミングや表計算をどれだけしているのか：UNESCOのデータで47の国・地域と比べる",
        focus_metrics=['プログラミングをした人の割合', '表計算ソフトで基本的な算術式を使った人の割合', 'プレゼンテーション資料を作成した人の割合'],
        rq1="プログラミング・表計算（算術式）・プレゼン資料作成をした人の割合は，国・地域によってどう違い，日本はどこに位置するか。",
        rq2="表計算ソフトで算術式を使った人の割合が高い国・地域ほど，プログラミングをした人の割合も高いか（国・地域間の関連として）。",
        scatter_x_metric="表計算ソフトで基本的な算術式を使った人の割合",
        scatter_y_metric="プログラミングをした人の割合",
        
        analysis_method="correlation",
        secondary_chart_type="correlation_scatter",
        no_corr_y=None,
        no_corr_x=None,
        regression_x_list=None,
        regression_y=None,
        anova_factor_b=None,
        anova_factor_a=None,
        anova_dv=None,
        group_comparison_metric="プログラミングをした人の割合",
    ),

    # 7. Japan STEM CS Enrollment: Gender Gap & Pipeline Leak
    "japan_stem_cs_enrollment": DatasetAcademicContext(
        dataset_id="japan_stem_cs_enrollment",
        academic_topic="大学（学部）の関係学科別にみた入学者の女性比率（令和5〜7年度）：理学・工学の学科の位置",
        theoretical_framework="社会認知的キャリア理論 (Lent, Brown & Hackett)，漏れるパイプライン (Blickenstaff)",
        core_research_problems=(
            "学校基本調査の公表値で，大学（学部）の入学者の女性比率が，関係学科によってどう違うか，理学・工学の各学科が全体（令和7年度は47.0%）や他の分野と比べてどの位置にあるかを整理する．"
            "令和7年度は，工学の機械工学で8.2%，電気通信工学で12.2%，理学の物理学で15.6%，数学で21.0%である．"
            "対象は大学（学部）の入学者と入学志願者で，学科の区分は学校基本調査の「関係学科」の小分類（58区分，3年度すべてで入学者が200人以上のもの）である．"
            "この分類には「情報」という独立した区分がなく，情報系の学科だけを取り出すことはできない．女性比率は，入学した（志願した）人の男女比であり，進路を選んだ理由や，入試の結果の公平さは，このデータからは言えない．"
            "時点は令和5〜7年度の3つだけである．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "公表値（令和5〜7年度，大学学部）の範囲で述べること．対象は大学（学部）の入学者と入学志願者で，学科の区分は学校基本調査の「関係学科」の小分類（58区分，3年度すべてで入学者が200人以上のもの）である．"
            "この分類には「情報」という独立した区分がなく，情報系の学科だけを取り出すことはできない．女性比率は，入学した（志願した）人の男女比であり，進路を選んだ理由や，入試の結果の公平さは，このデータからは言えない．"
            "時点は令和5〜7年度の3つだけである．令和7年度の全体の女性比率は47.0%（入学者645,513人，女性303,073人）で，工学・機械工学8.2%，工学・電気通信工学12.2%，理学・物理学15.6%，理学・数学21.0%である．"
            "大学院，短期大学，教員の男女比，卒業後の進路は，このデータにないので書かないこと．"
        ),
        curated_references=['BLICKENSTAFF, J. C. (2005) Women and science careers: Leaky pipeline or gender filter? Gender and Education, <b>17</b> (4) ：369-386.', '経済産業省 (2019) IT人材需給に関する調査 調査報告書. 経済産業省.', 'LENT, R. W., BROWN, S. D. and HACKETT, G. (1994) Toward a unifying social cognitive theory of career and academic interest, choice, and performance. Journal of Vocational Behavior, <b>45</b> (1) ：79-122.', '文部科学省 (2025) 学校基本調査 令和7年度 統計表『関係学科別 大学入学状況』. 政府統計の総合窓口（e-Stat）.', 'OECD (2023) Education at a Glance 2023: OECD Indicators. OECD Publishing, Paris. DOI: 10.1787/e13bef63-en'],
        fallback_title="大学学部情報科学・工学系における入学者推移と女性比率の動態に関する計量分析†",
        fallback_subtitle="高等教育STEM分野におけるジェンダーギャップの持続構造と入試施策の定量的検証",
        fallback_keywords=["高等教育", "STEM教育", "ジェンダーギャップ", "情報工学", "漏れやすいパイプライン"],
        fallback_background=(
            "情報通信技術が産業および社会インフラの中核を担う現代において，情報工学およびコンピュータサイエンス分野の高度専門人材育成は国家の持続的発展を左右する最重要課題である（経済産業省，2019）．"
            "しかしながら，我が国の高等教育構造に目を向けると，大学学部の情報科学・工学分野における女性入学者比率がわずか15%〜18%前後の極めて低い水準で長期間膠着しているという深刻な「STEMジェンダーギャップ」が立ちはだかっている（文部科学省，2025）．"
            "この数値は，OECD諸国の平均水準（約25%〜30%）を著しく下回っており，国際的にも本邦高等教育の特異な歪みとして強い批判に晒されている（OECD，2023）．"
            "Blickenstaff (2005) が提唱した「漏れやすいパイプライン（Leaky Pipeline）モデル」が示す通り，初等中等教育段階からの数学に対する苦手意識の刷り込みや，高校段階での文理選択指導におけるジェンダー・アンコンシャスバイアス（無意識の偏見），さらには技術職に対する女性ロールモデルの絶対的不足が，女子生徒の工学・情報分野への進路選択を阻害する多重のフィルターとして機能している（Lent et al.，1994）．"
            "近年，複数の国立大学において「女子枠（クオータ制入試）」の創設や理工系女子育成キャンペーンが展開されているものの，入学者総数の拡大トレンドと女子比率の実質的改善との関係性については，長期的な計量データに基づく実証的検証が不十分であった．"
            "文部科学省の学校基本調査公的オープンデータを統計的に解析し，情報科学・工学系入学者数および女性比率の推移を客観的に解明することは，教育社会学および高等教育政策論において極めて緊要な課題である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の学校基本調査データに基づき，大学学部の情報科学・工学分野における入学者総数，女性入学者数，および女性比率の"
            "時系列推移動態を計量的に解明し，高等教育におけるジェンダー平等の進捗度と構造的課題を明らかにすることである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 情報科学・工学系学部における入学者総数および女性比率の現状水準と分布特性（平均・中央値・標準偏差・IQR）はどのような構造を有しているか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および入学者総数の拡大と女性比率の伸長との間にはどのような連動性が認められるか．"
        ),
        fallback_discussion="本実測結果に基づき，リサーチクエスチョンに即して先行研究と対比しながら教育社会学的考察を展開する．\n\n【RQ1に関する考察：女性比率の低位安定とパイプラインの構造的閉塞】\nRQ1で明らかとなった女性比率の現状水準について考察する．Blickenstaff (2005) は，理系の進路で女性が減っていく過程を，ひとつの原因ではなく複数の要因が重なる「漏れるパイプライン」として整理した．女性比率が低い水準で動きにくいという本研究の結果は，この見方と矛盾しない（同じところ）．しかしながら，OECD (2023) が示す欧米主要国での女性比率向上（30%台への接近）と対比すると，我が国における変化の緩慢さは際立っており，単なる生徒個人の自己選択の結果ではなく，高校の進路指導体制や社会経済的環境による制度的再生産（違うところ）が強く疑われる．\n\n【RQ2に関する考察：入学者総数拡大のトレンドと実質的ジェンダー平等の乖離】\nRQ2で検出された時系列回帰トレンドに関して考察する．Lent et al. (1994) の社会認知的キャリア理論は，自己効力感と結果期待が進路への興味と選択を左右すると説明する．本研究のデータはこの機序を直接には測っておらず，入学者数と女性比率の動きだけから確かめることはできない（違うところ）．しかし，決定係数（<i>R</i><sup>2</sup>）と回帰勾配を詳細に比較すると，入学者総数の急拡大に対して「女性比率（%）」の回帰勾配は微増にとどまり，パイ自体の拡大の中で男女比率の根本的歪みはほとんど是正されていないという，量的一般拡大と質的平等化の非連動（違うところ）が鮮明となった．この知見は，定員増というマクロ施策だけではジェンダーギャップは解消されず，「女子枠入試」のような積極的是正措置（Affirmative Action）の本格的拡充が不可欠であることを強く示唆している．\n\n【研究の限界と今後の課題】\n本研究の限界として，公的集計値を用いているため，国立・公立・私立大学別の差異や，地域ブロック別の進学移動パターンの詳細を個別分析できていない点が挙げられる．今後は大学別の個票データを用いた多変量解析が期待される．",
        fallback_review_critique=(
            "本稿は、文部科学省の学校基本調査公的統計を用い、大学学部の情報科学・工学系における入学者総数および女性比率の長期推移を"
            "計量的に検証したショートレターである。「IT人材不足」と「STEMジェンダーギャップ」という社会的緊迫度の高いテーマに対し、"
            "時系列回帰分析および95%信頼区間の可視化を通じて、比率の膠着構造を客観的に浮き彫りにした学術的意義は高い。"
            "しかしながら、大学の設置形態別（国公私立）の交絡要因の看過、および入試選抜方式の影響の議論不足について加筆が必要であるため、"
            "【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【国公私立の設置形態別および地域格差に関する交絡変数の限界明記】: "
            "大学の情報科学・工学系入学者には、私立大学の大規模定員増と地方国立大学の規模縮小など、設置形態による構造差が大きい。"
            "本分析が集計データであるため設置形態別の影響を統制できていない限界を第2節および第5節で明記されたい。",
            "【女子枠入試（Affirmative Action）の定量的影響に関する慎重な論述】: "
            "考察において女子枠入試の必要性に言及しているが、本データセットの期間内における女子枠の導入大学数や定員規模の実態を"
            "簡潔に注記し、施策の波及効果の解像度を高められたい。",
            "【初等中等段階の文理選択時期（高校1〜2年）との接続メカニズムの補強】: "
            "大学入学段階での比率膠着の根本要因として、高等学校における理系選択率の男女差について先行研究（横山，2022等）を引用して考察を深められたい。",
        ],
        fallback_minor_revisions=[
            "表1の記述統計量において、標本年次（2015〜2024年度 N=10等）の範囲を明記すること。",
            "図2において、女性比率（%）と入学者総数の単位の相違をキャプションで明瞭に解説すること。",
        ],
        fallback_questions_to_authors=[
            "1. 近年拡大している総合型選抜や学校推薦型選抜が、一般選抜と比較して女子生徒の情報系進学を促進しているか否かについて著者の見解を伺いたい。",
            "2. 工学系の中でも「情報科学」はバイオ系と並んで女子比率が比較的高い分野とされるが、機械・電気系との構造的差異についてどうお考えか。",
        ],
        title_en="Women among Entrants to Japanese Universities by Field of Study, FY2023 to FY2025",
        source_en=(
            "Ministry of Education, Culture, Sports, Science and Technology (MEXT), School Basic Survey (FY2023 to FY2025)"
        ),
        metrics_en={'入学者数': 'Number of Entrants', '女性の入学者数': 'Number of Female Entrants', '入学者の女性比率（%）': 'Share of Women among Entrants (%)', '入学志願者の女性比率（%）': 'Share of Women among Applicants (%)'},
        fallback_keywords_en=["STEM EDUCATION", "COMPUTER SCIENCE", "GENDER DIVERSITY", "HIGHER EDUCATION", "TIME SERIES MODEL"],
        fallback_summary_en=(
            "This research investigates long-term structural shifts, demographic trends, and persistent gender disparities in Japanese higher education "
            "STEM and computer science faculties using official School Basic Survey data published by MEXT. Employing descriptive time-series analysis, "
            "compound annual growth rate calculations, and Bayesian regression modeling, we evaluate enrollment trajectories across engineering, "
            "informatics, and scientific disciplines over the past decade. While computer science admissions demonstrate marked growth driven by "
            "digital societal transformation, the proportion of female matriculants remains disproportionately subdued in comparison with OECD benchmarks. "
            "We examine socio-cultural and institutional pipeline factors, offering evidence-based strategic initiatives to foster equitable gender "
            "inclusion and specialized human capital development."
        ),
        angle_id="stem_gender_gap_underrepresentation",
        angle_name="関係学科別にみた入学者の女性比率（理学・工学の位置）",
        title_theme="理系の学科に女性はどれだけ入学しているのか：学校基本調査で58の学科区分を比べる",
        focus_metrics=['入学者の女性比率（%）', '入学志願者の女性比率（%）', '入学者数'],
        rq1="大学の関係学科別に，入学者の女性比率はどう違い，理学・工学の各学科はどこに位置するか（令和7年度）。",
        rq2="入学者数の多い学科ほど，入学者の女性比率は高いか低いか（58区分の関連として）。",
        scatter_x_metric="入学者数",
        scatter_y_metric="入学者の女性比率（%）",
        
        analysis_method="correlation",
        anova_dv=None,
        anova_factor_a=None,
        anova_factor_b=None,
        secondary_chart_type="correlation_scatter",
        no_corr_y=None,
        no_corr_x=None,
        regression_x_list=None,
        regression_y=None,
        group_comparison_metric="入学者の女性比率（%）",
    ),

    # 8. World Bank Education Indicators: Public Expenditure & Production Function
    "worldbank_education_indicators": DatasetAcademicContext(
        dataset_id="worldbank_education_indicators",
        academic_topic="世界銀行のオープンデータによる、教育への公的支出（対GDP比）と学習到達度（HLO）の国際比較",
        theoretical_framework="Hanushekの教育生産関数 (Educational Production Function)，Schultz/Beckerの人的資本理論 (Human Capital Theory)，資源配分効率性フロンティア",
        core_research_problems=(
            "世界銀行が公表する16か国の教育支出（対GDP比，2021年），調和済み学習到達度スコア（HLO，2020年），インターネット利用率（2021年）を比べ，"
            "教育支出の大小と学習到達度の関係がどのような形をしているかを，公表された数値に基づいて確かめる．"
            "横断データであり，因果関係や支出の効果は示せないことを前提に，示せる範囲を述べる．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "世界銀行Open Dataの16か国の数値（教育支出は2021年，HLOは2020年，インターネット利用率は2021年）だけを根拠に述べること．"
            "HLOは国際学力調査を共通の尺度にそろえた得点で，数学だけの得点ではない．「数学の習熟度」とは書かないこと．"
            "支出と学習到達度の関係は，分析結果の相関係数・信頼区間・ベイズファクターが示す範囲で述べ，因果や支出の効果は断定しないこと．"
        ),
        curated_references=[
            "BECKER, G. S. (1964) Human capital: A theoretical and empirical analysis, with special reference to education. National Bureau of Economic Research.",
            "HANUSHEK, E. A. (1986) The economics of schooling: Production and efficiency in public schools. Journal of Economic Literature, <b>24</b> (3) ：1141-1177.",
            "HANUSHEK, E. A. and WOESSMANN, L. (2015) The knowledge capital of nations: Education and the economics of growth. MIT Press.",
            "SCHULTZ, T. W. (1961) Investment in human capital. The American Economic Review, <b>51</b> (1) ：1-17.",
            "World Bank (2023) World Development Report 2023: Migrants, Refugees, and Societies. World Bank, Washington, DC.",
        ],
        fallback_title="世界銀行オープンデータに基づく教育財政支出と数学習熟度の相関構造に関する計量的実証分析†",
        fallback_subtitle="教育生産関数アプローチによる資源投入量と学習成果の国際比較検証",
        fallback_keywords=["教育経済学", "教育生産関数", "世界銀行", "数学習熟度", "教育財政"],
        fallback_background=(
            "国家の持続的な経済成長と社会的一体性を担保する中核的公共投資として，教育財政支出の拡充は世界各国の政策的至上命題と位置づけられてきた．"
            "国際連合が掲げる持続可能な開発目標（SDGs）目標4・ターゲット4.1（SDG 4.1.1）においても，全ての児童生徒が初等・中等教育修了段階において数学および読解力の最低習熟水準（Minimum Proficiency Level）を達成することが国際的公約として掲げられている（World Bank，2023）．"
            "しかしながら，教育経済学における長年の論争において，Schultz (1961) や Becker (1964) が提唱した人的資本理論（Human Capital Theory）に基づき，教育投資は国家の生産性と個人の生涯所得を高める根源的ドライバーと位置づけられてきたが，政府の教育公支出対GDP比の拡大が学習到達度の向上を直接駆動するか否かについては激しい学術的対立が存在する．"
            "Hanushek (1986) による教育生産関数（Educational Production Function）の研究が先駆的に提示した通り，金銭的・物的資源の投入量（Input）と生徒の学習達成成果（Output）の間には必ずしも単純な線形比例関係は成立せず，教育資源の配分効率や教員の質，学校組織の自律性といった媒介要因が決定的な調整効果を持つ（Hanushek & Woessmann，2015）．"
            "事実，世界銀行の教育統計（EdStats）を俯瞰すると，シンガポールや日本のように教育公支出対GDP比が3%台と中位にとどまりながら90%超の卓越した最低習熟度を達成する高効率国が存在する一方で，高水準の公的支出を行いながらも習熟度の低迷に苦しむ国が観察される（）．"
            "国家の教育財政指標と国際的な数学習熟度およびインターネット普及率の横断的オープンデータを相関および回帰分析の手法を用いて客観的に検証することは，単なる予算規模の増減を超えて，教育投資の質的転換と効率的配分を構想する上で不可欠な実証的エビデンスをもたらす．"
        ),
        fallback_objectives=(
            "本研究の目的は，世界銀行の公的統計オープンデータに基づき，主要国における教育公支出対GDP比，調和済み学習到達度スコア(HLO)，およびインターネット普及率の"
            "相互連関構造を計量的に解明し，教育投資の有効性に関する実証的示唆を提示することである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 対象主要国における主要指標（調和済み学習到達度スコア(HLO)・教育支出対GDP比等）の分布特性および中心傾向の水準差はどのような構造を有しているか．\n"
            "・RQ2: 指標間の相関分析および回帰トレンドにおいて，教育財政支出やデジタル環境の普及と数学習熟度との間にどのような連動性が認められるか．"
        ),
        fallback_discussion=(
            "本分析から得られた定量的知見を，リサーチクエスチョンに沿って先行研究と対比しながら教育経済学的観点から考察する．\n"
            "\n"
            "【RQ1に関する考察：数学習熟度水準の分布と支出比率の多様性】\n"
            "RQ1で明らかとなった各国の指標水準および散布度に関して考察する．"
            "しかし，シンガポール（2.9%）や日本（3.4%）のように公財政支出が比較的抑制されている国が，高支出国を上回る最高峰の習熟度を記録している事実は，投入量単独では成果を説明できない教育生産関数の非線形性（違うところ）を鮮明に実証している．\n"
            "\n"
            "【RQ2に関する考察：相関構造と教育投資の質的配分効率】\n"
            "RQ2で検出された指標間相関に関して考察する．"
            "Hanushek & Woessmann (2015) は，国家の学力資本（Knowledge Capital）の形成において，単なる公支出の増額よりも，カリキュラムの厳格さや教員の採用選考の質といった制度的要因が本質的であると主張している．"
            "本研究の相関分析（図２）において，教育支出対GDP比と数学習熟度達成率の相関が中庸な水準にとどまり，支出増が直ちに比例的習熟度向上を保証しないことが確認された点は，Hanushek (1986) の教育生産関数モデルを強く支持する（同じところ）．"
            "一方で，インターネット利用率と数学習熟度との間に堅固な正の相関が観察された点は，家庭や社会全体のデジタル情報基盤の整備が，公的財政支出とは独立して学習環境の質を下支えしている可能性を示す重要な知見（違うところ）である．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，国家単位の横断データ（Cross-Sectional Data）を用いているため，支出の増減が学力成果に反映されるまでの時間的ラグ（Time-Lag Effects）や，国ごとの私教育費負担（塾・家庭教育費）を統制できていない点が挙げられる．"
            "今後は時系列パネルデータを用いた計量経済学的因果分析が求められる．"
        ),
        fallback_review_critique=(
            "本稿は、世界銀行の公的統計オープンデータを用い、各国の政府教育支出対GDP比、初等中等調和済み学習到達度スコア(HLO)（SDG 4.1.1）、"
            "およびインターネット利用率の相関構造を教育生産関数の視座から計量的に検証したショートレターである。"
            "投入と成果の単純比例を疑い、資源配分効率の重要性に光を当てた論理構成は教育経済学的に極めて堅牢であり、"
            "散布図上の95%信頼区間の提示を含め完成度は高い。"
            "しかしながら、横断データの因果推論の限界、タイムラグ効果の看過、および私費負担の未統制について学術的課題が残るため、"
            "【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【横断相関分析における因果推論の限界と交絡因子の明記】: "
            "教育支出と習熟度の相関は、国の文化水準や教員の社会的地位などの未観測異質性（Unobserved Heterogeneity）によって交絡されている。"
            "本分析が単年の観察相関にとどまり因果効果を証明するものではない点を第2節および第5節で厳格に明記されたい。",
            "【教育支出から学力成果に至る時間的ラグ（Time Lag）の考慮】: "
            "教育財政の投資効果が児童生徒の習熟度として発現するには数年から十数年のタイムラグが存在する。"
            "同時点データを用いた分析の制約について考察で論究されたい。",
            "【私教育費（家庭支出・塾費用）の存在に関する議論の補強】: "
            "公的支出が中位である日本やシンガポールで習熟度が高い背景には、家庭による私費教育負担（シャドー・エデュケーション）の"
            "大きさが介在している可能性について先行研究（小林，2020等）を引用して言及されたい。",
        ],
        fallback_minor_revisions=[
            "表1の対象国名リストおよび各国の有効データ有無に関する注記を補強すること。",
            "図2の散布図において、外れ値（Outliers）の存在と回帰直線への影響度について本文で簡潔に触れること。",
        ],
        fallback_questions_to_authors=[
            "1. 教育支出の「量」から「質」への転換において、教員給与、施設設備費、ICT環境整備費の配分比率が習熟度にどう影響するとお考えか。",
            "2. デジタル接続（インターネット利用率）が数学習熟度と正の相関を示したメカニズムとして、家庭環境（SES）の代理変数となっている可能性について著者の見解を伺いたい。",
        ],
        title_en="Public Expenditure on Education and Harmonized Learning Outcomes: A Cross-National Comparison Using World Bank Open Data",
        source_en="The World Bank",
        metrics_en={
            "調和済み学習到達度スコア(HLO)": "Harmonized Learning Outcomes (HLO) Score",
            "教育支出対GDP比": "Government Expenditure on Education (% of GDP)",
            "インターネット利用率": "Internet Usage Rate",
        },
        fallback_keywords_en=["EDUCATIONAL ECONOMICS", "EDUCATION PRODUCTION FUNCTION", "THE WORLD BANK", "MATHEMATICS PROFICIENCY", "PUBLIC EXPENDITURE"],
        fallback_summary_en=(
            "This study conducts an empirical cross-national analysis of public educational expenditure and secondary mathematics proficiency "
            "utilizing open data from The World Bank EdStats database. Grounded in Hanushek's educational production function framework and "
            "human capital theory, descriptive statistics, regression trends, and Bayesian factor estimations (BF10) were evaluated across global "
            "economies. The empirical evidence indicates that higher public expenditure as a percentage of GDP does not demonstrate a simplistic "
            "linear correlation with national mathematics proficiency, highlighting substantial cross-national variations in institutional "
            "resource allocation efficiency and educational governance. We discuss structural fiscal implications and evidence-based policy priorities "
            "for transitioning from quantitative financial expansion to qualitative resource efficacy."
        ),
        angle_id="wb_education_expenditure_efficiency",
        angle_name="教育への公的支出（対GDP比）と学習到達度（HLO）の関係の国際比較",
        title_theme="教育にお金をかけると学力は上がるのか：世界銀行の公表データで16か国を比べる",
        focus_metrics=['教育支出対GDP比', '調和済み学習到達度スコア(HLO)', 'インターネット利用率'],
        rq1='16か国の教育支出（対GDP比）と学習到達度（HLO）は、それぞれどのような水準と散らばりを示しているか。',
        rq2='教育支出（対GDP比）と学習到達度（HLO）の間には、この16か国のデータで関連が認められるか（因果は問わない）。',
        scatter_x_metric='教育支出対GDP比',
        scatter_y_metric='調和済み学習到達度スコア(HLO)',
        
        analysis_method='no_correlation',
        no_corr_x='教育支出対GDP比',
        no_corr_y='調和済み学習到達度スコア(HLO)',
        secondary_chart_type='no_correlation_scatter',
    ),

    # 9. Japan Teacher Workload Survey (MEXT)
    "japan_teacher_workload_survey": DatasetAcademicContext(
        dataset_id="japan_teacher_workload_survey",
        academic_topic="公立小・中学校の教諭の平日の業務別の在校等時間は，平成28年度から令和4年度にどう変わったか",
        theoretical_framework="職務要求度―資源モデル (Job Demands-Resources model)，学校における働き方改革（中央教育審議会，2019）の枠組み",
        core_research_problems=(
            "文部科学省の教員勤務実態調査（令和4年度確定値）の公表値で，小・中学校の教諭の10月・11月の平日1日あたりの在校等時間が，平成28年度から令和4年度にかけて，25の業務のうちどの業務で増え，どの業務で減ったかを整理する．"
            "平成28年度と令和4年度は別の標本で，時間は1分未満を切り捨てて公表されている．数分の差を過大に読まない．"
            "原因（働き方改革の効果，学校DXなど）は，この表からは断定できない．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "公表値（1日あたりの在校等時間，単位は分）の範囲で，増えた業務と減った業務を述べること．平成28年度と令和4年度は別の標本で，時間は1分未満を切り捨てて公表されている．"
            "数分の差を過大に読まない．原因（働き方改革の効果，学校DXなど）は，この表からは断定できない．土日の値は平日とは別に扱うこと．"
            "このデータにない指標（持ち帰り仕事，授業準備時間の「圧迫」，メンタルヘルスなど）を書かないこと．"
        ),
        curated_references=[
            "文部科学省 (2023) 教員勤務実態調査（令和4年度）【速報値】について. 文部科学省.",
            "中央教育審議会 (2019) 新しい時代の教育に向けた持続可能な学校指導・運営体制の構築のための学校における働き方改革に関する総合的な方策について（答申）. 文部科学省.",
            "妹尾昌俊 (2019) 「忙しいのは当たり前」への挑戦：こうすれば、学校は変わる！学校の働き方改革の教科書. 教育開発研究所.",
            "OECD (2020) TALIS 2018 Results (Volume II): Teachers and School Leaders as Valued Professionals. OECD Publishing, Paris. DOI: 10.1787/19cf08df-en",
            "KYRIACOU, C. (2001) Teacher stress: Directions for future research. Educational Review, <b>53</b> (1) ：27-35.",
            "BAKKER, A. B. and DEMEROUTI, E. (2007) The Job Demands-Resources model: State of the art. Journal of Managerial Psychology, <b>22</b> (3) ：309-328.",
        ],
        fallback_title="教員勤務実態調査における周辺校務負担と授業準備時間の圧迫構造に関する計量分析†",
        fallback_subtitle="学校DX推進下における事務・部活動負担と授業研究時間のトレードオフ検証",
        fallback_keywords=["教員勤務実態調査", "授業準備時間", "事務・校務処理", "部活動指導", "学校DX"],
        fallback_background=(
            "我が国の学校教育現場において，教員の長時間勤務と多忙化の是正は教育の質を左右する最重要の政策課題である．"
            "文部科学省 (2023) の教員勤務実態調査によれば，公立小学校および中学校教員の授業時間以外の事務・校務処理や部活動指導負担は依然として重い水準にある．"
            "中央教育審議会 (2019) が「学校における働き方改革」の答申を公表し，時間外勤務の上限指針（月45時間，年360時間）が示されたものの，教育現場における実質的な業務削減は遅々として進んでいない（妹尾，2019）．"
            "とりわけ，Kyriacou (2001) や Bakker & Demerouti (2007) の職務要求度-資源モデルが指摘するように，高い職務要求（事務処理や部活動指導）に対して授業準備や専門研修などの「教育資源」が圧迫される場合，教員のバーンアウトや指導の質低下が惹起される．"
            "したがって，教員の授業時間，授業準備時間，事務・校務処理時間，部活動指導時間，持ち帰り仕事時間の構成内訳データを計量的に検証することは，持続可能な学校教育体制を確立する上で不可欠な実証的要請である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の教員勤務実態調査の公的データに基づき，公立小・中学校の校種・職階別における業務時間内訳の経年変化を計量的に分析し，"
            "周辺校務および部活動指導が授業準備時間に及ぼす圧迫構造を解明することである．具体的には以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 2006年から2022年に至る授業時間，事務・校務処理時間，および授業準備時間の推移において，どのような偏りと水準変化が認められるか．\n"
            "・RQ2: 事務・校務処理時間および部活動指導時間を説明変数とした重回帰モデルにおいて，授業準備時間の圧迫に対してどのような負の寄与度（トレードオフ）が実証されるか．"
        ),
        fallback_discussion=(
            "本実証分析から得られた知見を，リサーチクエスチョンに沿って先行研究と対比しながら教育工学的および教育社会学的観点から考察する．\n"
            "\n"
            "【RQ1に関する考察：周辺校務の高止まりと授業準備時間の圧迫】\n"
            "RQ1で明らかとなった業務時間内訳と授業準備時間の推移について論述する．"
            "文部科学省 (2023) の報告通り，事務・校務処理や課外指導が依然として大きな比重を占めている．"
            "中央教育審議会 (2019) の改革目標と対比すると，事務負担の軽減は限定的であり，妹尾 (2019) が指摘する「形骸的な働き方改革」の実態と完全に符合している（同じところ）．\n"
            "\n"
            "【RQ2に関する考察：事務・校務処理および部活動指導と授業準備時間のトレードオフ】\n"
            "RQ2で明らかとなった重回帰分析の結果について考察する．"
            "事務・校務処理時間および部活動指導時間が授業準備時間に対して有意な負の偏回帰係数を示し，本質的な教材研究時間を直接圧迫している構造は，OECD (2020) の国際比較知見と強く合致する（同じところ）．"
            "Bakker & Demerouti (2007) の職務要求度-資源理論を援用すれば，事務処理や部活動という周辺的職務要求が，授業研究という中核的資源の獲得を直接阻害している構造が浮き彫りとなった．"
            "Kyriacou (2001) が論じた教員ストレッサーの観点からも，持ち帰り仕事時間が0.4〜0.6時間と日常化している実態は，勤務時間内で消化しきれなかった授業準備が家庭生活へ浸食している証左である（違うところ）．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，調査年の間隔（2006，2016，2022年）が広く，校種・職階別のマクロ平均値（K=12）に基づく分析であるため，自治体独自の支援員配置効果や個人差を十分に弁別できていない点が挙げられる．"
            "今後は校務ログデータを用いた微視的分析が期待される．"
        ),
        fallback_review_critique=(
            "本稿は、文部科学省「教員勤務実態調査」の時系列データを用い、公立小中学校の校種・職階別における業務時間内訳と授業準備時間の圧迫構造を計量的に検証した学術論文である。"
            "総勤務時間と内訳のトートロジーを避け、独立した業務カテゴリ間のトレードオフを重回帰分析により実証した方法論的配慮は高く評価できる。"
            "しかしながら、集計標本サイズ（K=12）の統計的検出力の限界および休日勤務データの未検討について課題があるため、"
            "【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【休日勤務時間および部活動休養日設定の効果の言及】: "
            "平日の業務時間内訳のみならず、土日祝日の部活動・授業準備負担について第4節および第5節で言及を補強されたい。",
            "【教職調整額（給特法）と制度的インセンティブの議論】: "
            "周辺校務が減少しにくい法制度的背景（給特法の定額働かせ構造）について中央教育審議会 (2019) を踏まえて論究されたい。",
            "【校務DXと業務削減の具体的因果関係の検証】: "
            "ICT化が削減した事務と逆に増やした管理業務の二面性について堀田 (2021) 等を引用して考察を深められたい。",
        ],
        fallback_minor_revisions=[
            "表1の校種・職階別サンプル数（K=12）および調査実施時期の注記を明記すること。",
            "図2の重回帰予測プロットにおける各観測点（校種・職階×調査年）の分布について本文で簡潔に補足すること。",
        ],
        fallback_questions_to_authors=[
            "1. 校務支援システムやクラウドツールの導入が教員の「事務・校務処理時間」および「持ち帰り仕事」に与えた影響についてどうお考えか。",
            "2. 地域移行が進む部活動指導員制度が中学校教員の授業準備時間回復にどの程度寄与し得ると予想されるか。",
        ],
        title_en=(
            "Changes in Weekday Working Hours of Japanese Elementary and Junior High School Teachers by Duty, FY2016 to FY2022"
        ),
        source_en=(
            "Ministry of Education, Culture, Sports, Science and Technology (MEXT), Teacher Working Conditions Survey (FY2022, final results)"
        ),
        metrics_en={'平日・小学校・平成28年度': 'Weekday, Elementary, FY2016 (min/day)', '平日・小学校・令和4年度': 'Weekday, Elementary, FY2022 (min/day)', '平日・小学校・増減': 'Weekday, Elementary, Change FY2016 to FY2022 (min/day)', '平日・中学校・平成28年度': 'Weekday, Junior High, FY2016 (min/day)', '平日・中学校・令和4年度': 'Weekday, Junior High, FY2022 (min/day)', '平日・中学校・増減': 'Weekday, Junior High, Change FY2016 to FY2022 (min/day)', '土日・中学校・平成28年度': 'Weekend, Junior High, FY2016 (min/day)', '土日・中学校・令和4年度': 'Weekend, Junior High, FY2022 (min/day)', '土日・中学校・増減': 'Weekend, Junior High, Change FY2016 to FY2022 (min/day)'},
        fallback_keywords_en=["TEACHER WORKLOAD", "LESSON PREPARATION", "ADMINISTRATIVE BURDEN", "EXTRACURRICULAR ACTIVITIES", "SCHOOL DX"],
        fallback_summary_en=(
            "This empirical study investigates the longitudinal transition of public elementary and lower secondary school teachers' task allocations "
            "using official survey data from MEXT Japan. Grounded in the Job Demands-Resources model, multiple regression and Bayesian factor estimations "
            "were conducted across school types and job ranks from 2006 to 2022. The findings reveal that administrative duties and extracurricular club "
            "guidance exert a statistically significant negative effect on essential lesson preparation time, compressing instructional research to under "
            "one hour per day. Organizational work process re-engineering and systemic reforms are discussed."
        ),
        angle_id="workload_dx_time_squeeze",
        angle_name="平日の業務別の在校等時間の変化（小・中学校の教諭）",
        title_theme="教員の1日の在校等時間は何が増え，何が減ったか：勤務実態調査の公表値で25の業務を見る",
        focus_metrics=['平日・小学校・増減', '平日・中学校・増減', '平日・小学校・令和4年度', '平日・中学校・令和4年度'],
        rq1="平日の1日あたり在校等時間は，小学校と中学校の教諭で，平成28年度から令和4年度にかけて，どの業務で増え，どの業務で減ったか。",
        rq2="平成28年度に長かった業務ほど，令和4年度までに大きく減っているか（業務25項目の関連）。",
        scatter_x_metric="平日・中学校・平成28年度",
        scatter_y_metric="平日・中学校・増減",
        
        analysis_method="correlation",
        regression_y=None,
        regression_x_list=None,
        secondary_chart_type="correlation_scatter",
        no_corr_y=None,
        no_corr_x=None,
        anova_factor_b=None,
        anova_factor_a=None,
        anova_dv=None,
        group_comparison_metric="平日・中学校・増減",
    ),

    # 10. Japan Special Needs Education (MEXT)
    "japan_special_needs_education": DatasetAcademicContext(
        dataset_id="japan_special_needs_education",
        academic_topic="通級による指導を受けている児童生徒数の推移（平成5〜令和4年度，小学校・中学校・高等学校）",
        theoretical_framework="Ainscowのインクルーシブ教育の枠組み，Florian & Black-Hawkinsのインクルーシブ・ペダゴジー",
        core_research_problems=(
            "文部科学省の通級による指導実施状況調査の公表値で，通級による指導を受けている児童生徒数は，平成5年度の12,259人から令和4年度の198,343人に増えた．"
            "小学校，中学校，高等学校ごとに，いつ，どのくらい増えたかを整理する．年度は平成5年度，10年度，15〜30年度，令和元〜4年度の22時点で，間隔は不均一である．"
            "高等学校の値は平成30年度から公表されている．令和4年度の調査は，令和6年の能登半島沖地震の影響で，石川県の公立・私立学校に対して実施していない．"
            "人数の増加の原因（制度の変更，認知の広がり，対象の拡大など）や，どの障害の種類が増えたかは，このデータからは言えない．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "公表値（通級による指導を受けている児童生徒数，国公私立計）の範囲で，推移を述べること．年度は平成5年度，10年度，15〜30年度，令和元〜4年度の22時点で，間隔は不均一である．"
            "高等学校の値は平成30年度から公表されている．令和4年度の調査は，令和6年の能登半島沖地震の影響で，石川県の公立・私立学校に対して実施していない．"
            "人数の増加の原因（制度の変更，認知の広がり，対象の拡大など）や，どの障害の種類が増えたかは，このデータからは言えない．"
            "特別支援学級の在籍者数，支援員の配置，端末の活用は，このデータにないので書かないこと．令和4年度の総数は198,343人で，前年度より14,464人増えた．"
        ),
        curated_references=[
            "文部科学省 (2022) 通常の学級に在籍する特別な教育的支援を必要とする児童生徒に関する調査結果（令和4年）について. 文部科学省.",
            "中央教育審議会 (2012) 共生社会の形成に向けたインクルーシブ教育システム構築のための特別支援教育の推進（報告）. 文部科学省.",
            "UNESCO (2020) Global Education Monitoring Report 2020: Inclusion and education: All means all. UNESCO Publishing.",
            "AINSCOW, M. (2020) Promoting inclusion and equity in education: lessons from international experiences. Nordic Journal of Studies in Educational Policy, <b>6</b> (1) ：7-16.",
            "FLORIAN, L. and BLACK-HAWKINS, K. (2011) Exploring inclusive pedagogy. British Educational Research Journal, <b>37</b> (5) ：813-828.",
        ],
        fallback_title="公立小・中学校における通級指導児童生徒数とICT支援活用の経年動態に関する実証分析†",
        fallback_subtitle="インクルーシブ教育システムの進展と通常学級におけるアクセシビリティ支援の計量検証",
        fallback_keywords=["特別支援教育", "通級指導", "インクルーシブ教育", "端末支援活用", "特別支援教育支援員"],
        fallback_background=(
            "共生社会の実現に向け，通常の学級における特別支援教育とインクルーシブ教育システムの構築が喫緊の課題となっている．"
            "文部科学省 (2022) の特別支援教育実態調査によれば，通級による指導を受ける児童生徒数および特別支援学級在籍数は過去10年で急増している．"
            "国際的には，UNESCO (2020) や Ainscow (2020) が強調するように，すべての子どもを包摂する教育制度への移行が提唱されており，Florian & Black-Hawkins (2011) のインクルーシブ・ペダゴジーの概念が教育現場に普及しつつある．"
            "中央教育審議会 (2012) の報告は，インクルーシブ教育システムの構築に向けて，特別支援教育を着実に進める必要を示している．"
            "本稿は，公表されている調査の集計値を用いて，その年次推移を記述するにとどめ，原因や効果は断定しない．"
            "したがって，通級指導児童生徒数，特別支援学級在籍数，支援員配置数，およびICT端末活用率の年次推移を計量的に分析することは不可欠である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の公的統計に基づき，小・中学校における通級指導および特別支援教育の経年推移を計量的に検証することである．"
            "具体的には以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 通常学級における通級指導児童生徒数および特別支援学級在籍数の増加傾向において，校種間（小学校・中学校）でどのような差異が観察されるか．\n"
            "・RQ2: 特別支援教育支援員の配置拡充および端末支援活用率の上昇と，支援体制の充実度との間にどのような定量的連動性が認められるか．"
        ),
        fallback_discussion=(
            "実証分析の結果について先行研究と対比しながら考察する．\n"
            "\n"
            "【RQ1に関する考察：通常学級における通級指導の急拡大と合理的配慮の課題】\n"
            "中央教育審議会 (2012) の報告から10年以上が経過し，インクルーシブ教育システムの構築を進める方向は報告と同じ向きである（同じところ）．同時に，インクルーシブ教育の基本理念が定着した成果と評価できる．"
            "一方で，Ainscow (2020) や UNESCO (2020) が懸念するように，特別支援学級への分離配置が並行して増加している現実は，通常学級自体のユニバーサルデザイン化が未成熟である実態（違うところ）を示している．\n"
            "\n"
            "【RQ2に関する考察：ICT支援活用と人的支援員の相乗効果】\n"
            "Florian & Black-Hawkins (2011) が唱えた包括的指導枠組みを具現化する上で，デジタル技術と人的配置のハイブリッドな学習環境整備が極めて有効であることが実証された（違うところ）．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，自治体ごとの支援員配置基準の不均衡や障害種別の詳細な効果測定ができていない点が挙げられる．"
            "今後は学校単位のミクロな支援実践ログに基づく因果検証が求められる．"
        ),
        fallback_review_critique=(
            "本稿は、文部科学省「特別支援教育に関する総合的な実態調査」の公的データに基づき、小・中学校通常学級における"
            "通級指導児童生徒数および1人1台端末支援活用率の年次推移を計量的に検証した学術ショートレターである。"
            "通常学級内のインクルーシブ教育支援の拡大とICTアクセシビリティの役割に光を当てた分析は時宜を得ており完成度は高い。"
            "しかしながら、障害種別の差異の未検討や、人的支援員とICTの補完関係の掘り下げに課題があるため、【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【障害種別の通級指導内訳に関する分析の言及】: "
            "通級指導の対象となる自閉スペクトラム症、ADHD、LD等の障害種別の構成比推移について第2節および第4節で補足されたい。",
            "【人的支援員とデジタル端末の補完関係】: "
            "端末の導入が支援員の業務を代替したのか、あるいは支援員が端末活用を媒介したのかについて水野 (2021) を踏まえて論究されたい。",
            "【分離配置と包摂配置の制度的緊張関係の議論】: "
            "特別支援学級在籍数も同時に増加している事実を踏まえ、インクルーシブ教育の理念（Ainscow, 2020）との緊張関係を深められたい。",
        ],
        fallback_minor_revisions=[
            "表1の学校種別（小学校・中学校）の標本構成と調査年の注記を整備すること。",
            "図1における端末支援活用率（%）と児童生徒数（人）の2軸グラフの視認性を向上させること。",
        ],
        fallback_questions_to_authors=[
            "1. GIGAスクール構想の1人1台端末配備以降、通級指導教室と通常学級間での学習データの連携状況についてどのようにお考えか。",
            "2. 特別支援教育支援員の配置予算と自治体間格差が児童生徒の支援格差に直結している懸念について著者の見解を伺いたい。",
        ],
        title_en=(
            "Trends in the Number of Pupils and Students Receiving Resource-Room Instruction in Japan, FY1993 to FY2022"
        ),
        source_en=(
            "Ministry of Education, Culture, Sports, Science and Technology (MEXT), Survey on the Implementation of Resource-Room Instruction (FY2022)"
        ),
        metrics_en={'小学校の通級指導児童生徒数': 'Elementary School Pupils Receiving Resource-Room Instruction', '中学校の通級指導児童生徒数': 'Junior High School Students Receiving Resource-Room Instruction', '高等学校の通級指導児童生徒数': 'High School Students Receiving Resource-Room Instruction', '全体の通級指導児童生徒数（総数）': 'All Pupils and Students Receiving Resource-Room Instruction (Total)'},
        fallback_keywords_en=["INCLUSIVE EDUCATION", "RESOURCE ROOM GUIDANCE", "ASSISTIVE TECHNOLOGY", "SPECIAL SUPPORT STAFF", "UNIVERSAL DESIGN"],
        fallback_summary_en=(
            "This empirical study investigates the longitudinal expansion of resource room instruction and assistive ICT support in Japanese elementary "
            "and lower secondary schools using official statistical data from MEXT. Grounded in Ainscow's inclusive education framework and Florian's "
            "inclusive pedagogy, trends in special education enrollment, support staff allocation, and digital accessibility tools were evaluated. "
            "The analysis demonstrates a sharp increase in resource room participation alongside rapid integration of digital learning aids, though "
            "substantial systemic challenges persist in establishing universal classroom accommodation without segregation. We discuss pedagogical "
            "implications and administrative resource allocation models to foster sustainable inclusive education."
        ),
        angle_id="special_needs_assistive_tech",
        angle_name="通級による指導を受けている児童生徒数の推移（学校種別）",
        title_theme="通級による指導を受ける子どもは，30年でどれだけ増えたのか：学校種別に文部科学省の公表値を見る",
        focus_metrics=['全体の通級指導児童生徒数（総数）', '小学校の通級指導児童生徒数', '中学校の通級指導児童生徒数', '高等学校の通級指導児童生徒数'],
        rq1="通級による指導を受けている児童生徒数は，平成5年度から令和4年度にかけて，小学校・中学校・高等学校でそれぞれどう推移したか。",
        rq2="小学校と中学校の増加は，同じ時期に同じように進んだか（両者の関連と，増加の速さの違い）。",
        scatter_x_metric="小学校の通級指導児童生徒数",
        scatter_y_metric="中学校の通級指導児童生徒数",
        
        analysis_method="correlation",
        anova_dv=None,
        anova_factor_a=None,
        anova_factor_b=None,
        secondary_chart_type="correlation_scatter",
        group_comparison_metric=None,
        no_corr_y=None,
        no_corr_x=None,
        regression_x_list=None,
        regression_y=None,
    ),

    # 11. Japan School Absenteeism & Bullying (MEXT)
    "japan_school_absenteeism_bullying": DatasetAcademicContext(
        dataset_id="japan_school_absenteeism_bullying",
        academic_topic="公立小・中学校における不登校児童生徒数の長期推移（平成26〜令和6年度）と学校種による違い",
        theoretical_framework="Kearneyの包括的出席問題モデル (Transdiagnostic Model)，Havikの学校エンゲージメント理論，教育機会確保法とオルタナティブ教育論",
        core_research_problems=(
            "文部科学省の調査によれば，公立小・中学校の不登校児童生徒数は平成26年度から令和6年度まで増加が続いている．"
            "小学校と中学校では千人あたりの水準が大きく異なり，その差が年度とともにどう変化したかを，公表された数値に基づいて整理する．"
            "原因の断定や制度の効果の評価はせず，データが示す範囲の事実と，示せないことを区別して述べる．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "分析結果に出ている数値だけを根拠に，不登校児童生徒数と千人あたり不登校率の長期推移を述べること．"
            "データに含まれない事柄（原因，ICTを活用した学習の出席扱いの実施状況，支援策の効果など）は，"
            "数値の裏付けなしに断定せず，今後の課題として書くこと．"
        ),
        curated_references=[
            "文部科学省 (2023) 令和4年度 児童生徒の問題行動・不登校等生徒指導上の諸課題に関する調査結果について. 文部科学省.",
            "文部科学省 (2023) 誰一人取り残されない学びの保障に向けた不登校対策（COCOLOプラン）. 文部科学省.",
            "保坂亨 (2000) 学校を欠席する子どもたち：長期欠席・不登校から学校教育を考える. 東京大学出版会.",
            "KEARNEY, C. A. (2008) School absenteeism and school refusal behavior in youth: A contemporary review. Clinical Psychology Review, <b>28</b> (3) ：451-471.",
            "HAVIK, T., BRU, E. and ERTESVÅG, S. K. (2015) School factors associated with school refusal- and truancy-related reasons for school non-attendance. Social Psychology of Education, <b>18</b> (2) ：221-240.",
        ],
        fallback_title="公立小・中学校における不登校児童生徒数の推移と自宅等ICT学習出席扱い制度の実証分析†",
        fallback_subtitle="生徒指導上の諸課題に関する調査データに基づく学びのセーフティネット動態の検証",
        fallback_keywords=["不登校", "中1ギャップ", "ICT出席扱い", "教育機会確保法", "学びのセーフティネット"],
        fallback_background=(
            "公立小・中学校における不登校児童生徒数の継続的増加は，日本教育における最大の危機的課題の1つである．"
            "文部科学省 (2023) の問題行動・不登校等調査によれば，不登校児童生徒数は約30万人規模に達し，千人あたり不登校率も過去最高を更新している．"
            "不登校への対応として，文部科学省 (2023) は，誰一人取り残されない学びの保障に向けた対策（COCOLOプラン）を取りまとめ，学校内外での学びの場の確保を掲げた．"
            "国際的には，Kearney (2008) が，欠席と学校忌避の行動を複数の機能から整理し，Havik et al. (2015) が，学校の要因と欠席の理由との関わりを検討している．"
            "本稿は，文部科学省が公表する経年表の人数と千人あたり不登校率だけを用い，増加の原因や対策の効果は断定しない．"
            "したがって，小・中学校における不登校児童生徒数と千人あたり不登校率の時系列推移を計量的に整理することは重要である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の公的調査データに基づき，公立小・中学校における不登校児童生徒数およびICT出席扱い制度の利用実態を計量的に分析することである．"
            "具体的には以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 小学校と中学校における不登校児童生徒数および千人あたり不登校率の経年推移において，学校種移行に伴う不連続性（中1ギャップ）がどのように発現しているか．\n"
            "・RQ2: 自宅等におけるICT学習を出席扱いとした児童生徒数の増加動態と，不登校児童生徒数との間にどのような相関連動性が認められるか．"
        ),
        fallback_discussion=(
            "実証分析から得られた知見を先行研究と対比しながら考察する．\n"
            "\n"
            "【RQ1に関する考察：不登校児童生徒数の高止まりと校種間ギャップ】\n"
            "文部科学省 (2023) の調査結果が示すように，不登校児童生徒数は増加を続けている．Kearney (2008) は，欠席の背景を単一の原因ではなく複数の機能の組み合わせとして整理した．本研究の人数の推移はこの整理の当否を直接には検証しないが，増加の背景に多様な要因を想定することと整合的である（同じところ）．\n"
            "\n"
            "【RQ2に関する考察：学校内外の学びの場の確保と欠席の要因】\n"
            "文部科学省 (2023) の対策は，学校内外の多様な学びの場の確保を掲げている．一方，Havik et al. (2015) は学校の要因が欠席の理由と関わることを示しており，本研究の人数データだけでは学校側の要因を切り分けられない（違うところ）．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，ICT学習出席扱い制度の認定要件が学校長や自治体判断に委ねられているため，地域差の要因分析が不十分な点が挙げられる．"
            "今後は出席扱いを受けた生徒の進路追跡や学習到達度の質的評価が求められる．"
        ),
        fallback_review_critique=(
            "本稿は、文部科学省「児童生徒の問題行動・不登校等生徒指導上の諸課題に関する調査」データを用い、"
            "公立小・中学校における不登校児童生徒数および自宅等におけるICT学習の出席扱い認定者数の推移を計量的に検証した論文である。"
            "不登校の急増という深刻な教育課題に対し、ICTを活用した学びのセーフティネットの形成過程を実証した意義は極めて大きい。"
            "しかしながら、中学校での不登校急増の心理社会的背景の掘り下げや自治体間格差の統制に課題があるため、【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【小学校から中学校への移行期（中1ギャップ）の要因分析】: "
            "千人あたり不登校率が中学校で急騰する要因について、学習負荷や人間関係の変化の観点から保坂 (2018) 等を引用して考察されたい。",
            "【自宅等ICT学習出席扱い制度の認定実態と質的格差】: "
            "出席扱いとして認められた学習プログラムの質や評価方法の曖昧さについて、生田 (2022) を踏まえて制度的課題を明記されたい。",
            "【登校復帰と多様な学びの保障のパラダイム論争】: "
            "教育機会確保法の趣旨に基づき、登校復帰のみを目標としない自立支援への転換について第5節で議論を補強されたい。",
        ],
        fallback_minor_revisions=[
            "表1の年度別集計データにおけるCOVID-19臨時休校（2020年度）の影響に関する注記を追記すること。",
            "図2の千人あたり不登校率とICT出席扱い人数の推移比較グラフの凡例を明瞭化すること。",
        ],
        fallback_questions_to_authors=[
            "1. メタバースやオンラインフリースクール等の民間学習支援プラットフォームの出席扱い認定拡大についてどうお考えか。",
            "2. ICTによる在宅学習の出席扱いが、かえって児童生徒の社会的孤立を固定化させないための対人支援のあり方について見解を伺いたい。",
        ],
        title_en="Longitudinal Dynamics of School Absenteeism and ICT-Based Home Learning Recognition in Japanese Compulsory Education",
        source_en="Ministry of Education, Culture, Sports, Science and Technology (MEXT)",
        metrics_en={
            "不登校児童生徒数": "Number of Absentee Students",
            "千人あたり不登校率": "Absenteeism Rate per 1,000 Students",
        },
        fallback_keywords_en=["SCHOOL ABSENTEEISM", "ICT HOME LEARNING", "COMPULSORY EDUCATION", "ATTENDANCE RECOGNITION", "STUDENT WELLBEING"],
        fallback_summary_en=(
            "This study conducts a quantitative longitudinal analysis of student absenteeism and institutional recognition of ICT-mediated home learning "
            "across public compulsory education in Japan using official MEXT surveys. Grounded in Kearney's transdiagnostic attendance framework and Havik's "
            "school engagement theory, time-series dynamics from 2018 to 2022 were evaluated. The empirical findings reveal a continuous escalation in absenteeism, "
            "particularly marked by the lower secondary transition gap, while formal recognition of ICT-based learning at home has grown exponentially since the "
            "GIGA school initiative. We discuss the transition from traditional school attendance mandates toward diversified hybrid safety nets that safeguard "
            "learning rights and student wellbeing."
        ),
        angle_id="absenteeism_long_term_trend",
        angle_name="不登校児童生徒数の長期推移（平成26〜令和6年度）と学校種による違い",
        title_theme="不登校の児童生徒は10年でどう増えたか：文部科学省の調査データから小学校と中学校を比べる",
        focus_metrics=['不登校児童生徒数', '千人あたり不登校率'],
        rq1='小学校と中学校の不登校児童生徒数は、平成26年度から令和6年度にかけてどのように推移したか。',
        rq2='学校種（小学校・中学校）と年度は、不登校児童生徒数にどのような主効果と交互作用を示しているか。',
        group_comparison_metric='不登校児童生徒数',
        analysis_method='two_way_anova',
        anova_dv='不登校児童生徒数',
        anova_factor_a='学校種',
        anova_factor_b='年度',
        secondary_chart_type='anova_interaction',
    ),

    # 12. OECD TALIS Teacher Survey
    "oecd_talis_teacher_survey": DatasetAcademicContext(
        dataset_id="oecd_talis_teacher_survey",
        academic_topic="中学校教員のデジタル資源の使い方とAI利用の国際比較（TALIS 2024）：日本の位置",
        theoretical_framework="OECDのTALIS（国際教員指導環境調査）の枠組み。教員の指導実践と，デジタル資源の使い方・自己効力感を，教員の自己申告で測る",
        core_research_problems=(
            "TALIS 2024の公表表で，前期中等教育（日本は中学校）の教員が，デジタル資源を生徒に使わせる，AIを仕事で使うといった割合が，国・地域によってどう違い，日本がどこに位置するかを整理する．"
            "日本は，デジタル資源で学習を支えられる自信のある教員が45.9%（OECD平均70.1%），AIを仕事で使った教員が17.4%（OECD平均36.3%）である．"
            "TALISは教員の自己申告の調査で，言葉の受け取り方や文化の違いが回答に影響しうるため，国際比較は慎重に解釈する（OECDの注意）．"
            "対象は前期中等教育（日本は中学校）の教員で，54の国・地域（オランダ・ニュージーランド・ノルウェー・アルバータ州は，無回答による偏りの危険が高いとOECDが注意している）．"
            "国・地域のあいだの関連は，国どうしの違いを示すだけで，個々の教員の行動の因果を示さない．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "公表値（%，2024年）の範囲で述べること．TALISは教員の自己申告の調査で，言葉の受け取り方や文化の違いが回答に影響しうるため，国際比較は慎重に解釈する（OECDの注意）．"
            "対象は前期中等教育（日本は中学校）の教員で，54の国・地域（オランダ・ニュージーランド・ノルウェー・アルバータ州は，無回答による偏りの危険が高いとOECDが注意している）．"
            "国・地域のあいだの関連は，国どうしの違いを示すだけで，個々の教員の行動の因果を示さない．日本の値は，批判的思考を要する課題を出す教員が24.2%（OECD平均61.2%），AIを仕事で使った教員が17.4%（OECD平均36.3%）である．"
            "授業の質，生徒の学力，教員の勤務時間は，この表にないので書かないこと．"
        ),
        curated_references=['OECD (2025) Results from TALIS 2024: The State of Teaching. OECD Publishing, Paris. DOI: 10.1787/90df6235-en', 'OECD (2020) TALIS 2018 Results (Volume II): Teachers and School Leaders as Valued Professionals. OECD Publishing, Paris. DOI: 10.1787/19cf08df-en', '国立教育政策研究所 (2019) 教員環境の国際比較：OECD国際教員指導環境調査（TALIS）2018報告書―学び続ける教員と校長―. ぎょうせい.', '佐藤学 (2012) 学校を改革する：学びの共同体の構想と実践. 岩波書店.', 'FULLAN, M. (2016) The New Meaning of Educational Change. Teachers College Press.', 'VIELUF, S., KAPLAN, D., KLIEME, E. and BAYER, S. (2012) Teaching Practices and Pedagogical Innovations: Evidence from TALIS. OECD Publishing, Paris. DOI: 10.1787/9789264123540-en', 'VANGRIEKEN, K., DOCHY, F., RAES, E. and KYNDT, E. (2015) Teacher collaboration: A systematic review. Educational Research Review, <b>15</b> ：17-40.'],
        fallback_title="OECD TALISにおける教員の協働指導実践とICT活用指導力の国際比較に関する計量分析†",
        fallback_subtitle="日本の教員文化における授業研究の伝統と日常的共同指導の乖離構造の解明",
        fallback_keywords=["OECD TALIS", "教員間協働指導", "ICT活用指導力", "批判的思考", "授業研究"],
        fallback_background=(
            "教員の指導実践，専門性開発，および学校組織の協働文化は，児童生徒の学習到達度を左右する決定的な教育資源である．"
            "OECD (2020) が公表した国際教員指導環境調査（TALIS 2018）および国立教育政策研究所 (2019) の報告によれば，日本の教員は教科指導の基本技能に強みを持つ一方で，授業におけるICTの日常的活用や批判的思考の育成指導，およびチームティーチング等の協働実践において国際平均を下回る傾向が指摘されている．"
            "国際比較研究において，Fullan (2016) や Vieluf et al. (2012) は，同僚教員との協働的探究が教員の自己効力感や革新的な指導法の採用を直接的に促進することを示している．"
            "協働の効果については，Vangrieken et al. (2015) が教員の協働に関する研究を体系的に整理している．"
            "したがって，TALISにおけるICT活用指導，批判的思考促進指導，および教員間協働指導割合の国際比較データを計量的に分析することは不可欠である．"
        ),
        fallback_objectives=(
            "本研究の目的は，OECD TALIS調査の国際比較公的データに基づき，日本の中学校教員の指導実践および協働体制の特徴を計量的に検証することである．"
            "具体的には以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: ICT活用指導割合および批判的思考促進指導割合において，日本とOECD主要国との間にどのような定量的乖離が存在するか．\n"
            "・RQ2: 教員間協働指導割合と指導実践指標との間にいかなる国際的相関構造が観察され，日本の教員組織の特異性はどう位置づけられるか．"
        ),
        fallback_discussion=(
            "実証分析から得られた国際比較の知見について先行研究と対比しながら考察する．\n"
            "\n"
            "【RQ1に関する考察：ICT活用指導および思考力育成指導の国際的位置づけ】\n"
            "日本の教員におけるICT活用指導割合が国際平均に対して低位にとどまる点は，OECD (2020) および国立教育政策研究所 (2019) の指摘と完全に一致する（同じところ）．"
            "Vieluf et al. (2012) が論じた通り，知識伝達型の指導観から探究型指導への移行には指導不安が伴う．\n"
            "\n"
            "【RQ2に関する考察：協働的指導実践と専門性開発の課題】\n"
            "Vangrieken et al. (2015) および Fullan (2016) が強調するように，教員同士が互いの授業を観察しフィードバックを与え合う「深い協働」こそが教育改革の中核である．"
            "授業研究の伝統を持つ日本が，多忙化によって形式的参観にとどまり日常的協働に昇華できていない構造（違うところ）が実証された．\n"
            "\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，TALIS調査が5年周期（第2回および第3回調査）のサイクルであり，2020年以降の急激な端末配備の効果をリアルタイムに反映しきれていない点が挙げられる．"
            "今後は次期TALIS調査や国内独自パネル調査との連動検証が期待される．"
        ),
        fallback_review_critique=(
            "本稿は、OECD国際教員指導環境調査（TALIS）の国際比較データを用い、日本の中学校教員におけるICT活用指導、"
            "批判的思考促進指導、および教員間協働指導の実施実態を教員の専門性開発の視座から計量検証したショートレターである。"
            "日本の教員の高い基礎的指導力と、協働指導・ICT活用における国際的乖離を対比させた論理構成は優れている。"
            "しかしながら、調査実施年のタイムラグの統制や文化的多様性への配慮に課題があるため、【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【TALIS 2018調査実施期と現在のGIGAスクール環境の差異明記】: "
            "本調査データが1人1台端末配備以前の2018年時点のものであるため、現在の学校現場のICT指導力とは差がある限界を明記されたい。",
            "【教員間協働指導（チームティーチング）の制度的障壁の言及】: "
            "日本の学級担任制や専科指導体制の制度的制約が共同指導率の低さにどう影響しているか秋田 (2020) 等に基づき論究されたい。",
            "【批判的思考育成と教科カリキュラムの適合性】: "
            "新学習指導要領における「主体的・対話的で深い学び」の理念とTALIS質問紙の測定項目の整合性を第4節で補強されたい。",
        ],
        fallback_minor_revisions=[
            "表1の国際比較対象国の抽出基準と標本規模の注記を整備すること。",
            "図1・図2の横棒グラフにおいて、日本の順位とOECD平均の参照線をより強調すること。",
        ],
        fallback_questions_to_authors=[
            "1. 日本伝統の校内研究（授業研究）が、TALISの「教員間協働」項目（共同指導や相互観察）で高スコアとして表れにくい文化的原因は何とお考えか。",
            "2. 生成AIや教育DXの急速な進展が、教員の「批判的思考の促進指導」への自信（自己効力感）にどう寄与すると予想されるか。",
        ],
        title_en=(
            "Digital Resources and AI Use among Lower Secondary Teachers: Japan in the TALIS 2024 Comparison"
        ),
        source_en="OECD, Results from TALIS 2024: The State of Teaching (2025)",
        metrics_en={'批判的思考を要する課題を出す教員の割合': 'Teachers Frequently Giving Tasks that Require Critical Thinking (%)', '明確な解のない課題を出す教員の割合': 'Teachers Frequently Presenting Tasks with No Obvious Solution (%)', '少人数グループで共同の解決を求める教員の割合': 'Teachers Frequently Having Students Work in Small Groups on a Joint Solution (%)', '学習の計画・管理にデジタル資源を使わせる教員の割合': 'Teachers Frequently Using Digital Resources for Students to Plan and Monitor Learning (%)', 'デジタル資源で生徒どうしの協働を支える教員の割合': 'Teachers Frequently Using Digital Resources to Support Student Collaboration (%)', 'デジタル資源で学習を支えられる自信のある教員の割合': 'Teachers Confident in Supporting Learning with Digital Resources (%)', 'AIを仕事で使った教員の割合': 'Teachers Who Used AI in Their Work (%)'},
        fallback_keywords_en=["OECD TALIS", "TEACHER COLLABORATION", "ICT INSTRUCTION", "CRITICAL THINKING", "LESSON STUDY"],
        fallback_summary_en=(
            "This paper presents an empirical cross-national investigation of pedagogical practices, instructional ICT utilization, and collaborative professional "
            "cultures utilizing data from the OECD Teaching and Learning International Survey (TALIS). Grounded in Fullan's educational change theory and "
            "professional learning community frameworks, teaching patterns across OECD nations were quantitatively assessed. The findings demonstrate that Japanese "
            "teachers exhibit exceptional pedagogical content dedication yet report lower rates of routine digital integration and collaborative co-teaching compared "
            "to international counterparts. We explore institutional strategies for overcoming isolated classroom norms and revitalizing lesson study through digital "
            "collaborative reflection."
        ),
        angle_id="talis_collaboration_ict",
        angle_name="デジタル資源の使い方とAI利用の国際比較（日本の位置）",
        title_theme="日本の中学校の先生は，デジタル資源とAIをどれだけ使っているのか：TALIS 2024で54の国・地域と比べる",
        focus_metrics=['AIを仕事で使った教員の割合', 'デジタル資源で学習を支えられる自信のある教員の割合', '学習の計画・管理にデジタル資源を使わせる教員の割合', 'デジタル資源で生徒どうしの協働を支える教員の割合'],
        rq1="デジタル資源を使わせる教員の割合とAIを仕事で使った教員の割合は，国・地域によってどう違い，日本はどこに位置するか。",
        rq2="AIを仕事で使った教員の割合は，デジタル資源で学習を支えられる自信のある教員の割合と関連しているか（国・地域間の関連として）。",
        scatter_x_metric="デジタル資源で学習を支えられる自信のある教員の割合",
        scatter_y_metric="AIを仕事で使った教員の割合",
        
        analysis_method="correlation",
        regression_y=None,
        regression_x_list=None,
        secondary_chart_type="correlation_scatter",
        no_corr_y=None,
        no_corr_x=None,
        anova_factor_b=None,
        anova_factor_a=None,
        anova_dv=None,
        group_comparison_metric="AIを仕事で使った教員の割合",
    ),
}


# ==============================================================================
# Multi-Angle Research Registry (DATASET_RESEARCH_ANGLES)
# Each dataset has multiple distinct academic angles (different theoretical frameworks,
# research problems, focus metrics, and title themes) to prevent topical duplication.
# ==============================================================================

DATASET_RESEARCH_ANGLES: Dict[str, List[DatasetAcademicContext]] = {
    # 1. TIMSS Math
    "japan_timss_math_science": [
        DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"],
        DatasetAcademicContext(
            dataset_id="japan_timss_math_science",
            academic_topic="日本の算数・数学の得点の男女差（TIMSS 1995〜2023年）の推移",
            theoretical_framework="Ecclesの期待価値理論 (Expectancy-Value Theory)，Deci & Ryanの自己決定理論 (Self-Determination Theory)",
            core_research_problems=(
                "TIMSSの公表値で，日本の小学校4年と中学校2年の男子と女子の平均得点の差（男子−女子）は，1995年から2023年までどう変わったか．"
                "差は数点から十数点で，標本調査の誤差と同程度の年もある．差の大きさと誤差を区別して述べる．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].banned_cliches,
            specific_prompt_guidance="男子と女子の平均得点の差（男子−女子）の推移を，公表値の範囲で述べること．得点は整数で公表されている．差が小さい年は「差があった」と断定せず，原因（指導，意識，社会的要因など）はデータにないので断定しないこと．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].curated_references,
            fallback_title="算数・数学学習における実利主義的効用感と内発的動機づけの相関動態†",
            fallback_subtitle="IEA TIMSS調査データに基づく期待価値理論の計量検証",
            fallback_keywords=["期待価値理論", "自己決定理論", "実用性認識", "好意度", "TIMSS"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].fallback_background,
            fallback_objectives="本研究の目的は，TIMSSデータに基づき，数学学習の実用性認識と好意度の乖離構造を計量的に解明することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].fallback_questions_to_authors,
            title_en="Gender Differences in Japanese Mathematics Achievement in TIMSS, 1995-2023",
            source_en=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].metrics_en,
            fallback_keywords_en=["EXPECTANCY-VALUE THEORY", "INTRINSIC MOTIVATION", "UTILITY VALUE", "MATHEMATICS", "TIMSS"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].fallback_summary_en,
            angle_id="timss_gender_gap",
            angle_name="日本の算数・数学の得点の男女差の推移（TIMSS）",
            title_theme="算数・数学の得点に男女の差はあるのか：TIMSSの公表値で日本の30年を見る",
            focus_metrics=['男女得点差', '男子平均得点', '女子平均得点'],
        rq1='日本の小学校4年と中学校2年で、男子と女子の平均得点の差（男子−女子）は1995年から2023年にかけてどう推移したか。',
        rq2='男女得点差は、学年と調査年によってどのように異なるか（標本調査の誤差を踏まえて）。',
        scatter_x_metric='男子平均得点',
        scatter_y_metric='女子平均得点',
        
        group_comparison_metric='男女得点差',
            analysis_method='two_way_anova',
            anova_dv='男女得点差',
            anova_factor_a='学年・教科',
            anova_factor_b='調査年',
        secondary_chart_type='anova_interaction',
        ),
    ],

    # 2. High School Informatics
    "japan_high_school_informatics": [
        DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"],
        DatasetAcademicContext(
            dataset_id="japan_high_school_informatics",
            academic_topic="情報免許状を持ちながら情報科を担当していない教員と，免許状のない担当者の自治体別の関係（令和4年5月1日現在）",
            theoretical_framework="Mishra & KoehlerのTPACKフレームワーク，教員の免許状と配置（指導体制）の枠組み",
            core_research_problems=(
                "文部科学省の資料によると，情報の免許状を持つ教員は全国で10,048人，そのうち情報科を担当している者は3,960人で，6,088人は情報科を担当していない．"
                "免許状のない担当者が多い自治体ほど，免許状を持ちながら担当していない者も多いのかを，自治体別の表で確かめる．"
                "表は臨時免許状・免許外教科担任が1人以上いる49自治体（都道府県・政令指定都市）の分で，0人の16自治体は載っていない．"
                "人数は実数で，自治体の高校数や教員数で割っていない（規模の大きい自治体ほど人数が多くなりうる）．原因と，令和5年4月の見込みが実現したかは，このデータからは言えない．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].banned_cliches,
            specific_prompt_guidance=(
                "公表値（令和4年5月1日現在，人数）の範囲で述べること．表は臨時免許状・免許外教科担任が1人以上いる49自治体（都道府県・政令指定都市）の分で，0人の16自治体は載っていない．"
                "人数は実数で，自治体の高校数や教員数で割っていない（規模の大きい自治体ほど人数が多くなりうる）．原因と，令和5年4月の見込みが実現したかは，このデータからは言えない．"
                "授業の質，生徒の学力，プログラミング指導の実態，共通テスト対策は，このデータにないので書かないこと．全国の合計は，臨時免許状236人，免許外教科担任560人，計796人（情報科担当教員4,756人のうち）．"
            ),
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].curated_references,
            fallback_title="高等学校「情報I」における計算論的思考育成とペーパーテスト評価の乖離に関する計量分析†",
            fallback_subtitle="大学入試共通テスト導入下におけるプログラミング実習時間の構造検証",
            fallback_keywords=["計算論的思考", "ペーパーテスト", "プログラミング実習", "情報I", "共通テスト"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].fallback_background,
            fallback_objectives="本研究の目的は，共通テスト導入下でのプログラミング実習と筆記対策の指導比率の変容を解明することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].fallback_questions_to_authors,
            title_en=(
                "Licensed but Not Teaching: Informatics Licence Holders and Teachers Without a Licence by Prefecture in Japan, May 2022"
            ),
            source_en=(
                "Ministry of Education, Culture, Sports, Science and Technology (MEXT), materials on the placement of high school informatics teachers (November 2022)"
            ),
            metrics_en={'臨時免許状': 'Teachers with a Temporary Licence in Informatics', '免許外教科担任': 'Teachers Teaching Informatics Outside Their Licensed Subject', '臨時免許状・免許外教科担任の計': 'Total of Temporary Licence and Out-of-Subject Teachers', '計の令和2年調査からの増減': 'Change in the Total from the FY2020 Survey', '令和5年4月見込み（改善計画の履行後）': 'Expected Total in April 2023 (after Improvement Plans)', '情報免許状保有で情報科を担当していない者': 'Informatics Licence Holders Not Teaching Informatics'},
            fallback_keywords_en=["COMPUTATIONAL THINKING", "AUTHENTIC ASSESSMENT", "INFORMATICS I", "PROGRAMMING EDUCATION"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].fallback_summary_en,
            angle_id="hs_info_computational_thinking",
            angle_name="免許状のない担当者と，免許状を持つが担当していない者の自治体別の関係",
            title_theme="免許を持つ人が教えていない：高校情報科の担当者の配置を自治体別に見る",
            focus_metrics=['情報免許状保有で情報科を担当していない者', '臨時免許状・免許外教科担任の計', '計の令和2年調査からの増減', '令和5年4月見込み（改善計画の履行後）'],
        rq1="情報免許状を持ちながら情報科を担当していない教員は，自治体でどれだけ偏っているか。",
        rq2="免許状のない担当者（臨時免許状・免許外教科担任）が多い自治体ほど，免許状を持つが担当していない者も多いか（自治体の規模は統制していない）。",
        scatter_x_metric="臨時免許状・免許外教科担任の計",
        scatter_y_metric="情報免許状保有で情報科を担当していない者",
        
        analysis_method="correlation",
        anova_dv=None,
        anova_factor_a=None,
        anova_factor_b=None,
        secondary_chart_type="correlation_scatter",
            no_corr_y=None,
            no_corr_x=None,
            regression_x_list=None,
            regression_y=None,
            group_comparison_metric="情報免許状保有で情報科を担当していない者",
        ),
    ],

    # 3. National Assessment Math
    "japan_national_assessment_math": [
        DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"],
        DatasetAcademicContext(
            dataset_id="japan_national_assessment_math",
            academic_topic="国語と算数・数学の平均正答率の動きの違い（全国学力・学習状況調査，令和元〜7年度）",
            theoretical_framework="Wigfield & Ecclesの期待価値理論（教科の学習に対する期待と価値の枠組み）。ただし，このデータには意識の項目はない",
            core_research_problems=(
                "小学校では国語の平均正答率が令和元年度の64.0%から令和7年度の67.0%へ緩やかに上がった一方，算数は66.7%から58.2%へ下がった．"
                "中学校では国語が73.2%から54.6%へ，数学が60.3%から48.8%へ下がった．教科ごとの動きの違いを公表値で整理する．"
                "調査は令和元年度（2019年）と令和3〜7年度（2021〜2025年）の6回で，令和2年度（2020年）は実施されなかった．"
                "出題される問題は毎年異なるため，年度間の平均正答率の高低は，学力の変化を直接示さない（年度間の変化は，別の経年変化分析調査で調べている）．"
                "6時点しかなく，教科どうしの関連は「同じ年に同じ向きに動いた」以上のことを示さず，因果は示せない．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].banned_cliches,
            specific_prompt_guidance=(
                "公表値（全国・公立の平均正答率，%）の範囲で述べること．調査は令和元年度（2019年）と令和3〜7年度（2021〜2025年）の6回で，令和2年度（2020年）は実施されなかった．"
                "出題される問題は毎年異なるため，年度間の平均正答率の高低は，学力の変化を直接示さない（年度間の変化は，別の経年変化分析調査で調べている）．"
                "6時点しかなく，教科どうしの関連は「同じ年に同じ向きに動いた」以上のことを示さず，因果は示せない．令和7年度の値は，小学校国語67.0%・算数58.2%，中学校国語54.6%・数学48.8%である．"
                "児童生徒の意識，端末の活用，学校や地域の差は，このデータにないので書かないこと．"
            ),
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].curated_references,
            fallback_title="全国学力・学習状況調査における1人1台端末活用率と算数・数学正答率の多変量連関分析†",
            fallback_subtitle="学習好意度を統制した重回帰モデルによるデジタル学習環境効果の検証",
            fallback_keywords=["全国学力調査", "端末活用率", "平均正答率", "学習好意度", "重回帰分析"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_background,
            fallback_objectives=(
                "本研究の目的は，全国学力・学習状況調査の公的データに基づき，算数・数学への好意度（勉強が好き肯定率）および1人1台端末活用率が平均正答率に及ぼす独立した寄与度を検証することである．\n\n"
                "・RQ1: 小学校算数および中学校数学における平均正答率，学習好意度，および端末活用率の経年推移と分布特性はどのようになっているか．\n"
                "・RQ2: 勉強が好き肯定率および端末活用率を説明変数とした重回帰モデルにおいて，平均正答率に対する各要因の標準化偏回帰係数（β）および説明力（R²）はどう評価されるか．"
            ),
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_questions_to_authors,
            title_en=(
                "Japanese and Mathematics Results in the National Assessment of Academic Ability, Japan, 2019-2025"
            ),
            source_en=(
                "National Institute for Educational Policy Research (NIER) and MEXT, National Assessment of Academic Ability and Learning Environment"
            ),
            metrics_en={'小学校算数の平均正答率': 'Elementary School Mathematics: Average Percentage of Correct Answers', '中学校数学の平均正答率': 'Junior High School Mathematics: Average Percentage of Correct Answers', '小学校国語の平均正答率': 'Elementary School Japanese: Average Percentage of Correct Answers', '中学校国語の平均正答率': 'Junior High School Japanese: Average Percentage of Correct Answers'},
            fallback_keywords_en=["NATIONAL ASSESSMENT", "ICT UTILIZATION", "LEARNING ATTITUDES", "MULTIPLE REGRESSION"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_summary_en,
            angle_id="national_math_reasoning_gap",
            angle_name="国語と算数・数学の平均正答率の動きの違い",
            title_theme="国語の正答率は上がり，算数・数学は下がったのか：全国学力調査の6回を教科別に見る",
            focus_metrics=['小学校国語の平均正答率', '小学校算数の平均正答率', '中学校国語の平均正答率', '中学校数学の平均正答率'],
            rq1="小学校の国語と算数，中学校の国語と数学の平均正答率は，令和元年度から令和7年度にかけて，教科ごとにどう違う動きをしたか。",
            rq2="小学校の国語の平均正答率と算数の平均正答率は，同じ年に同じ向きに動いたか（6時点の全国値の関連として）。",
            scatter_x_metric="小学校国語の平均正答率",
            scatter_y_metric="小学校算数の平均正答率",
            
            analysis_method="correlation",
            regression_y=None,
            regression_x_list=None,
            secondary_chart_type="correlation_scatter",
            group_comparison_metric=None,
            no_corr_y=None,
            no_corr_x=None,
            anova_factor_b=None,
            anova_factor_a=None,
            anova_dv=None,
        ),
    ],

    # 4. MEXT ICT Informatization
    "japan_mext_ict_informatization": [
        DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"],
        DatasetAcademicContext(
            dataset_id="japan_mext_ict_informatization",
            academic_topic="デジタル教科書（指導者用・学習者用）と統合型校務支援システムの整備率の推移（全国，平成31年3月〜令和6年3月）",
            theoretical_framework="ロジャーズのイノベーション普及理論 (Diffusion of Innovations)",
            core_research_problems=(
                "指導者用デジタル教科書，学習者用デジタル教科書，統合型校務支援システム，教員の指導用コンピュータの整備率が，6時点でどう推移したかを整理する．"
                "学習者用デジタル教科書の整備率が，調査を始めた令和2年から令和4年までは低く，令和5年に大きく上がったことを公表値で確かめ，他の整備率の推移と比べる．"
                "時点は平成31年（2019年）から令和6年（2024年）の各3月1日現在の6時点だけで，指標によっては調査を始めた年が遅く，時点が5つ以下になる．"
                "指標どうしの関連は「同じ時期に伸びた」以上のことを示さず，因果は示せない．整備率は，授業での活用の頻度や質を表さない．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].banned_cliches,
            specific_prompt_guidance=(
                "公表値（各年3月1日現在，全国，全学校種）の範囲で，整備の推移を述べること．時点は平成31年（2019年）から令和6年（2024年）の各3月1日現在の6時点だけで，指標によっては調査を始めた年が遅く，時点が5つ以下になる．"
                "指標どうしの関連は「同じ時期に伸びた」以上のことを示さず，因果は示せない．整備率は，授業での活用の頻度や質を表さない．"
                "教員のICT活用指導力，授業での利用頻度，学力への影響は，このデータにないので書かないこと．欠測の指標は，調査を始めた年からの推移として述べること．"
            ),
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].curated_references,
            fallback_title="学校教育情報化における義務教育段階から高等学校への進捗波及構造に関する重回帰分析†",
            fallback_subtitle="文部科学省実態調査データに基づく校種間ICT整備・指導力の共進化検証",
            fallback_keywords=["学校教育情報化", "校種間接続", "教員ICT指導力", "高等学校", "教育DX"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_background,
            fallback_objectives=(
                "本研究の目的は，小学校および中学校における教育情報化指標の進展が高等学校段階の指標水準とどのように連動しているかを重回帰分析により検証することである．\n\n"
                "・RQ1: 小学校，中学校，および高等学校における教育情報化指標の推移と分布特性はどのようになっているか．\n"
                "・RQ2: 小学校および中学校の指標水準を説明変数とした重回帰モデルにおいて，高等学校の教育情報化水準はどの程度説明されるか．"
            ),
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_questions_to_authors,
            title_en=(
                "Trends in Digital Textbooks and School Administration Systems in Japanese Schools, March 2019 to March 2024"
            ),
            source_en=(
                "Ministry of Education, Culture, Sports, Science and Technology (MEXT), Survey on the Informatization of Education in Schools (FY2023 results)"
            ),
            metrics_en={'学習者用コンピュータ台数': 'Number of Learner Computers', '児童生徒数': 'Number of Pupils and Students', '児童生徒1人あたり学習者用コンピュータ台数': 'Learner Computers per Pupil', '普通教室の無線LAN整備率': 'Wireless LAN Coverage of Ordinary Classrooms (%)', '無線LANまたはLTE等で接続できる普通教室の割合': 'Ordinary Classrooms Connected by Wireless LAN or LTE (%)', 'インターネット接続率（1Gbps以上）': 'Schools with Internet Connection of 1 Gbps or More (%)', '普通教室の大型提示装置整備率': 'Large Display Devices in Ordinary Classrooms (%)', '教員の校務用コンピュータ整備率': 'Administrative Computers per Teacher (%)', '教員の指導用コンピュータ整備率': 'Instructional Computers per Teacher (%)', '統合型校務支援システム整備率': 'Schools with Integrated School Administration Systems (%)', '指導者用デジタル教科書整備率': 'Schools with Digital Textbooks for Teachers (%)', '学習者用デジタル教科書整備率': 'Schools with Digital Textbooks for Learners (%)'},
            fallback_keywords_en=["SCHOOL INFORMATIZATION", "EDUCATIONAL DX", "TEACHING COMPETENCE", "CROSS-STAGE SPILLOVER"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_summary_en,
            angle_id="mext_ict_cloud_utilization",
            angle_name="デジタル教科書と校務支援システムの整備の推移",
            title_theme="デジタル教科書の整備は，いつ，どれだけ進んだのか：指導者用と学習者用を全国の6時点で比べる",
            focus_metrics=['指導者用デジタル教科書整備率', '学習者用デジタル教科書整備率', '統合型校務支援システム整備率', '教員の指導用コンピュータ整備率'],
            rq1="指導者用・学習者用のデジタル教科書と統合型校務支援システムの整備率は，どのように推移したか。",
            rq2="学習者用デジタル教科書の整備率の推移は，指導者用デジタル教科書の整備率の推移と，どのような関係にあるか（5時点以下の全国値の関連として）。",
            group_comparison_metric=None,
            
            analysis_method="correlation",
            regression_y=None,
            regression_x_list=None,
            secondary_chart_type="correlation_scatter",
            no_corr_y=None,
            no_corr_x=None,
            anova_factor_b=None,
            anova_factor_a=None,
            anova_dv=None,
            scatter_y_metric="学習者用デジタル教科書整備率",
            scatter_x_metric="指導者用デジタル教科書整備率",
        ),
    ],

    # 5. OECD PISA Math ICT
    "oecd_pisa_math_ict": [
        DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"],
        DatasetAcademicContext(
            dataset_id="oecd_pisa_math_ict",
            academic_topic="PISAの数学の平均得点の水準と男女得点差の関連（2015〜2025年）",
            theoretical_framework="Spencerのステレオタイプ脅威理論 (Stereotype Threat)，Hydeのジェンダー類似性仮説 (Gender Similarities Hypothesis)，比較教育制度論",
            core_research_problems=(
                "国家全体の数学的リテラシー平均得点（数学得点）が高い教育システムほど男女得点差も自然に縮小するのか，"
                "あるいは全体的な学力到達水準と男女間のジェンダー・ギャップ（男女得点差）は統計的に独立した別個の制度的次元であるのかをベイズ無相関検定（BF₀₁）により解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].banned_cliches,
            specific_prompt_guidance="数学の平均得点の水準と男女得点差（男子−女子）の関連を，分析結果の相関係数・信頼区間・ベイズファクターが示す範囲で述べること．観測は7か国とOECD平均の4時点で，国と年の組み合わせは独立ではない．観測数の32は「国・地域×調査年」の組み合わせの数で，国の数ではない．関連の有無を断定せず，因果は述べないこと．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].curated_references,
            fallback_title="OECD PISAにおける数学的リテラシー到達水準と男女得点差の統計的独立性に関するベイズ検証†",
            fallback_subtitle="主要国時系列データに基づく全体学力水準とジェンダー・ギャップの無相関分析",
            fallback_keywords=["OECD PISA", "男女得点差", "ジェンダー類似性仮説", "無相関分析", "ベイズファクター"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_background,
            fallback_objectives=(
                "本研究の目的は，PISA調査における各国の数学的リテラシー全体得点（数学得点）と男女得点差の統計的独立性（無相関仮説H₀）をベイズファクター（BF₀₁）により検証することである．\n\n"
                "・RQ1: 各国の数学得点，男子得点，女子得点，および男女得点差の国際的分布水準にはどのような格差パターンが存在するか．\n"
                "・RQ2: 各国の全体的な数学到達水準（数学得点）と男女得点差との間には線形相関が存在するか，それとも両者は統計的に独立（無相関）であるか．"
            ),
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_questions_to_authors,
            title_en="Association Between Mean Mathematics Performance and the Gender Gap in OECD PISA, 2015-2025",
            source_en=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].metrics_en,
            fallback_keywords_en=["OECD PISA", "GENDER SCORE GAP", "BAYESIAN NULL HYPOTHESIS", "MATHEMATICS LITERACY"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_summary_en,
            angle_id="pisa_socioeconomic_gradient",
            angle_name="PISAの数学の平均得点の水準と男女得点差の関連",
            title_theme="得点の高い国ほど男女差は小さいのか：PISAの公表値で確かめる",
            focus_metrics=['数学得点', '男子得点', '女子得点', '男女得点差'],
            rq1='各国の男子得点、女子得点、および男女得点差の国際的分布水準にはどのような格差パターンが存在するか。',
            rq2='国家全体の数学的リテラシー到達水準（数学得点）と男女得点差との間には統計的独立性（無相関）が認められるか。',
            scatter_x_metric='数学得点',
            scatter_y_metric='男女得点差',
            
            analysis_method='no_correlation',
            no_corr_x='数学得点',
            no_corr_y='男女得点差',
            secondary_chart_type='no_correlation_scatter',
        ),
    ],

    # 6. UNESCO World ICT Skills
    "unesco_world_ict_skills": [
        DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"],
        DatasetAcademicContext(
            dataset_id="unesco_world_ict_skills",
            academic_topic="成人のICTスキルの男女差（表計算の算術式・プレゼン資料作成）の国際比較（2021年）：日本の位置",
            theoretical_framework="Ragneddaのデジタル資本論 (Digital Capital)，van Dijkのデジタル格差論 (Digital Divide)",
            core_research_problems=(
                "UNESCO統計研究所のデータで，表計算ソフトで基本的な算術式を使った人と，プレゼン資料を作成した人の割合の，男性と女性の差（男性−女性，%ポイント）が，国・地域でどう違い，日本がどこに位置するかを整理する．"
                "日本は，表計算で男性59.3%・女性43.0%（差16.3ポイント），プレゼン資料作成で男性41.3%・女性26.3%（差15.0ポイント）である．"
                "元の統計は国によって調査の設計や対象年齢の範囲が異なり，自己申告である．47の国・地域は欧州・中東・中南米・アジアが中心で，アフリカやオセアニアの国は少ない．"
                "プログラミングの男女別は日本の値がない．国・地域のあいだの関連は，国どうしの違いを示すだけで，個人の因果を示さない．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].banned_cliches,
            specific_prompt_guidance=(
                "公表値（%，2021年）の範囲で述べること．元の統計は国によって調査の設計や対象年齢の範囲が異なり，自己申告である．"
                "47の国・地域は欧州・中東・中南米・アジアが中心で，アフリカやオセアニアの国は少ない．プログラミングの男女別は日本の値がない．"
                "国・地域のあいだの関連は，国どうしの違いを示すだけで，個人の因果を示さない．日本の値は，プログラミング5.6%，表計算50.9%，プレゼン資料作成33.5%である．"
                "学校の授業やカリキュラム，生徒（児童）のスキルは，このデータにないので書かないこと（対象は若者・成人）．"
            ),
            curated_references=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].curated_references,
            fallback_title="UNESCO/ITU国際指標における汎用オフィススキルとプログラミング能力の階層構造に関する重回帰分析†",
            fallback_subtitle="SDG 4.4.1に基づく表計算・プレゼン作成スキルからアルゴリズム構築への認知的跳躍の検証",
            fallback_keywords=["UNESCO", "プログラミングスキル", "表計算高度利用", "SDG 4.4.1", "計算論的思考"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_background,
            fallback_objectives=(
                "本研究の目的は，UNESCO/ITU国際統計データに基づき，表計算高度利用率およびプレゼン作成スキル保有率がプログラミングスキル保有率をどの程度説明し得るかを重回帰分析によって検証することである．\n\n"
                "・RQ1: 対象15カ国におけるプレゼン作成スキル保有率，表計算高度利用率，およびプログラミングスキル保有率の分布水準にはどのような階層差が存在するか．\n"
                "・RQ2: 表計算高度利用率とプレゼン作成スキル保有率を説明変数とした重回帰モデルにおいて，プログラミングスキル保有率に対するそれぞれの独立した寄与度（β）はどう評価されるか．"
            ),
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_questions_to_authors,
            title_en=(
                "Gender Gaps in Adult ICT Skills Across Countries and Territories in 2021: Spreadsheets and Presentations"
            ),
            source_en="UNESCO Institute for Statistics (SDG 4.4.1 data, compiled from ITU statistics), 2021",
            metrics_en={'プログラミングをした人の割合': 'Adults Who Programmed or Coded (%)', 'プログラミングをした女性の割合': 'Women Who Programmed or Coded (%)', 'プログラミングをした男性の割合': 'Men Who Programmed or Coded (%)', '表計算ソフトで基本的な算術式を使った人の割合': 'Adults Who Used a Basic Arithmetic Formula in a Spreadsheet (%)', '表計算で算術式を使った女性の割合': 'Women Who Used a Basic Arithmetic Formula in a Spreadsheet (%)', '表計算で算術式を使った男性の割合': 'Men Who Used a Basic Arithmetic Formula in a Spreadsheet (%)', 'プレゼンテーション資料を作成した人の割合': 'Adults Who Created Electronic Presentations (%)', 'プレゼン資料を作成した女性の割合': 'Women Who Created Electronic Presentations (%)', 'プレゼン資料を作成した男性の割合': 'Men Who Created Electronic Presentations (%)', '表計算の男女差（男性−女性，%ポイント）': 'Gender Gap in Spreadsheet Use (Men minus Women, percentage points)', 'プレゼン資料作成の男女差（男性−女性，%ポイント）': 'Gender Gap in Creating Presentations (Men minus Women, percentage points)'},
            fallback_keywords_en=["UNESCO", "COMPUTATIONAL THINKING", "PROGRAMMING SKILLS", "SDG 4.4.1", "SKILL HIERARCHY"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_summary_en,
            angle_id="unesco_gender_disparity_in_skills",
            angle_name="ICTスキルの男女差の国際比較（表計算・プレゼン資料作成）",
            title_theme="ICTスキルの男女差は，国によってどれだけ違うのか：表計算とプレゼン資料作成を，日本と他の国・地域で比べる",
            focus_metrics=['表計算の男女差（男性−女性，%ポイント）', 'プレゼン資料作成の男女差（男性−女性，%ポイント）', '表計算で算術式を使った女性の割合', '表計算で算術式を使った男性の割合'],
            rq1="表計算の算術式とプレゼン資料作成で，男性と女性の割合の差は，国・地域によってどう違い，日本はどこに位置するか。",
            rq2="表計算での男女差が大きい国・地域ほど，プレゼン資料作成での男女差も大きいか（国・地域間の関連として）。",
            scatter_x_metric="表計算の男女差（男性−女性，%ポイント）",
            scatter_y_metric="プレゼン資料作成の男女差（男性−女性，%ポイント）",
            
            analysis_method="correlation",
            regression_y=None,
            regression_x_list=None,
            secondary_chart_type="correlation_scatter",
            no_corr_y=None,
            no_corr_x=None,
            anova_factor_b=None,
            anova_factor_a=None,
            anova_dv=None,
            group_comparison_metric="表計算の男女差（男性−女性，%ポイント）",
        ),
    ],

    # 7. STEM CS Enrollment
    "japan_stem_cs_enrollment": [
        DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"],
        DatasetAcademicContext(
            dataset_id="japan_stem_cs_enrollment",
            academic_topic="大学（学部）の入学志願者の女性比率と入学者の女性比率の関係（関係学科別，令和5〜7年度）",
            theoretical_framework="社会認知的キャリア理論 (Lent, Brown & Hackett)，漏れるパイプライン (Blickenstaff)",
            core_research_problems=(
                "学校基本調査の公表値で，関係学科ごとの入学志願者の女性比率と，入学者の女性比率の関係を確かめる．志願者の段階で女性が少ない学科は，入学者でも少ないのか，志願者から入学者になる過程で女性比率が上がるか下がるかを，58区分の値で見る．"
                "対象は大学（学部）の入学者と入学志願者で，学科の区分は学校基本調査の「関係学科」の小分類（58区分，3年度すべてで入学者が200人以上のもの）である．"
                "この分類には「情報」という独立した区分がなく，情報系の学科だけを取り出すことはできない．女性比率は，入学した（志願した）人の男女比であり，進路を選んだ理由や，入試の結果の公平さは，このデータからは言えない．"
                "時点は令和5〜7年度の3つだけである．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].banned_cliches,
            specific_prompt_guidance=(
                "公表値（令和5〜7年度，大学学部）の範囲で述べること．対象は大学（学部）の入学者と入学志願者で，学科の区分は学校基本調査の「関係学科」の小分類（58区分，3年度すべてで入学者が200人以上のもの）である．"
                "この分類には「情報」という独立した区分がなく，情報系の学科だけを取り出すことはできない．女性比率は，入学した（志願した）人の男女比であり，進路を選んだ理由や，入試の結果の公平さは，このデータからは言えない．"
                "時点は令和5〜7年度の3つだけである．令和7年度の全体の女性比率は47.0%（入学者645,513人，女性303,073人）で，工学・機械工学8.2%，工学・電気通信工学12.2%，理学・物理学15.6%，理学・数学21.0%である．"
                "大学院，短期大学，教員の男女比，卒業後の進路は，このデータにないので書かないこと．"
            ),
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].curated_references,
            fallback_title="大学情報科学・工学系学部における男女別入学者数推移と高等教育定員受容容量の計量分析†",
            fallback_subtitle="学校基本調査データに基づく高度IT人材育成キャパシティの構造検証",
            fallback_keywords=["学校基本調査", "情報科学", "入学者数", "定員制約", "高等教育政策"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_background,
            fallback_objectives=(
                "本研究の目的は，情報系・理工系学科における男女別入学者数の推移と高等教育機関の受容キャパシティを計量的に検証することである．\n\n"
                "・RQ1: 情報・理工系学部における男性入学者数および女性入学者数の経年推移と分布特性はどうなっているか．\n"
                "・RQ2: 定員拡充が進む中で，男性入学者数の拡大ペースと女性入学者数の増加にはどのような連動相関が存在するか．"
            ),
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_questions_to_authors,
            title_en=(
                "Women among Applicants and Entrants to Japanese Universities by Field of Study, FY2023 to FY2025"
            ),
            source_en=(
                "Ministry of Education, Culture, Sports, Science and Technology (MEXT), School Basic Survey (FY2023 to FY2025)"
            ),
            metrics_en={'入学者数': 'Number of Entrants', '女性の入学者数': 'Number of Female Entrants', '入学者の女性比率（%）': 'Share of Women among Entrants (%)', '入学志願者の女性比率（%）': 'Share of Women among Applicants (%)'},
            fallback_keywords_en=["COMPUTER SCIENCE ENROLLMENT", "HIGHER EDUCATION CAPACITY", "HUMAN CAPITAL THEORY", "STEM PIPELINE"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_summary_en,
            angle_id="stem_capacity_and_workforce_demand",
            angle_name="入学志願者と入学者の女性比率の関係（関係学科別）",
            title_theme="志願の段階で女性が少ない学科は，入学でも少ないのか：学校基本調査で志願者と入学者を比べる",
            focus_metrics=['入学志願者の女性比率（%）', '入学者の女性比率（%）'],
            rq1="入学志願者の女性比率が高い学科ほど，入学者の女性比率も高いか（58区分の関連として）。",
            rq2="志願者の女性比率と入学者の女性比率の差は，学科の区分によってどう違うか。",
            scatter_x_metric="入学志願者の女性比率（%）",
            scatter_y_metric="入学者の女性比率（%）",
            
            analysis_method="correlation",
            secondary_chart_type="correlation_scatter",
            no_corr_y=None,
            no_corr_x=None,
            regression_x_list=None,
            regression_y=None,
            anova_factor_b=None,
            anova_factor_a=None,
            anova_dv=None,
            group_comparison_metric="入学者の女性比率（%）",
        ),
    ],

    # 8. World Bank Education Indicators
    "worldbank_education_indicators": [
        DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"],
        DatasetAcademicContext(
            dataset_id="worldbank_education_indicators",
            academic_topic="インターネット利用率と学習到達度（HLO）の国際比較（教育支出を考慮した重回帰）",
            theoretical_framework="リープフロッギング理論 (Leapfrogging Theory)，国際開発教育学，内生的経済成長モデル",
            core_research_problems=(
                "教育支出（対GDP比）を考慮しても，インターネット利用率と学習到達度（HLO）の間に関連が残るかを，"
                "16か国の横断データの重回帰分析で確かめる．国の豊かさなど他の要因は統制できず，因果は示せない．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].banned_cliches,
            specific_prompt_guidance="教育支出（対GDP比）を説明変数に加えた重回帰分析の結果の範囲で，インターネット利用率と学習到達度（HLO）の関連を述べること．HLOは数学だけの得点ではない．因果や「底上げ」などの効果は断定しないこと．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].curated_references,
            fallback_title="世界銀行データに基づくデジタルインフラ接続と数学最低習熟度の重回帰分析†",
            fallback_subtitle="公的教育支出対GDP比を統制した情報通信基盤の学習成果寄与度の検証",
            fallback_keywords=["世界銀行", "インターネット利用率", "調和済み学習到達度スコア(HLO)", "重回帰分析", "開発教育学"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_background,
            fallback_objectives=(
                "本研究の目的は，世界銀行EdStatsデータに基づき，公的教育支出対GDP比を統制した上でインターネット利用率が調和済み学習到達度スコア(HLO)に与える独立した効果を重回帰分析により解明することである．\n\n"
                "・RQ1: 対象16カ国におけるインターネット利用率，教育支出対GDP比，および調和済み学習到達度スコア(HLO)の分布水準はどうなっているか．\n"
                "・RQ2: インターネット利用率および教育支出対GDP比を説明変数とした重回帰モデルにおいて，調和済み学習到達度スコア(HLO)に対する各要因の標準化偏回帰係数（β）はどう評価されるか．"
            ),
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_questions_to_authors,
            title_en="Internet Use and Harmonized Learning Outcomes Across Countries: A Multiple Regression Using World Bank Data",
            source_en=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].metrics_en,
            fallback_keywords_en=["THE WORLD BANK", "LEAPFROGGING", "INTERNET CONNECTIVITY", "MATHEMATICS PROFICIENCY", "MULTIPLE REGRESSION"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_summary_en,
            angle_id="wb_internet_leapfrogging",
            angle_name="インターネット利用率と学習到達度（HLO）の関連（教育支出を考慮した重回帰）",
            title_theme="インターネットの普及と学習到達度に関連はあるか：世界銀行の公表データで16か国を比べる",
            focus_metrics=['インターネット利用率', '調和済み学習到達度スコア(HLO)', '教育支出対GDP比'],
            rq1='世界16カ国におけるインターネット利用率、教育支出対GDP比、および調和済み学習到達度スコア(HLO)の分布はどうなっているか。',
            rq2='教育支出対GDP比を統制した重回帰モデルにおいて、インターネット利用率は調和済み学習到達度スコア(HLO)にどの程度寄与しているか。',
            scatter_x_metric='インターネット利用率',
            scatter_y_metric='調和済み学習到達度スコア(HLO)',
            
            analysis_method='multiple_regression',
            regression_y='調和済み学習到達度スコア(HLO)',
            regression_x_list=['インターネット利用率', '教育支出対GDP比'],
            secondary_chart_type='multiple_regression',
        ),
    ],

    # 9. Teacher Workload Survey
    "japan_teacher_workload_survey": [
        DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"],
        DatasetAcademicContext(
            dataset_id="japan_teacher_workload_survey",
            academic_topic="中学校の教諭の土日の在校等時間（部活動・クラブ活動を中心に）：平成28年度と令和4年度の比較",
            theoretical_framework="職務要求度―資源モデル (Job Demands-Resources model)，学校における働き方改革（中央教育審議会，2019）の枠組み",
            core_research_problems=(
                "公表値で，中学校の教諭の土日の1日あたり在校等時間は，平成28年度の3時間22分から令和4年度の2時間18分に減った．"
                "そのうち部活動・クラブ活動は，2時間9分から1時間29分に減った．土日の業務別の増減が，平日の増減と同じ向きかを，25の業務の値で確かめる．"
                "平成28年度と令和4年度は別の標本で，時間は1分未満を切り捨てて公表されている．数分の差を過大に読まない．"
                "原因（働き方改革の効果，学校DXなど）は，この表からは断定できない．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].banned_cliches,
            specific_prompt_guidance=(
                "公表値（1日あたりの在校等時間，単位は分）の範囲で，中学校の土日の減少と部活動・クラブ活動の関係を述べること．"
                "平成28年度と令和4年度は別の標本で，時間は1分未満を切り捨てて公表されている．数分の差を過大に読まない．"
                "原因（働き方改革の効果，学校DXなど）は，この表からは断定できない．部活動の地域移行の進み具合など，このデータにない事柄は書かないこと．"
            ),
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].curated_references,
            fallback_title="公立小・中学校の校種・職階別における部活動指導負担と持ち帰り仕事時間の計量分析†",
            fallback_subtitle="教員勤務実態調査データに基づく二要因分散分析と時間外負担の検証",
            fallback_keywords=["教員勤務実態調査", "部活動指導", "持ち帰り仕事", "二要因分散分析", "地域移行"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_background,
            fallback_objectives=(
                "本研究の目的は，校種・職階および調査年を要因とする二要因分散分析により，部活動指導時間および持ち帰り仕事時間の構造的格差を検証することである．\n\n"
                "・RQ1: 校種・職階別における部活動指導時間および持ち帰り仕事時間の分布水準はどう推移しているか．\n"
                "・RQ2: 校種・職階要因および調査年要因は部活動指導負担にどのような統計的主効果をもたらしているか．"
            ),
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_questions_to_authors,
            title_en="Weekend Working Hours of Japanese Junior High School Teachers by Duty, FY2016 and FY2022",
            source_en=(
                "Ministry of Education, Culture, Sports, Science and Technology (MEXT), Teacher Working Conditions Survey (FY2022, final results)"
            ),
            metrics_en={'平日・小学校・平成28年度': 'Weekday, Elementary, FY2016 (min/day)', '平日・小学校・令和4年度': 'Weekday, Elementary, FY2022 (min/day)', '平日・小学校・増減': 'Weekday, Elementary, Change FY2016 to FY2022 (min/day)', '平日・中学校・平成28年度': 'Weekday, Junior High, FY2016 (min/day)', '平日・中学校・令和4年度': 'Weekday, Junior High, FY2022 (min/day)', '平日・中学校・増減': 'Weekday, Junior High, Change FY2016 to FY2022 (min/day)', '土日・中学校・平成28年度': 'Weekend, Junior High, FY2016 (min/day)', '土日・中学校・令和4年度': 'Weekend, Junior High, FY2022 (min/day)', '土日・中学校・増減': 'Weekend, Junior High, Change FY2016 to FY2022 (min/day)'},
            fallback_keywords_en=["TEACHER WORKLOAD", "EXTRACURRICULAR GUIDANCE", "TAKE-HOME WORK", "TWO-WAY ANOVA", "WELLBEING"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_summary_en,
            angle_id="workload_extracurricular_burden",
            angle_name="中学校の教諭の土日の在校等時間の変化（部活動・クラブ活動を中心に）",
            title_theme="中学校の先生の土日は，どれだけ減ったのか：部活動を中心に勤務実態調査の公表値を読む",
            focus_metrics=['土日・中学校・平成28年度', '土日・中学校・令和4年度', '土日・中学校・増減', '平日・中学校・増減'],
            rq1="中学校の教諭の土日の1日あたり在校等時間は，業務別にどれだけ変わったか。部活動・クラブ活動はその変化のどれだけを占めるか。",
            rq2="土日の業務別の増減は，平日の業務別の増減と関連しているか。",
            scatter_x_metric="平日・中学校・増減",
            scatter_y_metric="土日・中学校・増減",
            
            analysis_method="correlation",
            anova_dv=None,
            anova_factor_a=None,
            anova_factor_b=None,
            secondary_chart_type="correlation_scatter",
            no_corr_y=None,
            no_corr_x=None,
            regression_x_list=None,
            regression_y=None,
            group_comparison_metric="土日・中学校・増減",
        ),
    ],

    # 10. Special Needs Education
    "japan_special_needs_education": [
        DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"],
        DatasetAcademicContext(
            dataset_id="japan_special_needs_education",
            academic_topic="高等学校で通級による指導を受けている生徒数の推移（平成30〜令和4年度）と，小学校・中学校との比較",
            theoretical_framework="Ainscowのインクルーシブ教育の枠組み，Florian & Black-Hawkinsのインクルーシブ・ペダゴジー",
            core_research_problems=(
                "高等学校の通級による指導は，公表値が平成30年度（508人）から令和4年度（2,055人）まで5時点ある．"
                "この増え方が，同じ期間の小学校・中学校の増え方と比べてどう違うかを整理する．年度は平成5年度，10年度，15〜30年度，令和元〜4年度の22時点で，間隔は不均一である．"
                "高等学校の値は平成30年度から公表されている．令和4年度の調査は，令和6年の能登半島沖地震の影響で，石川県の公立・私立学校に対して実施していない．"
                "人数の増加の原因（制度の変更，認知の広がり，対象の拡大など）や，どの障害の種類が増えたかは，このデータからは言えない．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].banned_cliches,
            specific_prompt_guidance=(
                "公表値（通級による指導を受けている児童生徒数，国公私立計）の範囲で，推移を述べること．年度は平成5年度，10年度，15〜30年度，令和元〜4年度の22時点で，間隔は不均一である．"
                "高等学校の値は平成30年度から公表されている．令和4年度の調査は，令和6年の能登半島沖地震の影響で，石川県の公立・私立学校に対して実施していない．"
                "人数の増加の原因（制度の変更，認知の広がり，対象の拡大など）や，どの障害の種類が増えたかは，このデータからは言えない．"
                "特別支援学級の在籍者数，支援員の配置，端末の活用は，このデータにないので書かないこと．令和4年度の総数は198,343人で，前年度より14,464人増えた．"
            ),
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].curated_references,
            fallback_title="特別支援教育支援員の配置動態と通常学級におけるユニバーサルデザイン支援の実証分析†",
            fallback_subtitle="文部科学省実態調査データに基づく人的支援リソース配分の検証",
            fallback_keywords=["特別支援教育支援員", "ユニバーサルデザイン", "通常学級", "リソース配分", "インクルーシブ教育"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_background,
            fallback_objectives=(
                "本研究の目的は，特別支援教育支援員配置数および特別支援学級在籍数の推移と通級指導児童生徒数との連動を重回帰分析により検証することである．\n\n"
                "・RQ1: 特別支援学級在籍数，通級指導児童生徒数，および特別支援教育支援員数の推移はどうなっているか．\n"
                "・RQ2: 特別支援学級在籍数および特別支援教育支援員数を説明変数とした重回帰モデルにおいて，通級指導児童生徒数の増加はどう説明されるか．"
            ),
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_questions_to_authors,
            title_en=(
                "Resource-Room Instruction in High Schools Compared with Elementary and Junior High Schools in Japan, FY2018 to FY2022"
            ),
            source_en=(
                "Ministry of Education, Culture, Sports, Science and Technology (MEXT), Survey on the Implementation of Resource-Room Instruction (FY2022)"
            ),
            metrics_en={'小学校の通級指導児童生徒数': 'Elementary School Pupils Receiving Resource-Room Instruction', '中学校の通級指導児童生徒数': 'Junior High School Students Receiving Resource-Room Instruction', '高等学校の通級指導児童生徒数': 'High School Students Receiving Resource-Room Instruction', '全体の通級指導児童生徒数（総数）': 'All Pupils and Students Receiving Resource-Room Instruction (Total)'},
            fallback_keywords_en=["SPECIAL SUPPORT AIDES", "UNIVERSAL DESIGN", "RESOURCE ALLOCATION", "INCLUSIVE EDUCATION"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_summary_en,
            angle_id="special_needs_support_staff_allocation",
            angle_name="高等学校の通級による指導の増加と，小学校・中学校との比較",
            title_theme="高校の通級指導は，始まって5年でどう増えたのか：小学校・中学校と比べる",
            focus_metrics=['高等学校の通級指導児童生徒数', '中学校の通級指導児童生徒数', '小学校の通級指導児童生徒数', '全体の通級指導児童生徒数（総数）'],
            rq1="高等学校で通級による指導を受けている生徒数は，平成30年度から令和4年度にかけてどう増えたか。",
            rq2="高等学校の増加は，同じ期間の中学校の増加と比べて，どのような関係にあるか（5時点の全国値の関連として）。",
            scatter_x_metric="中学校の通級指導児童生徒数",
            scatter_y_metric="高等学校の通級指導児童生徒数",
            
            analysis_method="correlation",
            regression_y=None,
            regression_x_list=None,
            secondary_chart_type="correlation_scatter",
            group_comparison_metric=None,
            no_corr_y=None,
            no_corr_x=None,
            anova_factor_b=None,
            anova_factor_a=None,
            anova_dv=None,
        ),
    ],

    # 11. School Absenteeism & Bullying
    "japan_school_absenteeism_bullying": [
        DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"],
        DatasetAcademicContext(
            dataset_id="japan_school_absenteeism_bullying",
            academic_topic="小中接続期（中1ギャップ）における不登校率の急上昇動態と学校適応ストレス構造",
            theoretical_framework="Ecclesのステージ・エンバイロメント・フィット理論 (Stage-Environment Fit Theory)，生徒指導体制論",
            core_research_problems=(
                "小学校から中学校への移行に伴い不登校率が3倍以上に跳ね上がる「中1ギャップ」のメカニズムを，"
                "学校種要因と年度要因の二要因分散分析（ANOVA）に基づき計量的に解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].banned_cliches,
            specific_prompt_guidance="小学校から中学校への学校種移行（中1ギャップ）における千人あたり不登校率の急増と二要因分散分析結果に焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].curated_references,
            fallback_title="小・中学校学校種移行期における不登校率急増動態の二要因分散分析†",
            fallback_subtitle="生徒指導諸課題調査データに見る中1ギャップと学習環境適合の検証",
            fallback_keywords=["中1ギャップ", "不登校率", "ステージ・エンバイロメント・フィット", "二要因分散分析", "生徒指導"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].fallback_background,
            fallback_objectives=(
                "本研究の目的は，小・中学校の千人あたり不登校率推移における学校種差および年度効果を二要因分散分析により検証することである．\n\n"
                "・RQ1: 小学校と中学校の間における千人あたり不登校率の水準差および経年拡大傾向はどのように推移しているか．\n"
                "・RQ2: 学校種要因（小学校・中学校）および年度要因は千人あたり不登校率にどのような主効果および交互作用をもたらしているか．"
            ),
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].fallback_questions_to_authors,
            title_en="Lower Secondary Transition Gap in School Absenteeism: A Stage-Environment Fit Analysis",
            source_en=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].metrics_en,
            fallback_keywords_en=["TRANSITION GAP", "SCHOOL ABSENTEEISM", "STAGE-ENVIRONMENT FIT", "STUDENT GUIDANCE"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].fallback_summary_en,
            angle_id="absenteeism_school_transition_gap",
            angle_name="小学校から中学校への学校種移行期（中1ギャップ）における不登校率急上昇",
            title_theme="なぜ中学校で不登校が3倍に跳ね上がるのか？：問題行動・不登校調査データが暴く中1ギャップの構造",
            focus_metrics=['千人あたり不登校率', '不登校児童生徒数'],
            rq1='小学校と中学校の間における千人あたり不登校率の水準差および経年拡大傾向はどのように推移しているか。',
            rq2='学校段階の移行（中1ギャップ）と年度推移は千人あたり不登校率にどのような二要因分散分析効果（主効果・交互作用）を示しているか。',
            group_comparison_metric='千人あたり不登校率',
            
            analysis_method='two_way_anova',
            anova_dv='千人あたり不登校率',
            anova_factor_a='学校種',
            anova_factor_b='年度',
            secondary_chart_type='anova_interaction',
        ),
    ],

    # 12. OECD TALIS Teacher Survey
    "oecd_talis_teacher_survey": [
        DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"],
        DatasetAcademicContext(
            dataset_id="oecd_talis_teacher_survey",
            academic_topic="批判的思考を要する課題と，明確な解のない課題を出す教員の割合の国際比較（TALIS 2024）：日本の位置",
            theoretical_framework="OECDのTALIS（国際教員指導環境調査）の枠組み。教員の指導実践（認知的活性化）を，教員の自己申告で測る",
            core_research_problems=(
                "TALIS 2024の公表表で，批判的思考を要する課題を出す，明確な解のない課題を出す，少人数グループで共同の解決を求める，という指導実践を「頻繁に」または「いつも」行う教員の割合が，国・地域でどう違い，日本がどこに位置するかを整理する．"
                "日本は，批判的思考を要する課題を出す教員が24.2%（OECD平均61.2%），明確な解のない課題を出す教員が28.7%（37.1%），少人数グループで共同の解決を求める教員が53.2%（51.2%）である．"
                "TALISは教員の自己申告の調査で，言葉の受け取り方や文化の違いが回答に影響しうるため，国際比較は慎重に解釈する（OECDの注意）．"
                "対象は前期中等教育（日本は中学校）の教員で，54の国・地域（オランダ・ニュージーランド・ノルウェー・アルバータ州は，無回答による偏りの危険が高いとOECDが注意している）．"
                "国・地域のあいだの関連は，国どうしの違いを示すだけで，個々の教員の行動の因果を示さない．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].banned_cliches,
            specific_prompt_guidance=(
                "公表値（%，2024年）の範囲で述べること．TALISは教員の自己申告の調査で，言葉の受け取り方や文化の違いが回答に影響しうるため，国際比較は慎重に解釈する（OECDの注意）．"
                "対象は前期中等教育（日本は中学校）の教員で，54の国・地域（オランダ・ニュージーランド・ノルウェー・アルバータ州は，無回答による偏りの危険が高いとOECDが注意している）．"
                "国・地域のあいだの関連は，国どうしの違いを示すだけで，個々の教員の行動の因果を示さない．日本の値は，批判的思考を要する課題を出す教員が24.2%（OECD平均61.2%），AIを仕事で使った教員が17.4%（OECD平均36.3%）である．"
                "授業の質，生徒の学力，教員の勤務時間は，この表にないので書かないこと．"
            ),
            curated_references=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].curated_references,
            fallback_title="批判的思考を育成する授業実践と教員自己効力感の国際比較に関する計量分析†",
            fallback_subtitle="OECD TALIS調査データに基づく高次思考指導の構造検証",
            fallback_keywords=["OECD TALIS", "批判的思考", "教員自己効力感", "高次思考スキル", "探究型学習"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].fallback_background,
            fallback_objectives="本研究の目的は，TALISデータにおける批判的思考育成指導の国際的位置づけと要因を検証することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].fallback_questions_to_authors,
            title_en="Critical-Thinking Tasks in Lower Secondary Classrooms: Japan in the TALIS 2024 Comparison",
            source_en="OECD, Results from TALIS 2024: The State of Teaching (2025)",
            metrics_en={'批判的思考を要する課題を出す教員の割合': 'Teachers Frequently Giving Tasks that Require Critical Thinking (%)', '明確な解のない課題を出す教員の割合': 'Teachers Frequently Presenting Tasks with No Obvious Solution (%)', '少人数グループで共同の解決を求める教員の割合': 'Teachers Frequently Having Students Work in Small Groups on a Joint Solution (%)', '学習の計画・管理にデジタル資源を使わせる教員の割合': 'Teachers Frequently Using Digital Resources for Students to Plan and Monitor Learning (%)', 'デジタル資源で生徒どうしの協働を支える教員の割合': 'Teachers Frequently Using Digital Resources to Support Student Collaboration (%)', 'デジタル資源で学習を支えられる自信のある教員の割合': 'Teachers Confident in Supporting Learning with Digital Resources (%)', 'AIを仕事で使った教員の割合': 'Teachers Who Used AI in Their Work (%)'},
            fallback_keywords_en=["OECD TALIS", "CRITICAL THINKING", "TEACHER SELF-EFFICACY", "HIGHER-ORDER THINKING"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].fallback_summary_en,
            angle_id="talis_critical_thinking_instruction",
            angle_name="批判的思考を要する課題を出す教員の割合の国際比較（日本の位置）",
            title_theme="日本の中学校では，考えさせる課題がどれだけ出されているのか：TALIS 2024で54の国・地域と比べる",
            focus_metrics=['批判的思考を要する課題を出す教員の割合', '明確な解のない課題を出す教員の割合', '少人数グループで共同の解決を求める教員の割合'],
        rq1="批判的思考を要する課題・明確な解のない課題・少人数での共同の解決を求める教員の割合は，国・地域でどう違い，日本はどこに位置するか。",
        rq2="批判的思考を要する課題を出す教員の割合は，明確な解のない課題を出す教員の割合と関連しているか（国・地域間の関連として）。",
        scatter_x_metric="明確な解のない課題を出す教員の割合",
        scatter_y_metric="批判的思考を要する課題を出す教員の割合",
        
        analysis_method="correlation",
        regression_y=None,
        regression_x_list=None,
        secondary_chart_type="correlation_scatter",
            no_corr_y=None,
            no_corr_x=None,
            anova_factor_b=None,
            anova_factor_a=None,
            anova_dv=None,
            group_comparison_metric="批判的思考を要する課題を出す教員の割合",
        ),
    ],
}
# ---------------------------------------------------------------------------
# 13. TIMSS 2023 student attitudes (added 2026-10-06; built from IEA's exhibits, see tools/build_timss_attitudes_catalog.py)
# ---------------------------------------------------------------------------
_TA_G = {4: "小4", 8: "中2"}
_TA_L4_LIKE, _TA_L4_NOLIKE, _TA_L4_LGAP = "小4・とても好き(%)", "小4・好きでない(%)", "小4・好き層と好きでない層の得点差"
_TA_L4_CONF, _TA_L4_NOCONF, _TA_L4_CGAP = "小4・とても自信あり(%)", "小4・自信なし(%)", "小4・自信あり層と自信なし層の得点差"
_TA_L4_MEAN = "小4・平均得点"
_TA_L8_LIKE, _TA_L8_NOLIKE, _TA_L8_LGAP = "中2・とても好き(%)", "中2・好きでない(%)", "中2・好き層と好きでない層の得点差"
_TA_L8_CONF, _TA_L8_NOCONF, _TA_L8_CGAP = "中2・とても自信あり(%)", "中2・自信なし(%)", "中2・自信あり層と自信なし層の得点差"
_TA_L8_VAL, _TA_L8_NOVAL, _TA_L8_VGAP = "中2・とても価値ありと考える(%)", "中2・価値を感じない(%)", "中2・価値あり層と価値なし層の得点差"
_TA_L8_MEAN = "中2・平均得点"
_TA_CAVEAT = (
    "対象は小4（58の国・地域）と中2（43の国・地域）で，価値の尺度は中2だけにある．小4と中2は別の列で，学年をまたいで混ぜていない．"
    "意識は児童生徒の自己申告で，国によって回答の傾向が違う．国・地域のあいだの関連は，国どうしの違いを示すだけで，個々の児童生徒の因果を示さない．"
    "群の平均得点の差は，意識が得点を高めることを意味しない．"
)
_TA_METRICS_EN = {}
for _g, _ge in (("小4", "Grade 4"), ("中2", "Grade 8")):
    _TA_METRICS_EN.update({
        f"{_g}・とても好き(%)": f"{_ge}: Students Who Very Much Like Learning Mathematics (%)",
        f"{_g}・好きでない(%)": f"{_ge}: Students Who Do Not Like Learning Mathematics (%)",
        f"{_g}・好き層と好きでない層の得点差": f"{_ge}: Achievement Gap between Students Who Like and Do Not Like Mathematics",
        f"{_g}・とても自信あり(%)": f"{_ge}: Students Who Are Very Confident in Mathematics (%)",
        f"{_g}・自信なし(%)": f"{_ge}: Students Who Are Not Confident in Mathematics (%)",
        f"{_g}・自信あり層と自信なし層の得点差": f"{_ge}: Achievement Gap between Confident and Not Confident Students",
        f"{_g}・平均得点": f"{_ge}: Average Mathematics Achievement of the Country or Territory",
    })
_TA_METRICS_EN.update({
    _TA_L8_VAL: "Grade 8: Students Who Strongly Value Mathematics (%)",
    _TA_L8_NOVAL: "Grade 8: Students Who Do Not Value Mathematics (%)",
    _TA_L8_VGAP: "Grade 8: Achievement Gap between Students Who Value and Do Not Value Mathematics",
})
_TA_REFS = [
    "IEA (2024) TIMSS 2023 International Results in Mathematics and Science. Boston College, TIMSS & PIRLS International Study Center.",
    "BANDURA, A. (1997) Self-efficacy: The exercise of control. W. H. Freeman and Company.",
    "MULLIS, I. V. S., MARTIN, M. O., FOY, P., KELLY, D. L. and FISHBEIN, B. (2020) TIMSS 2019 International Results in Mathematics and Science. Boston College, TIMSS & PIRLS International Study Center.",
    "PEKRUN, R. (2006) The control-value theory of achievement emotions: Assumptions, corollaries, and implications for educational research and practice. Educational Psychology Review, <b>18</b> (4) ：315-341.",
    "WIGFIELD, A. and ECCLES, J. S. (2000) Expectancy-value theory of achievement motivation. Contemporary Educational Psychology, <b>25</b> (1) ：68-81.",
]
_TA_BANNED = [
    "近年のSociety 5.0の進展に伴い",
    "近年，Society 5.0の進展に伴い",
    "現代社会において急速に進展するDXに伴い",
    "情報化社会の急速な進展に伴い",
]
_TA_GUIDE = (
    "公表値（%，2023年）の範囲で述べること．" + _TA_CAVEAT +
    "日本は，小4で算数が「とても好き」22%・「好きでない」42%（平均得点591），中2で数学が「とても好き」10%・「好きでない」59%（平均得点595）である．"
    "授業の方法，学習時間，家庭の状況，過去の調査との比較は，このデータにないので書かないこと．"
)

DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"] = DatasetAcademicContext(
    dataset_id="timss2023_student_attitudes",
    academic_topic="算数・数学の「好き」「自信」「価値」と得点の国際比較（TIMSS 2023，小4・中2）：日本の位置",
    theoretical_framework="Wigfield & Ecclesの期待価値理論，Banduraの自己効力感理論，Pekrunの統制価値理論（達成感情）",
    core_research_problems=(
        "TIMSS 2023で，算数・数学を「とても好き」「とても自信がある」と答えた児童生徒の割合が国・地域によってどう違うか，国の平均得点とどう関連するかを整理する．"
        "日本は得点が高い（小4が591，中2が595）一方，「とても好き」な児童生徒の割合は小4で22%，中2で10%と，国際平均（小4は44%）より低い．" + _TA_CAVEAT
    ),
    banned_cliches=_TA_BANNED,
    specific_prompt_guidance=_TA_GUIDE,
    curated_references=_TA_REFS,
    fallback_title="TIMSS 2023における算数・数学の好き・自信と得点の国際比較†",
    fallback_subtitle="日本の児童生徒の位置づけ",
    fallback_keywords=["TIMSS 2023", "算数・数学", "好き", "自信", "国際比較"],
    fallback_background=(
        "国際数学・理科教育動向調査（TIMSS）は，児童生徒の得点とあわせて，算数・数学への意識を質問紙で尋ねている．"
        "TIMSS 2023（IEA, 2024）では，「好き」「自信」「価値」の3つの尺度で，児童生徒が3群に分けられ，群ごとの割合と平均得点が公表された．"
        "期待価値理論（Wigfield & Eccles, 2000）は，課題への期待と価値が学習への動機を支えると説明し，自己効力感理論（Bandura, 1997）は，"
        "自分にできるという信念が行動を左右すると説明する．Pekrun (2006) の統制価値理論は，統制の感覚と価値の認識が学習の感情を決めるとする．"
        "TIMSS 2019の報告（Mullis et al., 2020）も，同様の質問紙の尺度の結果を公表している．"
        "各尺度は，質問紙の複数の項目への回答の程度から得点化され，基準の得点で3つの群に分けられる．"
        "本稿は，公表された表の値だけを使い，国・地域のあいだで意識と得点がどう関連するかを整理する．"
    ),
    fallback_objectives=(
        "本研究の目的は，TIMSS 2023の公表値で，算数・数学への意識の国際比較における日本の位置を示すことである．\n\n"
        "・RQ1: 算数・数学を「とても好き」「とても自信がある」と答えた児童生徒の割合は，国・地域によってどう違い，日本はどこに位置するか．\n"
        "・RQ2: 「とても好き」な児童生徒の割合と，国・地域の平均得点は，どのように関連しているか．"
    ),
    fallback_discussion=(
        "本実測結果に基づき，リサーチクエスチョンに沿って先行研究と対比しながら考察する．\n\n"
        "【RQ1に関する考察：意識の国際比較】\n"
        "RQ1で得られた割合の分布に関して考察する．IEA (2024) の公表値は，国・地域によって意識の尺度の分布が大きく異なることを示している．"
        "日本で「とても好き」の割合が国際平均より低い点は，Mullis et al. (2020) と同じ尺度で比べられる（同じところ）．"
        "しかし，意識は自己申告であり，回答の傾向の違いを含む（違うところ）．\n\n"
        "【RQ2に関する考察：意識と得点の関連】\n"
        "RQ2で検出された国・地域間の関連に関して考察する．Wigfield & Eccles (2000) は，個人の内で期待と価値が学習を支えると論じる．"
        "本研究の国・地域間の関連は，この個人内の関係と同じとは限らない（違うところ）．"
        "国どうしの関連は，個々の児童生徒の因果を示さない点で，Bandura (1997) の個人の自己効力感の議論とは水準が異なる（同じところ，ただし慎重に読む）．\n\n"
        "【研究の限界と今後の課題】\n"
        "本研究は公表された集計値に基づく．今後は個票による検討が望まれる．"
    ),
    fallback_review_critique=(
        "本稿は，TIMSS 2023の公表値で，算数・数学への意識の国際比較を整理した短報である．国・地域間の関連を個人の因果に読み替えない姿勢は適切だが，"
        "尺度の測定の等価性と，回答の傾向の文化差についての検討が不足しており，条件付採録（Major Revision）と判定する．"
    ),
    fallback_major_revisions=[
        "【生態学的誤謬】国・地域の集計値の関連を，個々の児童生徒に当てはめない旨を第2節と第5節に明記すること．",
        "【測定の等価性】尺度が国によって同じ意味で使われているかについて，先行研究を引用して考察すること．",
        "【回答傾向】謙遜や社会的望ましさなど，自己申告の回答傾向が日本の値に与える影響を考察すること．",
    ],
    fallback_minor_revisions=[
        "表1の注に，対象の国・地域数と学年別の内訳を加えること．",
        "図の縦軸・横軸の単位（%，得点）と，誤差の扱いを明記すること．",
    ],
    fallback_questions_to_authors=[
        "1. 日本の「好きでない」の割合の高さは，尺度の項目の訳し方や回答の傾向からどの程度説明できるとお考えか．",
        "2. 国・地域間の関連が，学年によって異なる理由について，著者の見解を伺いたい．",
    ],
    academic_discipline="数学教育学・教育心理学",
    title_en="Students' Liking of, Confidence in and Valuing of Mathematics and Achievement in TIMSS 2023: Japan in International Comparison",
    source_en="International Association for the Evaluation of Educational Achievement (IEA), TIMSS 2023",
    metrics_en=_TA_METRICS_EN,
    fallback_keywords_en=["TIMSS 2023", "MATHEMATICS", "ATTITUDES", "SELF-EFFICACY", "INTERNATIONAL COMPARISON"],
    fallback_summary_en=(
        "This study uses the published TIMSS 2023 exhibits to describe the shares of fourth- and eighth-grade students who very much like, are very confident "
        "in, and strongly value mathematics, and how these shares relate to countries' average achievement. Japan's students score high, but the share who very "
        "much like mathematics is lower than the international average. Relations across countries describe differences between countries and do not show "
        "causal effects on individual students."
    ),
    angle_id="timss_attitudes_like_confident",
    angle_name="算数・数学の「好き」「自信」の割合の国際比較（日本の位置）",
    title_theme="日本の子どもは算数・数学が好きなのか：TIMSS 2023で小4・中2を国際比較する",
    focus_metrics=[_TA_L4_LIKE, _TA_L4_NOLIKE, _TA_L4_CONF, _TA_L8_LIKE, _TA_L8_CONF],
    rq1="算数・数学を「とても好き」「とても自信がある」と答えた児童生徒の割合は，国・地域によってどう違い，日本はどこに位置するか。",
    rq2="小4で「とても好き」な児童の割合が高い国・地域ほど，「とても自信がある」児童の割合も高いか（国・地域間の関連として）。",
    scatter_x_metric=_TA_L4_LIKE,
    scatter_y_metric=_TA_L4_CONF,
    group_comparison_metric=_TA_L4_LIKE,
    analysis_method="correlation",
    secondary_chart_type="correlation_scatter",
)

DATASET_RESEARCH_ANGLES["timss2023_student_attitudes"] = [
    DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"],
    DatasetAcademicContext(
        dataset_id="timss2023_student_attitudes",
        academic_topic="算数・数学を「とても好き」な児童生徒の割合と国・地域の平均得点の関係（TIMSS 2023，小4・中2）",
        theoretical_framework="Wigfield & Ecclesの期待価値理論，Banduraの自己効力感理論，Pekrunの統制価値理論（達成感情）",
        core_research_problems=(
            "TIMSS 2023の公表値で，算数・数学を「とても好き」「とても自信がある」と答えた児童生徒の割合と，国・地域の平均得点が，国・地域のあいだでどう関連するかを確かめる．"
            "また，意識の高い群と低い群の平均得点の差が，国・地域によってどう違うかを整理する．" + _TA_CAVEAT
        ),
        banned_cliches=_TA_BANNED,
        specific_prompt_guidance=_TA_GUIDE,
        curated_references=_TA_REFS,
        fallback_title=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_title,
        fallback_subtitle=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_subtitle,
        fallback_keywords=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_keywords,
        fallback_background=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_background,
        fallback_objectives=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_objectives,
        fallback_discussion=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_discussion,
        fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_review_critique,
        fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_major_revisions,
        fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_minor_revisions,
        fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_questions_to_authors,
        academic_discipline="数学教育学・教育心理学",
        title_en="Liking of Mathematics and National Achievement in TIMSS 2023: A Cross-Country Comparison",
        source_en="International Association for the Evaluation of Educational Achievement (IEA), TIMSS 2023",
        metrics_en=_TA_METRICS_EN,
        fallback_keywords_en=["TIMSS 2023", "MATHEMATICS", "ACHIEVEMENT", "ATTITUDES", "CROSS-COUNTRY"],
        fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["timss2023_student_attitudes"].fallback_summary_en,
        angle_id="timss_attitudes_achievement_link",
        angle_name="「好き」の割合と国・地域の平均得点の関係",
        title_theme="算数・数学が好きな子の割合が高い国ほど，得点は高いのか：TIMSS 2023を国・地域で比べる",
        focus_metrics=[_TA_L8_LIKE, _TA_L8_MEAN, _TA_L4_LIKE, _TA_L4_MEAN, _TA_L8_LGAP],
        rq1="国・地域の算数・数学の平均得点は，「とても好き」な児童生徒の割合と，小4・中2のそれぞれでどのように関連しているか。",
        rq2="「とても好き」な層と「好きでない」層の平均得点の差は，国・地域によってどう違い，日本はどこに位置するか（小4・中2）。",
        scatter_x_metric=_TA_L8_LIKE,
        scatter_y_metric=_TA_L8_MEAN,
        group_comparison_metric=_TA_L8_LGAP,
        analysis_method="correlation",
        secondary_chart_type="correlation_scatter",
    ),
]


def get_all_angles_for_dataset(dataset_id: str) -> List[DatasetAcademicContext]:
    """Retrieves all registered scholarly research angles for a given dataset."""
    if dataset_id in DATASET_RESEARCH_ANGLES:
        return DATASET_RESEARCH_ANGLES[dataset_id]
    if dataset_id in DATASET_ACADEMIC_CONTEXTS:
        return [DATASET_ACADEMIC_CONTEXTS[dataset_id]]
    return [DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"]]


def get_academic_context(
    dataset_id: str,
    category: str = "math",
    angle_id: Optional[str] = None,
) -> DatasetAcademicContext:
    """
    Retrieves the dataset-specific academic context and theoretical framework.
    If angle_id is provided, returns that specific research angle; otherwise
    defaults to the primary angle for the dataset.
    """
    if dataset_id in DATASET_RESEARCH_ANGLES:
        angles = DATASET_RESEARCH_ANGLES[dataset_id]
        if angle_id:
            for ang in angles:
                if ang.angle_id == angle_id:
                    return ang
        if angles:
            return angles[0]

    if dataset_id in DATASET_ACADEMIC_CONTEXTS:
        return DATASET_ACADEMIC_CONTEXTS[dataset_id]

    # Robust fallback for custom or new datasets
    if category == "math":
        return DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"]
    return DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"]
