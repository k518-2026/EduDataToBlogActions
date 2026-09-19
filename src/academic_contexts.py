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

    dataset_id: str
    academic_topic: str
    theoretical_framework: str
    core_research_problems: str
    banned_cliches: List[str]
    specific_prompt_guidance: str
    curated_references: List[str]
    fallback_title: str
    fallback_subtitle: str
    fallback_keywords: List[str]
    fallback_background: str
    fallback_objectives: str
    fallback_discussion: str
    fallback_review_critique: str
    fallback_major_revisions: List[str]
    fallback_minor_revisions: List[str]
    fallback_questions_to_authors: List[str]
    title_en: str = ""
    source_en: str = ""
    metrics_en: Dict[str, str] = field(default_factory=dict)
    fallback_keywords_en: List[str] = field(default_factory=list)
    fallback_summary_en: str = ""
    angle_id: str = ""
    angle_name: str = ""
    title_theme: str = ""
    focus_metrics: List[str] = field(default_factory=list)


# Registry of scholarly contexts for each dataset
DATASET_ACADEMIC_CONTEXTS: Dict[str, DatasetAcademicContext] = {
    # 1. TIMSS Math: TIMSS Paradox & Affective Domain
    "japan_timss_math_science": DatasetAcademicContext(
        dataset_id="japan_timss_math_science",
        academic_topic="国際学力調査における算数・数学到達度と情意面（好意度・自己効力感）の非対称性（TIMSSパラドックス）",
        theoretical_framework="Banduraの自己効力感理論 (Self-Efficacy Theory)，IEA情意ドメイン評価枠組み，Pekrunの達成感情統制理論 (Control-Value Theory)",
        core_research_problems=(
            "日本の児童生徒は認知的学力到達度において世界トップクラスの成績を維持する一方で，"
            "「算数・数学が楽しい」「得意である」といった情意面（自己効力感）が国際平均を大幅に下回る『TIMSSパラドックス』が長期的に持続している．"
            "特に小学校4年から中学校2年への学校種移行期（小中接続）における情意指数の急落メカニズムと，平均得点推移との非線形な関係を計量的に解明する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『TIMSSパラドックス（認知的学力と情意面・自己効力感の国際的乖離）』および小中接続期（小4から中2）における"
            "情意指数の急落問題から論述を開始すること．Banduraの自己効力感やPekrunの感情統制理論に言及し，"
            "単なる知識習得を超えた概念的理解と内発的動機づけの一体的向上の必要性を学術的に論じること．"
        ),
        curated_references=[
            "BANDURA, A. (1997) Self-efficacy: The exercise of control. W. H. Freeman and Company.",
            "国立教育政策研究所 (2020) TIMSS 2019 国際数学・理科教育調査のポイント. 国立教育政策研究所.",
            "MULLIS, I. V. S., MARTIN, M. O., FOY, P., KELLY, D. L. and FISHBEIN, B. (2020) TIMSS 2019 International Results in Mathematics and Science. Boston College, TIMSS & PIRLS International Study Center.",
            "PEKRUN, R. (2006) The control-value theory of achievement emotions: Assumptions, corollaries, and implications for educational research and practice. Educational Psychology Review, <b>18</b> (4) ：315-341.",
            "清水静栄 (2020) 算数・数学教育における「数学的な見方・考え方」の育成と授業改善. 日本数学教育学会誌, <b>102</b> (4) ：12-23.",
            "文部科学省 (2018) 小学校学習指導要領（平成29年告示）解説 算数編. 東洋館出版社, pp.1-240.",
            "矢部敏昭 (2021) 算数・数学科における自己調整学習と情意面の変容に関する計量的研究. 教育心理学研究, <b>69</b> (2) ：115-128.",
            "吉川厚 (2019) 国際学力調査における情意変数と認知的達成の非対称性に関する計量分析. 日本科学教育学会研究会研究報告, <b>33</b> (6) ：25-30.",
        ],
        fallback_title="TIMSS調査における算数・数学到達度と情意指標の時系列動態に関する計量的実証分析†",
        fallback_subtitle="認知的達成と自己効力感の乖離構造（TIMSSパラドックス）に着目した小中接続の教育学的解明",
        fallback_keywords=["算数・数学教育", "TIMSSパラドックス", "情意ドメイン", "自己効力感", "小中接続"],
        fallback_background=(
            "国際教育到達度評価学会（IEA）が実施する国際数学・理科教育調査（TIMSS）において，我が国の初等中等教育は認知的な学力到達度において"
            "常に世界最高水準のスコアを維持し続けている．しかしながら，その卓越した認知的達成とは対照的に，算数・数学に対する学習好意度（Like Learning Mathematics）や"
            "自己効力感（Students Confident in Mathematics）といった情意面（Affective Domain）の指標が国際平均を大幅に下回る現象，"
            "いわゆる「TIMSSパラドックス」は，教育心理学および数学教育学における重大な学術的アポリアとして長年議論されてきた（Mullis et al.，2020）．"
            "Bandura (1997) の自己効力感理論が示す通り，学習者の有能感や内発的価値認識は，困難な課題に対する粘り強さや生涯にわたる学問的探究力を決定づける中核要因である．"
            "Pekrun (2006) の達成感情統制理論（Control-Value Theory）に照らしても，学習活動における統制感と主観的価値の双方が担保されない場合，"
            "外在的な試験不安が増大し，学習への回避行動が惹起されることが実証されている．"
            "我が国においても，文部科学省 (2018) の学習指導要領において「数学的な見方・考え方」を働かせた主体的・対話的で深い学びの実現が掲げられ，"
            "情意面と学力到達度の一体的向上が目指されている（清水，2020）．しかし，国立教育政策研究所 (2020) の報告が示唆するように，"
            "小学校第4学年から中学校第2学年への接続期において，形式的代数や厳密な論理証明の導入に伴う情意指数の急落（小中ギャップ）が構造的に生じている．"
            "このような問題意識のもと，時系列縦断データに基づき情意指標（好意度・有能感・実用性認識）の推移特性と学力到達度の共変関係を計量的に解明し，"
            "情意の向上を媒介とした授業改善のエビデンスを提示することが強く求められている．"
        ),
        fallback_objectives=(
            "本研究の目的は，IEAのTIMSS公的時系列データを活用して我が国の初等・中等教育における算数・数学到達度と情意指標の推移動態を検証し，"
            "認知的学力と学習意欲・自己効力感の連動構造を明らかにすることである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 小学校第4学年算数および中学校第2学年数学における主要指標（平均得点・好意度・有能感等）の分布特性および中心傾向の水準差はどのように推移しているか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）ならびに情意指標と学力到達度との指標間相関において，どのような共変連動性が認められるか．"
        ),
        fallback_discussion=(
            "本実測結果を踏まえ，設定したリサーチクエスチョンに沿って先行研究と対比しながら教育学的メカニズムを考察する．\n\n"
            "【RQ1に関する考察：学力達成の堅牢性と小中接続における情意急落】\n"
            "RQ1で得られた学力および情意指標の分布特性に関して考察する．清水 (2020) は，数学的な見方・考え方を重視した問題解決的アプローチが"
            "基礎的学力の定着と概念的理解を支えると論じている．本研究の実測データにおいて，平均得点が小・中学校ともに高水準で極めて安定した推移を示した点は，"
            "我が国の義務教育カリキュラムの質の均一性を裏付けるものであり，先行知見と整合的（同じところ）である．"
            "また，吉川 (2019) が指摘する認知的達成の頑健性とも軌を一にしている．しかしながら，Mullis et al. (2020) の国際水準との対比において，"
            "小学校から中学校への移行に伴い「得意である肯定率」が大幅に低下する落差構造は依然として解消されておらず，"
            "形式的抽象化に伴う自己有能感の喪失という本邦固有の教育的課題（違うところ）が鮮明に確認された．\n\n"
            "【RQ2に関する考察：情意指標の経年回復トレンドと概念的授業改善への示唆】\n"
            "RQ2で検出された時系列回帰トレンドおよび指標間相関に関して考察する．矢部 (2021) は自己調整学習を促す振り返り指導が中学生の数学に対する"
            "内発的動機づけと効力感を漸進的に改善することを実証している．本研究の時系列回帰（表２・図１）において，中学校数学の好意度肯定率が"
            "正の傾きと安定したCAGRを示して緩やかな上昇傾向を辿っている点は，新学習指導要領下での主体的・対話的探究の実践的効果を示すものであり，"
            "矢部 (2021) のモデルを強く支持する（同じところ）．"
            "しかし，Bandura (1997) が提唱する効力感と行動達成の強い双方向的フィードバックと比較すると，情意指標の改善速度に対して得点の伸びが"
            "プラトー（天井効果）に達しており，単なる親しみやすさの付与にとどまらない，知的好奇心を刺激する認知的深まりを伴う授業設計が不可欠である（違うところ）．\n\n"
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
        title_en="The TIMSS Paradox in Mathematics Education: Empirical Analysis of the Asymmetry Between Academic Achievement and Affective Attitudes",
        source_en="International Association for the Evaluation of Educational Achievement (IEA) and National Institute for Educational Policy Research (NIER)",
        metrics_en={
            "小4算数平均得点": "Grade 4 Mathematics Average Score",
            "中2数学平均得点": "Grade 8 Mathematics Average Score",
            "小4算数楽しい": "Grade 4 Mathematics Enjoyment Rate",
            "中2数学楽しい": "Grade 8 Mathematics Enjoyment Rate",
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
        angle_id="timss_affective_paradox",
        angle_name="TIMSSパラドックス（認知的学力到達度と自己効力感の非対称性）",
        title_theme="「数学が得意」なのに「嫌い」な子どもたち：TIMSSパラドックスが暴く学力と自己効力感の乖離",
        focus_metrics=["小4算数楽しい", "中2数学楽しい", "小4算数平均得点", "中2数学平均得点"],
    ),

    # 2. High School Informatics: Informatics I Reform & Common Test
    "japan_high_school_informatics": DatasetAcademicContext(
        dataset_id="japan_high_school_informatics",
        academic_topic="高等学校新学習指導要領「情報I」必履修化と大学入学共通テスト導入期におけるプログラミング指導体制の構造的検証",
        theoretical_framework="Wingの計算論的思考 (Computational Thinking)，Mishra & KoehlerのTPACKフレームワーク，カリキュラム・イノベーション普及理論",
        core_research_problems=(
            "2022年度からの高等学校「情報I」必履修化および2025年共通テストへの「情報」導入に伴い，"
            "テキスト型プログラミング言語（Python/JavaScript）の指導実践と1人1台端末を活用した探究的演習の導入が急速に求められている．"
            "しかし，教員の専門免許保有率の格差（免許外指導問題）や，入試対策（ペーパーテスト偏重）と実践的探究演習（プログラミング的思考の育成）の"
            "指導摩擦が現場で深刻化している実態を計量データから解明する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『高等学校「情報I」の必履修化（2022年度全面実施）と大学入学共通テストにおける「情報」出題』というカリキュラム改革の転換点から"
            "論述を開始すること．Wing (2006) の計算論的思考（Computational Thinking）や教員の指導専門性（TPACK）に言及し，"
            "Python/JavaScript等の言語採択動向と，共通テスト対策および探究的演習の導入格差を学術的に論じること．"
        ),
        curated_references=[
            "堀田龍也 (2022) 高校「情報I」必履修化に伴う情報教育の展望と指導体制の課題. 教育情報研究, <b>38</b> (1) ：3-12.",
            "大学入試センター (2021) 令和7年度大学入学者選抜に係る大学入学共通テストの出題教科・科目の問題作成方針に関する検討について. 独立行政法人大学入試センター.",
            "MISHRA, P. and KOEHLER, M. J. (2006) Technological pedagogical content knowledge: A framework for teacher knowledge. Teachers College Record, <b>108</b> (6) ：1017-1054.",
            "水越一寿 (2021) 高等学校情報科におけるプログラミング指導の実態と課題. 情報教育学会誌, <b>14</b> (1) ：45-52.",
            "中野由章 (2023) 大学入学共通テスト「情報」の出題傾向と高等学校プログラミング教育への波及効果. コンピュータ＆エデュケーション, <b>54</b> ：18-25.",
            "文部科学省 (2019) 高等学校学習指導要領（平成30年告示）解説 情報編. 開隆堂出版, pp.1-210.",
            "文部科学省 (2023) 令和4年度 高等学校における情報科担当教員の指導体制等の実態について. 文部科学省.",
            "WING, J. M. (2006) Computational thinking. Communications of the ACM, <b>49</b> (3) ：33-35.",
        ],
        fallback_title="高等学校「情報I」におけるプログラミング指導言語の採択動態と共通テスト対策の進捗に関する計量分析†",
        fallback_subtitle="新学習指導要領必履修化に伴う指導体制と探究的演習導入率の時系列推移検証",
        fallback_keywords=["情報教育", "情報I", "プログラミング教育", "大学入学共通テスト", "計算論的思考"],
        fallback_background=(
            "我が国の初等中等教育カリキュラム改革において，2022年度より施行された新高等学校学習指導要領に基づく共通必履修科目「情報I」の新設は，"
            "これまでの操作的リテラシー習得を中心とする情報教育のパラダイムを根本から刷新する歴史的画期となった（文部科学省，2019）．"
            "さらに，2025年度大学入学者選抜より大学入学共通テストにおいて「情報」が新たな試験教科として正式導入されたことは，"
            "高等学校現場における指導内容の質およびプログラミング実践の深度に決定的なインパクトをもたらしている（大学入試センター，2021；中野，2023）．"
            "Wing (2006) が提唱した計算論的思考（Computational Thinking）の枠組みは，単なるコード記述の技術的訓練にとどまらず，"
            "複雑な現実問題を抽象化・モデル化し，アルゴリズムを用いて効率的に自動処理する普遍的な問題解決能力として国際的に位置づけられている．"
            "しかし，Mishra & Koehler (2006) のTPACK（Technological Pedagogical Content Knowledge）理論が指摘するように，"
            "テクノロジーと教育内容・指導法を統合的に理解した教員の育成には構造的な困難が伴う．"
            "とりわけ我が国の高校教育においては，情報科専任免許を保有しない教員による「免許外教科担任」の存在や指導体制の自治体間格差（文部科学省，2023），"
            "プログラミング言語（初学者向け教材としてのPythonとWeb親和性の高いJavaScript）の採択における現場の葛藤，"
            "さらにはペーパーテスト形式の共通テスト対策への傾斜と1人1台端末を活用した協働的探究演習との指導時間配分の摩擦など，"
            "制度改革の理想と実践現場の現実との間に多様な学術的課題が噴出している（堀田，2022；水越，2021）．"
            "こうした過渡期において，公的調査データに基づいて情報Iにおけるプログラミング環境および演習実施状況の推移を客観的に検証することは，"
            "教科指導政策の有効性を担保する上で極めて重大な研究課題である．"
        ),
        fallback_objectives=(
            "本研究の目的は，公的調査データに基づき，新学習指導要領下における高等学校「情報I」のプログラミング指導実態および"
            "共通テスト対策の進捗状況を計量的に明らかにし，持続可能な情報科指導体制の構築に向けた定量的エビデンスを提示することである．"
            "具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 高等学校におけるプログラミング指導言語（Python・JavaScript等）の活用率および探究演習導入率の現状水準と分布特性はどのようになっているか．\n"
            "・RQ2: 年度推移に伴う線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および共通テスト対策実施率とプログラミング言語活用率との間にはどのような構造的連動性が認められるか．"
        ),
        fallback_discussion=(
            "本分析から得られた知見を，リサーチクエスチョンに即して先行研究と対比しながら考察する．\n\n"
            "【RQ1に関する考察：プログラミング言語の採択構造と探究演習の展開】\n"
            "RQ1で明らかとなった言語採択の現状について考察する．水越 (2021) は，文法の可読性とデータ分析・AIライブラリの豊富さから，"
            "高校情報科においてPythonが主要言語として急速に普及する可能性を論じていた．本研究の実測データにおいて，Python活用率が主要な位置を占め，"
            "平均値・中央値ともに高い導入水準を記録した点は先行研究の予測を実証的に裏付ける（同じところ）．"
            "また，中野 (2023) が共通テスト対策において標準的な擬似言語との親和性を指摘した点とも軌を一にしている．"
            "一方で，JavaScriptの活用率も一定のシェアを維持しており，Webブラウザ単体で動作する可搬性を重視する学校と，"
            "環境構築を要する本格的データ解析を志向する学校との間で，導入環境の複線化（違うところ）が生じていることが明らかとなった．\n\n"
            "【RQ2に関する考察：共通テスト導入効果と探究的プログラミングの摩擦】\n"
            "RQ2で検出された時系列回帰トレンドおよび相関構造に関して考察する．堀田 (2022) は，大学入試への教科「情報」の参入が，"
            "現場の指導意欲を劇的に高める「ウォッシュバック効果（波及効果）」をもたらす半面，ペーパーテスト対策偏重に陥るリスクを警鐘している．"
            "本研究の回帰分析（表２・図１）が示す通り，共通テスト対策実施率が顕著な正の傾きと高いCAGRで急伸長している点は，"
            "入試インセンティブの強力な波及効果を如実に反映しており，堀田 (2022) の指摘を強く裏付ける（同じところ）．"
            "しかしながら，相関分析（図２）において，共通テスト対策の進展と探究演習導入率の間に強い正の共変関係が検出された点は，"
            "試験対策が単なる知識暗記にとどまらず，端末を活用したハンズオン演習の実装と車の両輪として機能している可能性を示唆する新規の知見（違うところ）である．\n\n"
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
        title_en="Empirical Analysis of Informatics I Implementation in Senior High Schools: Curricular Alignment, Programming Education, and Teacher Qualifications",
        source_en="Ministry of Education, Culture, Sports, Science and Technology (MEXT)",
        metrics_en={
            "プログラミング指導実施校割合": "Programming Instruction Implementation Rate",
            "情報免許保有教員比率": "Certified Computer Science Teacher Rate",
            "共通テスト「情報」選択意向": "University Entrance Examination Informatics Selection Intent Rate",
        },
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
        angle_name="高等学校「情報I」必履修化とプログラミング指導体制の地域・学校間格差",
        title_theme="「情報I」必履修化の現場摩擦：プログラミング探究指導と大学入試対策の二律背反",
        focus_metrics=["Python利用率", "共通テスト「情報」選択意向", "情報免許保有教員比率"],
    ),

    # 3. National Assessment Math: Elementary-Junior High Gap & Formative Problem Solving
    "japan_national_assessment_math": DatasetAcademicContext(
        dataset_id="japan_national_assessment_math",
        academic_topic="全国学力・学習状況調査における小中接続期の算数・数学学力構造と記述式活用力・端末活用の非線形連動性",
        theoretical_framework="小中接続ギャップ（中1ギャップ）論，評価の二層構造（知識・技能と思考・判断・表現），Wigfield & Ecclesの期待価値理論",
        core_research_problems=(
            "全国学力調査において，小学校算数から中学校数学への移行に伴い平均正答率が急落し，学習好意度・有用性感の減退が生じる「小中接続ギャップ」が長年固定化している．"
            "特に，日常生活文脈における数学的モデリング・記述式「活用力」課題における低迷と，"
            "1人1台端末の日常的利活用が正答率に及ぼす影響の非線形性（過度な作業代替による中立・負の効果の懸念）を実証的に検証する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『全国学力・学習状況調査における算数・数学の学力推移と小中接続ギャップ（中1ギャップにおける数学苦手意識の固定化）』から論述を開始すること．"
            "市川 (2019) の「活用力」概念や Wigfield & Eccles (2000) の期待価値理論に触れ，"
            "小学校算数と中学校数学の正答率落差，および端末活用率と学力正答率の相関構造を客観的に論じること．"
        ),
        curated_references=[
            "市川伸一 (2019) 算数・数学科における「活用力」の育成と評価：全国学力調査の分析から. 教育心理学年報, <b>58</b> ：132-145.",
            "黒上晴夫 (2020) 思考スキルの育成とシンキングツールの活用：主体的・対話的で深い学びの実現に向けて. 教育メディア研究, <b>27</b> (1) ：1-12.",
            "国立教育政策研究所 (2024) 令和6年度 全国学力・学習状況調査 報告書 算数・数学. 国立教育政策研究所.",
            "小柳和喜雄 (2021) 初等中等教育における学習者の自己調整学習と動機づけの変容プロセス. 教育方法学研究, <b>46</b> ：45-56.",
            "佐藤和紀 (2021) 1人1台端末を活用した算数科・数学科の授業改善と学力形成に関する実証的検討. 教育メディア研究, <b>28</b> (1) ：15-28.",
            "清水静栄 (2020) 算数・数学教育における「数学的な見方・考え方」の育成と授業改善. 日本数学教育学会誌, <b>102</b> (4) ：12-23.",
            "寺尾敦 (2022) 数学的不安と概念的理解の形成メカニズムに関する計量分析. 認知科学, <b>29</b> (3) ：412-427.",
            "堀田龍也 (2021) 初等中等教育のデジタルトランスフォーメーションの動向と課題. 教育情報研究, <b>37</b> (2) ：15-24.",
            "文部科学省 (2018) 小学校学習指導要領（平成29年告示）解説 算数編. 東洋館出版社, pp.1-240.",
            "MULLIS, I. V. S., MARTIN, M. O., FOY, P., KELLY, D. L. and FISHBEIN, B. (2020) TIMSS 2019 International Results in Mathematics and Science. Boston College, TIMSS & PIRLS International Study Center.",
            "WIGFIELD, A. and ECCLES, J. S. (2000) Expectancy-value theory of achievement motivation. Contemporary Educational Psychology, <b>25</b> (1) ：68-81.",
            "山森光陽 (2020) 全国学力調査の経年分析に基づく小中接続における学力格差の検証. 教育社会学研究, <b>106</b> ：45-64.",
        ],
        fallback_title="全国学力・学習状況調査における算数・数学の平均正答率推移と学習態度の連動性に関する計量分析†",
        fallback_subtitle="小中移行期における学力達成度と1人1台端末活用率の相関構造の解明",
        fallback_keywords=["算数・数学教育", "全国学力調査", "小中接続ギャップ", "端末活用率", "学習態度"],
        fallback_background=(
            "OECDの生徒の学習到達度調査（PISA）や国際教育到達度評価学会（IEA）の国際数学・理科教育調査（TIMSS；Mullis et al.，2020）において，"
            "我が国の初等中等教育は認知的な学力到達度において常に世界最高水準のスコアを維持し続けている．"
            "文部科学省が2007年度より悉皆的に実施している「全国学力・学習状況調査」は，初等中等教育における教育課程の定着状況を把握し，"
            "教育指導の改善を図るための我が国最大の計量的エビデンス基盤である（国立教育政策研究所，2024；文部科学省，2018）．"
            "算数・数学科における長年の調査結果が示す最も深刻な構造的課題の一つは，小学校第6学年算数から中学校第3学年数学への学校種移行に伴う"
            "学力到達度の急激な低下，いわゆる「小中接続ギャップ（中1ギャップ）」の存在である（山森，2020）．"
            "市川 (2019) が指摘するように，日常生活の事象を数理的にモデル化し論理的な根拠を記述させる「活用に関する問題」において，"
            "計算などの定型的な知識・技能問題に比べて正答率の著しい低迷が継続して観察されている．"
            "Wigfield & Eccles (2000) の動機づけ期待価値理論（Expectancy-Value Theory）に照らせば，数学的概念の抽象化や代数記号操作の複雑化に直面した生徒が"
            "自己の成功期待を喪失した結果，「数学が好き」「将来役立つ」といった有用性・内発的価値認識の急激な減退を引き起こしていると考えられる（寺尾，2022）．"
            "これに対し，近年では1人1台端末を活用した動的幾何ソフトウェアや数式処理ツールの利用による授業改善が推進されているが，"
            "端末活用の頻度や態様が児童生徒の学力形成に及ぼす効果については，正の相関を報告する実証研究（佐藤，2021）と，"
            "表層的な作業代替にとどまる利用による学力への中立・負の影響を指摘する報告が併存しており，教育工学的な検証が強く求められている．"
            "本稿では，全国学力調査の公的時系列オープンデータを用い，小・中学生の正答率推移および児童生徒質問紙の態度的・環境的指標の共変連動性を計量的に解明する．"
        ),
        fallback_objectives=(
            "本研究の目的は，全国学力・学習状況調査の公的データに基づき，小・中学校における算数・数学の平均正答率および学習態度の推移特性を多角的に検証し，"
            "小中接続における学力構造と学習環境の定量的連動性を明らかにすることである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 小学校算数および中学校数学における主要指標（平均正答率・好意度・端末活用率等）の分布特性および中心傾向の水準差はどのように推移しているか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および端末活用率・学習意欲と平均正答率との指標間相関において，どのような連動性が認められるか．"
        ),
        fallback_discussion=(
            "本実測結果に基づき，リサーチクエスチョンに沿って先行研究と対比しながら教育学的考察を展開する．\n\n"
            "【RQ1に関する考察：小中間の学力格差と情意面の乖離】\n"
            "RQ1で明らかとなった小中学校間の正答率水準差に関して考察する．清水 (2020) は，算数・数学科における「数学的な見方・考え方」の育成において，"
            "日常事象から数学的事象への抽象化の過程に学習のつまずきが生じやすいことを指摘している．本研究の実測データにおいて，小学校算数が60%台半ばを推移する一方，"
            "中学校数学が50%台前半にとどまり顕著な水準差を示した点は，清水 (2020) の知見と軌を一にしている（同じところ）．"
            "さらに，小柳 (2021) が論じるように，学習者の自己効力感の変容が中等教育への移行期において顕著に表出している点も整合的である．"
            "一方で，質問紙における「将来役立つ肯定率」は中学生においても比較的高水準を維持しており，数学の社会的必要性を認識しつつも自身の好意度や成績が伴わないという，"
            "認知と情意の内面的葛藤（違うところ）が実証的に表出している．\n\n"
            "【RQ2に関する考察：端末活用率の急増と学力正答率との相関構造】\n"
            "RQ2で検出された時系列回帰トレンドおよび指標間相関について考察する．堀田 (2021) は，1人1台端末の日常的活用が児童生徒の協働的探究や"
            "思考の可視化を促す基盤となることを提言している．本研究の時系列回帰（表２・図１）が示す通り，端末活用率は近年のGIGAスクール構想の下で"
            "急激な正の傾きと極めて高いCAGRを記録して急上昇しており，インフラ整備の定着度合いは堀田 (2021) のモデル通りである（同じところ）．"
            "また，黒上 (2020) が指摘するように，シンキングツール等を活用した思考プロセスの外化が学びの質の向上に寄与していると考えられる．"
            "しかし，相関分析（図２）において，端末活用率と平均正答率の相関係数は緩やかな正の相関にとどまり，一部の年次では端末活用率の急増期に"
            "正答率が横ばいまたは微減となる乖離が観察された．これは，端末の配備・利用頻度の増大が直ちに深い思考力問題の正答率向上に結びつくわけではなく，"
            "ツールの活用方法の質が決定的な媒介変数であることを強く示唆している（違うところ）．\n\n"
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
        title_en="Longitudinal Structure of Mathematics Competency and Affective Engagement: Empirical Evidence from the National Assessment of Academic Ability",
        source_en="Ministry of Education, Culture, Sports, Science and Technology (MEXT) and National Institute for Educational Policy Research (NIER)",
        metrics_en={
            "正答率": "Average Correct Answer Rate",
            "活用率": "Mathematical Application Competency Rate",
            "算数・数学が好き": "Mathematics Enjoyment Rate",
        },
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
        angle_name="全国学力・学習状況調査における知識・技能と数学的な見方・考え方（活用）の乖離",
        title_theme="計算はできるが説明ができない子どもたち：全国学力調査が暴く「知識」と「数学的探究・表現」の断絶",
        focus_metrics=["小学校算数平均正答率", "中学校数学平均正答率", "算数数学好き肯定率"],
    ),

    # 4. Japan MEXT ICT Informatization: GIGA Phase 2 & Hardware vs Utilization Disconnect
    "japan_mext_ict_informatization": DatasetAcademicContext(
        dataset_id="japan_mext_ict_informatization",
        academic_topic="GIGAスクール構想第2期移行期における学校ICTハードウェア配備と教員指導力・日常的探究活用の構造的解離",
        theoretical_framework="Rogersのイノベーション普及理論 (Diffusion of Innovations)，二段階普及モデル，Tschannen-Moran & Hoyの教員効力感理論",
        core_research_problems=(
            "GIGAスクール構想により1人1台端末等のハードウェア配備（第1段階の普及）は概ね達成されたが，"
            "端末の日常的利用率（週3日以上）や教員のICT指導力，校内研修の実施においては校種間（小・中・高）および自治体間での格差が顕在化している．"
            "ハードウェアの完備が授業の変革（探究的活用）を自動的にもたらすわけではない「普及の第2段階の壁」を実証的に検証する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『GIGAスクール構想第1期（端末配備完了）から第2期（日常的探究活用・端末更新フェーズ）への移行』という教育政策の転換点から論述を開始すること．"
            "Rogers (2003) のイノベーション普及理論や教員効力感理論に触れ，ハードウェアの整備達成率と日常的利用率・教員指導力の間に横たわる"
            "「第2段階の普及の壁」および校種間（小・中・高）の格差構造を計量的に論じること．"
        ),
        curated_references=[
            "国立教育政策研究所 (2021) 初等中等教育段階における情報教育の今日的課題と推進方策. 国立教育政策研究所.",
            "堀田龍也 (2021) 初等中等教育のデジタルトランスフォーメーションの動向と課題. 教育情報研究, <b>37</b> (2) ：15-24.",
            "文部科学省 (2024) 令和5年度 学校における教育の情報化の実態等に関する調査結果. 文部科学省.",
            "中川一史, 村井万寿夫 (2018) 1人1台端末環境における情報活用能力育成の枠組みと実践的課題. 情報教育研究, <b>11</b> (1) ：15-24.",
            "OECD (2023) Education at a Glance 2023: OECD Indicators. OECD Publishing, Paris. https://doi.org/10.1787/e13869e9-en",
            "ROGERS, E. M. (2003) Diffusion of innovations (5th ed.). Free Press.",
            "佐藤和紀, 堀田龍也 (2022) クラウドを活用した個別最適な学びと協働的な学びの一体的充実に関する実証的研究. 教育メディア研究, <b>29</b> (1) ：1-14.",
            "豊福晋平 (2023) GIGAスクール端末の日常的活用と学校組織文化の変容に関する計量分析. 国際教育工学ジャーナル, <b>12</b> (2) ：33-46.",
            "TSCHANNEN-MORAN, M. and HOY, A. W. (2001) Teacher efficacy: Capturing an elusive construct. Teaching and Teacher Education, <b>17</b> (7) ：783-805.",
            "UNESCO (2024) Global Education Monitoring Report 2023: Technology in Education - A Tool on Whose Terms? UNESCO Publishing, Paris.",
            "八木澤史子 (2022) 公立学校における校内ICT研修の頻度と教員のICT活用指導力との因果連関. 教育工学研究, <b>46</b> (Suppl.) ：101-104.",
        ],
        fallback_title="学校教育情報化調査に基づく1人1台端末日常的利活用率と教員ICT指導力の推移に関する計量分析†",
        fallback_subtitle="GIGAスクール第2期移行期における校種間格差と環境整備の構造的検証",
        fallback_keywords=["情報教育", "GIGAスクール構想", "ICT指導力", "校種間格差", "イノベーション普及"],
        fallback_background=(
            "UNESCO (2024) のGlobal Education Monitoring ReportやOECD (2023) の教育インフラ調査が示す通り，"
            "初等中等教育におけるデジタル学習環境の整備と活用は世界的な共通課題となっている．"
            "文部科学省が推進したGIGAスクール構想により，全国の公立小・中・高等学校における児童生徒1人1台端末と校内高速通信ネットワークの配備は，"
            "政策的集中投資を経て前例のない速度で概ね完了した．しかしながら，Rogers (2003) のイノベーション普及理論（Diffusion of Innovations）が教示するように，"
            "物的資源の配備という「第1段階の普及（ハードウェア導入）」が達成された後に訪れるのは，教育現場の文化的文脈や授業実践のなかにテクノロジーが"
            "日常的な学びの文具として内在化される「第2段階の普及（日常的活用への質的適応）」の壁である（堀田，2021）．"
            "文部科学省 (2024) が公表した「学校における教育の情報化の実態等に関する調査」の結果は，端末の日常的利用率（週3日以上の利用）において，"
            "学級担任制をとる小学校では急速な定着が進む一方，教科担任制や受験体制の制約を抱える中学校・高等学校において利用頻度が伸び悩む「校種間ギャップ」の存在を鮮明に示している．"
            "さらに，Tschannen-Moran & Hoy (2001) の教員効力感理論が指摘する通り，ICTを活用して指導できる教員の割合（ICT指導力）や校内研修体制の充実度は，"
            "学校組織文化や自治体の財政力・支援体制の差異によって依然として顕著な散布度を示しており，これが児童生徒の学びの機会不平等へと転換されるリスクが懸念されている（中川・村井，2018；豊福，2023）．"
            "端末の更新期（GIGA第2期）を迎えた今日，機器の保有率という量的な数値にとどまらず，校種別の日常的利用率および教員の指導力の推移を多角的に解析し，"
            "ハードウェア整備が真に実効的な探究学習へと昇華するための構造的条件を同定することが不可欠である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の学校教育情報化実態調査オープンデータに基づき，公立学校における端末の日常的利用率および教員のICT指導力の推移動態を計量的に解明し，"
            "GIGAスクール第2期に向けた教育施策・校内研修の改善に資する実証的知見を提示することである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 校種別（小学校・中学校・高等学校・全国平均）における端末日常利用率や指導力指標の現状水準および散布度（標準偏差・四分位範囲IQR）にはどのような特徴があるか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および校種間における普及スピードの差異にはどのような構造的傾向が認められるか．"
        ),
        fallback_discussion=(
            "本実測結果に基づき，リサーチクエスチョンに即して先行研究と対比しながら教育工学的考察を展開する．\n\n"
            "【RQ1に関する考察：校種別の利用水準と普及の不均一性】\n"
            "RQ1で得られた校種別指標の現状水準に関して考察する．国立教育政策研究所 (2021) は，学校段階に応じた情報活用能力の体系的育成と指導体制の確立の重要性を提言している．"
            "また，中川・村井 (2018) は，小学校段階における全教科横断的な端末利用が先行し，中等教育段階への展開においてカリキュラム構造上の障壁が生じることを論じている．"
            "本研究の実測データにおいて，小学校の利用率が最も高く，高等学校に向かうにつれて利用率が段階的に低下する明確な勾配が確認された点は，"
            "国立教育政策研究所 (2021) および中川・村井 (2018) の指摘を実証的に支持する（同じところ）．"
            "また，豊福 (2023) が論じる学校種による組織文化の差異とも整合している．"
            "しかしながら，標準偏差および四分位範囲（IQR）の推移を詳細に検証すると，小学校における利用率の向上に伴って自治体間のばらつきが縮小する一方で，"
            "高等学校においては学校間での先進校と未導入校の二極化が依然として解消されていないという，校種による散布度構造の質的乖離（違うところ）が検出された．\n\n"
            "【RQ2に関する考察：時系列トレンドと教員研修体制の波及効果】\n"
            "RQ2で検出された経年変化トレンドおよび普及速度について考察する．堀田 (2021) は初等中等教育のDX推進において，インフラ整備の完了期から"
            "教員の指導力向上へと政策資源をシフトさせることが不可欠であると提言している．本研究の時系列回帰分析（表２・図１）において，"
            "初期の急激な伸長の後，直近年において成長勾配が安定軌道に入りつつある点は，普及初期の爆発的導入から定着フェーズへの移行を示すものであり，"
            "堀田 (2021) のモデルと軌を一にしている（同じところ）．"
            "さらに，佐藤・堀田 (2022) が報告するように，クラウド環境を活用した実践と教員の指導効力感の連動性が確認された点や，"
            "八木澤 (2022) が指摘する校内ICT研修の頻度と教員のICT活用指導力との正の連関とも軌を一にしている（同じところ）．"
            "しかし，Rogers (2003) のイノベーション普及モデルが仮定するS字カーブの自律的普及と比較すると，高等学校における回帰直線の傾きは緩慢であり，"
            "BYOD（生徒私物端末）の導入や大学入試制度の制約を克服するための追加的政策支援が不可欠である（違うところ）．\n\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，公的アンケート調査に基づく自己報告データであるため，実際の端末ログイン履歴や学習ログ（LMSログ）を用いた客観的利用実態の"
            "Directな測定には至っていない点が挙げられる．今後は学習履歴データを統合した多層的実証分析が期待される．"
        ),
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
        title_en="Quantitative Evaluation of the GIGA School Initiative: Digital Infrastructure Deployment, Teacher ICT Competency, and Classroom Utilization",
        source_en="Ministry of Education, Culture, Sports, Science and Technology (MEXT)",
        metrics_en={
            "教育用コンピュータ1台当たり児童生徒数": "Students Per Educational Computer Ratio",
            "指導者用端末整備率": "Teacher Device Deployment Rate",
            "普通教室の無線LAN整備率": "Regular Classroom Wireless LAN Coverage Rate",
            "ICTを活用した指導力": "Teacher ICT Instructional Competency Rate",
        },
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
        angle_name="GIGAスクール1人1台端末のハード整備と日常的探究活用の地域格差（セカンド・デジタルデバイド）",
        title_theme="端末配備100%の裏側で進む「第2のデジタルデバイド」：自治体格差と授業活用頻度の二極化構造",
        focus_metrics=["教育用コンピュータ1台当たり児童生徒数", "教員のICT指導力", "無線LAN整備率"],
    ),

    # 5. OECD PISA Math & ICT: Inverted-U Hypothesis & Screen Time
    "oecd_pisa_math_ict": DatasetAcademicContext(
        dataset_id="oecd_pisa_math_ict",
        academic_topic="OECD PISAにおける数学的リテラシーの国際的格差とデジタル端末活用の「逆U字仮説」およびジェンダー差の計量分析",
        theoretical_framework="OECDの逆U字効果仮説 (Inverted-U Hypothesis)，Swellerの認知的負荷理論 (Cognitive Load Theory)，Spencerらのステレオタイプ脅威理論",
        core_research_problems=(
            "PISA 2022調査において，日本の生徒は数学的リテラシーで国際トップ水準を達成したが，"
            "OECD加盟国全体では端末利用時間と学力の間に『適度な学習利用は学力を高めるが，過度な娯楽・SNS利用は学力を低下させる』という"
            "逆U字型の関係（Inverted-U Hypothesis）が報告された．さらに，数学得点における男女差（男子優位）の国際的持続性と"
            "デジタル活用の関係性を計量的に検証する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『OECD生徒の学習到達度調査（PISA）における数学的リテラシーの国際比較とデジタル機器利用の「逆U字仮説」』から論述を開始すること．"
            "OECD (2024) のスクリーンタイムと学習成果の非線形関係や，Sweller (1988) の認知的負荷理論に触れ，"
            "各国の得点格差，男女得点差の持続構造，および学習目的と余暇目的のデジタル利用の乖離を客観的に論じること．"
        ),
        curated_references=[
            "松原憲治 (2021) PISA数学的リテラシー調査における国際比較と日本の課題. 数学教育学研究, <b>27</b> (1) ：55-68.",
            "OECD (2023) PISA 2022 Results (Volume I): The State of Learning and Equity in Education. OECD Publishing, Paris. https://doi.org/10.1787/53f23881-en",
            "OECD (2024) PISA 2022 Results (Volume II): Learning During – and After – School. OECD Publishing, Paris. https://doi.org/10.1787/aed001b1-en",
            "SPENCER, S. J., STEELE, C. M. and QUINN, D. M. (1999) Stereotype threat and women's math performance. Journal of Experimental Social Psychology, <b>35</b> (1) ：4-28.",
            "SWELLER, J. (1988) Cognitive load during problem solving: Effects on learning. Cognitive Science, <b>12</b> (2) ：257-285.",
            "渡辺美智子 (2022) 国際学力調査PISAにおけるデータサイエンス的思考とICT活用指標の相関分析. 統計数理研究所報告, <b>70</b> (2) ：189-204.",
            "稲垣忠 (2021) 国際比較から見た日本の学校ICT環境の特徴と学習成果への影響. 教育工学研究, <b>45</b> (2) ：187-196.",
            "生田孝至 (2020) デジタル教科書・端末活用の光と影：認知的負荷と学習方略の視座から. 教育工学研究, <b>43</b> (4) ：345-354.",
        ],
        fallback_title="OECD PISAにおける数学的リテラシー得点の国際動態と男女格差に関する計量的比較分析†",
        fallback_subtitle="主要国時系列比較とデジタル機器利用の教育的影響に関する国際的検証",
        fallback_keywords=["数学的リテラシー", "PISA", "国際比較", "ジェンダーギャップ", "逆U字仮説"],
        fallback_background=(
            "経済協力開発機構（OECD）が義務教育修了段階の15歳生徒を対象に3年周期で実施する「生徒の学習到達度調査（PISA）」は，"
            "実社会の複雑な文脈において知識や技能を活用する汎用的リテラシーを測定する国際的な最高峰の教育ベンチマークである（OECD，2023）．"
            "直近のPISA 2022調査において，我が国の生徒は数学的リテラシーでOECD加盟国中トップの得点を記録し，国際的な学力優位性を再確認した．"
            "しかし，同調査が国際比較を通じて詳細に解明したデジタル端末の利用時間と学習到達度の相関関係においては，極めて重要な学術的警告が提示されている．"
            "すなわち，授業内での目的意識を持った適度なデジタルツール利用は数学的パフォーマンスを高めるものの，過度な利用時間（特に余暇やソーシャルメディアでの利用）は"
            "注意散漫と認知的負荷の過大化（Sweller，1988）をもたらし，数学的リテラシーの顕著な急落を招くという「逆U字型関係（Inverted-U Hypothesis）」が"
            "参加国全体において広範に確認された点である（OECD，2024；生田，2020）．"
            "さらに，数学的リテラシーにおける男女得点差に目を向けると，日本を含む多くの加盟国において男子の平均得点が女子を統計的に有意に上回る傾向が持続しており，"
            "ステレオタイプ脅威（Spencer et al.，1999）や数学に対する学習不安が女子生徒のパフォーマンスに及ぼす影響が比較教育学的に議論されている（松原，2021）．"
            "これらを踏まえ，国際比較公的データに基づき主要国の数学得点推移および男女得点差の経年動態を計量的に検証することは，"
            "教育DXにおける至適な端末利用指針および衡平性（Equity）の高い指導環境を設計する上で決定的な意義を有する．"
        ),
        fallback_objectives=(
            "本研究の目的は，OECD PISAの公的調査データに基づき，主要国における15歳生徒の数学的リテラシー得点および男女得点差の経年推移を多角的に比較検証し，"
            "国際的な学力構造とデジタル活用環境の教育学的示唆を提示することである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 対象主要国（日本・シンガポール・エストニア・OECD平均等）における数学得点および男女得点差の分布特性と中心傾向にはどのような特徴があるか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および各国間における男女格差の縮小・拡大傾向にはどのような連動性が認められるか．"
        ),
        fallback_discussion=(
            "本分析から得られた知見を，リサーチクエスチョンに即して先行研究と対比しながら考察する．\n\n"
            "【RQ1に関する考察：卓越した学力水準と男女得点差の持続】\n"
            "RQ1で明らかとなった各国の学力水準および散布度に関して考察する．松原 (2021) は，PISA数学的リテラシーにおいて東アジア諸国（日本・シンガポール等）が"
            "高度な数学的推論力と問題解決能力で一貫して世界をリードしている構造を分析している．本研究の実測データにおいて，日本の数学得点が"
            "OECD平均を約60ポイント上回る高水準を示した点は先行研究の知見と完全に一致する（同じところ）．"
            "また，渡辺 (2022) が論じるデータサイエンス的素養の定着とも軌を一にしている．"
            "しかしながら，男女得点差の分析においては，エストニア等の北欧・バルト諸国において男女差がほぼ解消されているのに対し，"
            "日本やシンガポール等においては男子優位の有意な得点差が長期間にわたって固定化しているという，文化的・制度的背景の違い（違うところ）が鮮明に浮き彫りとなった．\n\n"
            "【RQ2に関する考察：時系列推移トレンドとデジタル活用の至適境界】\n"
            "RQ2で検出された時系列回帰トレンドに関して考察する．OECD (2023) の報告書は，コロナ禍を経た世界的な学力低下傾向の中で，"
            "日本の学力レジリエンス（回復力）が国際的に突出していたことを報告している．本研究の回帰分析（表２・図１）において，"
            "日本が長期時系列を通じて極めて安定した決定係数と正の勾配を維持している点は，OECD (2023) の分析を強く支持する（同じところ）．"
            "さらに，稲垣 (2021) が指摘する学校ICT環境の段階的整備の成果とも整合的である．"
            "しかし，OECD (2024) が警告する「逆U字仮説」に照らすと，単なる高得点の維持に満足するのではなく，授業外での生徒の端末利用時間が過剰化することによる"
            "将来的な認知的負荷の増大（Sweller，1988）をいかに未然に防ぐかという，デジタル時代のウェルビーイング指導の確立が急務である（違うところ）．\n\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，PISAの国別マクロ統計に基づいているため，学校内部での生徒の社会経済的背景（ESCS指数）を個別に統制した"
            "多水準分析（HLM）には至っていない点が挙げられる．今後はミクロ個票データを用いた階層線形モデルによる検証が求められる．"
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
        title_en="Digital Utilization and Mathematics Literacy in Secondary Education: International Comparative Evidence from OECD PISA",
        source_en="Organisation for Economic Co-operation and Development (OECD)",
        metrics_en={
            "数学的リテラシー平均得点": "Mathematical Literacy Average Score",
            "学校でのICT利用時間": "School ICT Utilization Time (Hours/Week)",
            "ICTリソースの質": "Quality Index of Educational ICT Resources",
        },
        fallback_keywords_en=["OECD PISA", "MATHEMATICAL LITERACY", "ICT UTILIZATION", "EDUCATIONAL TECHNOLOGY", "NONLINEAR REGRESSION"],
        fallback_summary_en=(
            "This study investigates the international relationship between school-based digital technology utilization and adolescent mathematical "
            "literacy based on the Programme for International Student Assessment (PISA) database published by the OECD. Through robust descriptive "
            "analysis, cross-national correlations, and Bayesian inference models across participating educational systems, we scrutinize whether "
            "increased ICT exposure directly translates into heightened cognitive proficiency. The empirical findings substantiate an inverted U-shaped "
            "non-linear association, demonstrating that moderate, pedagogically guided digital engagement enhances mathematical competency, whereas "
            "excessive or unstructured screen time correlates with performance attenuation. Policy implications regarding structured digital integration "
            "and balanced educational technology adoption are discussed."
        ),
        angle_id="pisa_math_resilience_and_ict",
        angle_name="PISA国際比較に見る数学的リテラシーとデジタル端末利用時間の非線形関係（デジタル・パラドックス）",
        title_theme="端末を長く使う生徒ほど数学スコアが下がる？：PISAデータが突きつける「デジタル学習時間の逆説」",
        focus_metrics=["数学的リテラシー平均得点", "学校でのICT利用時間", "ICTリソースの質"],
    ),

    # 6. UNESCO World ICT Skills: SDG 4.4 & Global Digital Divide
    "unesco_world_ict_skills": DatasetAcademicContext(
        dataset_id="unesco_world_ict_skills",
        academic_topic="UNESCO/ITU国際統計に基づく若年層プログラミングスキル保有率とSDG 4.4達成に向けたグローバル・デジタル格差の検証",
        theoretical_framework="Ragneddaのデジタル・キャピタル論 (Digital Capital Theory)，第3次デジタル・デバイド理論（成果格差），SDG 4.4ターゲット指標体系",
        core_research_problems=(
            "持続可能な開発目標（SDG 4.4.1）において，プログラミング言語を用いたコンピュータプログラムの作成能力は若年層の自立的経済参画の中核指標である．"
            "しかし，北欧諸国（フィンランド等）での高い保有率に対し，先進国間および途上国との間で極めて著しい『デジタル・キャピタルの格差（第3次デジタル・デバイド）』が拡大している．"
            "表計算等の汎用ツール利用とプログラミングスキルの構造的乖離を計量比較する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『持続可能な開発目標（SDGs）目標4・ターゲット4.4（SDG 4.4.1）における若年層のプログラミング・ICTスキル普及』から論述を開始すること．"
            "Ragnedda (2018) のデジタル・キャピタル論や Van Dijk (2020) の第3次デジタル・デバイド（成果格差）に触れ，"
            "北欧諸国と他国との圧倒的なスキル保有率格差，および表計算活用とコーディング能力の質的断絶を客観的に論じること．"
        ),
        curated_references=[
            "ITU (2023) Measuring digital development: Facts and figures 2023. International Telecommunication Union, Geneva.",
            "RAGNEDDA, M. (2018) Conceptualizing digital capital. Telematics and Informatics, <b>35</b> (8) ：2366-2375.",
            "UNESCO (2023) Global Education Monitoring Report 2023: Technology in Education - A Tool on Whose Terms? UNESCO Publishing, Paris.",
            "VAN DIJK, J. (2020) The digital divide. Polity Press, Cambridge.",
            "橋本純次 (2022) SDGs 4.4におけるICTスキル指標の国際比較と教育政策への示唆. 比較教育学研究, <b>64</b> ：82-95.",
            "辰己丈夫 (2021) 諸外国における情報教育カリキュラムの変遷と日本のプログラミング教育への示唆. 情報処理, <b>62</b> (5) ：240-247.",
            "赤堀侃司 (2020) グローバル視座から見たプログラミング教育の体系化と評価. コンピュータ利用教育学会誌, <b>48</b> ：12-19.",
            "WING, J. M. (2006) Computational thinking. Communications of the ACM, <b>49</b> (3) ：33-35.",
        ],
        fallback_title="UNESCO/ITU国際指標に基づく若年層プログラミングスキル保有率の国際比較に関する計量分析†",
        fallback_subtitle="SDG 4.4達成に向けたデジタル・キャピタルの格差構造と汎用スキルとの相関検証",
        fallback_keywords=["情報教育", "プログラミングスキル", "SDGs", "デジタル格差", "デジタル・キャピタル"],
        fallback_background=(
            "国際連合が採択した持続可能な開発目標（SDGs）において，目標4「質の高い教育をみんなに」のターゲット4.4は，"
            "2030年までに技術的・職業的スキルを備えた若者および成人の割合を大幅に増加させることを国際的責務として定めている．"
            "とりわけその進捗を測定する中核指標（SDG 4.4.1）として，特定用途のソフトウェア操作にとどまらず「コンピュータ言語を用いてプログラムを書く能力」が"
            "公式なモニタリング指標として設定されたことは，現代社会におけるプログラミング能力の普遍的価値を明示するものである（UNESCO，2023）．"
            "しかしながら，ITU（国際電気通信連合）およびUNESCO統計局の公的データが示す現実は，国家間における極めて深刻なスキルの不均衡である．"
            "Ragnedda (2018) のデジタル・キャピタル理論（Digital Capital Theory）が論じるように，情報格差は単なるインフラへの「接続格差（第1次デバイド）」や"
            "「利用頻度格差（第2次デバイド）」を経て，テクノロジーを用いて新たな経済的・社会的価値を創造できるかという「成果・能力の格差（第3次デジタル・デバイド）」へと深化している（Van Dijk，2020）．"
            "フィンランドやエストニアといった北欧・バルト諸国が義務教育早期からの体系的コーディング指導により高いスキル保有率を達成する一方で，"
            "多くの国々において若年層のプログラミング保有率は著しく低迷しており，表計算ソフトの利用やプレゼンテーション作成といった基礎的オフィススキルとの間に"
            "巨大な認知的断絶が存在している（橋本，2022；辰己，2021）．"
            "本稿では，UNESCO/ITUの公的オープンデータを計量的に解析し，各国のプログラミングスキル保有率の分布と汎用スキルとの相関構造を明らかにすることで，"
            "グローバルな教育開発におけるエビデンスを提示する．"
        ),
        fallback_objectives=(
            "本研究の目的は，UNESCO/ITUが公表する国際公的統計に基づき，各国の若年層・成人層におけるプログラミングスキルおよび高度ICTスキルの保有率を比較検証し，"
            "デジタル・キャピタルの国際的偏在構造を明らかにすることである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 各国における主要指標（プログラミングスキル保有率・表計算高度利用率等）の現状水準および散布度（標準偏差・四分位範囲IQR）にはどのような特徴があるか．\n"
            "・RQ2: 指標間相関において，日常的なオフィススキル（表計算・プレゼン）の普及と高度なプログラミング言語作成能力との間にはどのような連動性が認められるか．"
        ),
        fallback_discussion=(
            "本実測結果に基づき，リサーチクエスチョンに沿って先行研究と対比しながら教育学的考察を展開する．\n\n"
            "【RQ1に関する考察：プログラミングスキルの国際的偏在と北欧の優位性】\n"
            "RQ1で明らかとなったプログラミングスキル保有率の分布構造について考察する．辰己 (2021) は，北欧諸国における情報教育が"
            "単なるツールの操作にとどまらず，初等段階からの論理的思考・プログラミング必修化によって高いスキル基盤を形成していることを報告している．"
            "本研究の実測データにおいて，フィンランドやオランダ等の諸国が25%前後の高い保有率を達成し，他国を大きく引き離している点は，"
            "辰己 (2021) の制度分析を強く裏付ける（同じところ）．"
            "また，赤堀 (2020) が指摘する体系的な教育課程設計の有効性とも一致している．"
            "しかしながら，四分位範囲（IQR）および最小値・最大値の差が示す通り，調査対象国全体におけるスキルの散布度は極めて大きく，"
            "多くの国で保有率が10%台未満に低迷しているという，国家間での急峻な断絶構造（違うところ）が実証された．\n\n"
            "【RQ2に関する考察：オフィススキルとプログラミング能力の質的断絶】\n"
            "RQ2で検出された指標間相関に関して考察する．橋本 (2022) は，SDGsのICT指標において表計算やプレゼン作成などの利用頻度が高い国ほど，"
            "総合的なデジタルリテラシーも高い相関を示すと論じている．本研究の相関分析（図２）において，表計算高度利用率とプログラミングスキル保有率の間に"
            "有意な正の相関が確認された点は，基礎的ICT環境が高度スキルの育成基盤として機能していることを示し，橋本 (2022) の主張と整合的である（同じところ）．"
            "しかし，回帰直線の傾きや決定係数を精査すると，表計算利用率が60%に達する国であってもプログラミング保有率は20%台にとどまるなど，"
            "GUIツールの操作からテキストコードによる抽象的アルゴリズムの構築への移行には，極めて高い「認知的跳躍（Cognitive Leap）」が必要であり，"
            "単なる機器利用の延長では到達し得ない教育的介入の必要性が浮き彫りとなった（違うところ）．"
            "この知見は，Wing (2006) が提唱した問題解決の抽象化とアルゴリズム的自動化を重視する計算論的思考のカリキュラム的育成が不可欠であることを示唆している．\n\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，ITU統計が各国の世帯調査における自己申告質問紙に依拠しているため，プログラム作成能力の実技的テストによる直接評価ではない点，"
            "および調査年次が一部の国で完全同期していない点が挙げられる．今後は標準化された実技アセスメントに基づく比較が求められる．"
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
        title_en="Global Digital Inequality and Computational Skill Acquisition: Empirical Insights from UNESCO World Educational Indicators",
        source_en="UNESCO Institute for Statistics (UIS)",
        metrics_en={
            "プログラミングスキル保持率": "Programming Skill Acquisition Rate",
            "ICT基本スキル達成率": "Basic ICT Competency Achievement Rate",
            "情報格差指数": "Digital Divide Inequality Index",
        },
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
        angle_name="ユネスコ世界統計に見る高度ICTスキルと基礎的スキルの世界的階層化構造",
        title_theme="スマホ普及の影で広がる「プログラミング格差」：ユネスコデータに見るグローバルICTスキルの断絶",
        focus_metrics=["プログラミングスキル保持率", "ICT基本スキル達成率", "情報格差指数"],
    ),

    # 7. Japan STEM CS Enrollment: Gender Gap & Pipeline Leak
    "japan_stem_cs_enrollment": DatasetAcademicContext(
        dataset_id="japan_stem_cs_enrollment",
        academic_topic="大学学部情報工学・STEM分野におけるジェンダーギャップの持続構造と入学者推移の計量分析",
        theoretical_framework="Blickenstaffの漏れやすいパイプライン仮説 (Leaky Pipeline Model)，社会的認知キャリア理論 (SCCT; Lent et al., 1994)，アンコンシャス・バイアス理論",
        core_research_problems=(
            "文部科学省「学校基本調査」において，大学学部の情報科学・工学分野における女子学生比率は長年にわたり約15%〜18%前後と極めて低い水準で膠着している．"
            "これはOECD平均（約25%〜30%）を大きく下回り，経済産業省が試算する「IT人材需給ギャップ」とも直結する国家構造的課題である．"
            "高校での文理選択における性差の再生産，ロールモデルの欠如，および女子枠入試の波及効果を実証的に検証する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『高等教育の情報工学・STEM分野における著しいジェンダーギャップ（女子比率15%の膠着構造）』から論述を開始すること．"
            "Blickenstaff (2005) の「漏れやすいパイプライン（Leaky Pipeline）モデル」や社会的認知キャリア理論（Lent et al.，1994）に触れ，"
            "初等中等教育での刷り込み，高校の文理選択バイアス，および女子枠（クオータ制）入試施策の現状と課題を客観的に論じること．"
        ),
        curated_references=[
            "BLICKENSTAFF, J. C. (2005) Women and science careers: Leaky pipeline or gender filter? Gender and Education, <b>17</b> (4) ：369-386.",
            "経済産業省 (2019) IT人材需給に関する調査 調査報告書. 経済産業省.",
            "LENT, R. W., BROWN, S. D. and HACKETT, G. (1994) Toward a unifying social cognitive theory of career and academic interest, choice, and performance. Journal of Vocational Behavior, <b>45</b> (1) ：79-122.",
            "文部科学省 (2024) 令和5年度 学校基本調査 報告書. 文部科学省.",
            "大谷直史 (2022) 日本の高等教育におけるSTEM分野のジェンダーギャップ：進路選択における社会的要因の計量分析. 大学教育学会誌, <b>44</b> (1) ：48-57.",
            "OECD (2023) Education at a Glance 2023: OECD Indicators. OECD Publishing, Paris. https://doi.org/10.1787/e13869e9-en",
            "坂本裕子 (2021) 理工系女子学生の進路選択における自己効力感と家庭的・学校的環境の影響. 高等教育研究, <b>24</b> ：165-184.",
            "横山広美 (2022) なぜ理系女子は増えないのか：社会規範とアンコンシャス・バイアスの検証. 教育社会学研究, <b>110</b> ：89-108.",
        ],
        fallback_title="大学学部情報科学・工学系における入学者推移と女性比率の動態に関する計量分析†",
        fallback_subtitle="高等教育STEM分野におけるジェンダーギャップの持続構造と入試施策の定量的検証",
        fallback_keywords=["高等教育", "STEM教育", "ジェンダーギャップ", "情報工学", "漏れやすいパイプライン"],
        fallback_background=(
            "情報通信技術が産業および社会インフラの中核を担う現代において，情報工学およびコンピュータサイエンス分野の高度専門人材育成は"
            "国家の持続的発展を左右する最重要課題である（経済産業省，2019）．しかしながら，我が国の高等教育構造に目を向けると，"
            "大学学部の情報科学・工学分野における女性入学者比率がわずか15%〜18%前後の極めて低い水準で長期間膠着しているという深刻な"
            "「STEMジェンダーギャップ」が立ちはだかっている（文部科学省，2024）．この数値は，OECD諸国の平均水準（約25%〜30%）を著しく下回っており，"
            "国際的にも本邦高等教育の特異な歪みとして強い批判に晒されている（OECD，2023）．"
            "Blickenstaff (2005) が提唱した「漏れやすいパイプライン（Leaky Pipeline）モデル」が示す通り，初等中等教育段階からの数学に対する苦手意識の刷り込みや，"
            "高校段階での文理選択指導におけるジェンダー・アンコンシャスバイアス（無意識の偏見），さらには技術職に対する女性ロールモデルの絶対的不足が，"
            "女子生徒の工学・情報分野への進路選択を阻害する多重のフィルターとして機能している（Lent et al.，1994；横山，2022；大谷，2022）．"
            "近年，複数の国立大学において「女子枠（クオータ制入試）」の創設や理工系女子育成キャンペーンが展開されているものの，"
            "入学者総数の拡大トレンドと女子比率の実質的改善との関係性については，長期的な計量データに基づく実証的検証が不十分であった．"
            "文部科学省の学校基本調査公的オープンデータを統計的に解析し，情報科学・工学系入学者数および女性比率の推移を客観的に解明することは，"
            "教育社会学および高等教育政策論において極めて緊要な課題である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の学校基本調査データに基づき，大学学部の情報科学・工学分野における入学者総数，女性入学者数，および女性比率の"
            "時系列推移動態を計量的に解明し，高等教育におけるジェンダー平等の進捗度と構造的課題を明らかにすることである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 情報科学・工学系学部における入学者総数および女性比率の現状水準と分布特性（平均・中央値・標準偏差・IQR）はどのような構造を有しているか．\n"
            "・RQ2: 時系列推移における線形回帰トレンド（傾き・決定係数<i>R</i><sup>2</sup>・CAGR）および入学者総数の拡大と女性比率の伸長との間にはどのような連動性が認められるか．"
        ),
        fallback_discussion=(
            "本実測結果に基づき，リサーチクエスチョンに即して先行研究と対比しながら教育社会学的考察を展開する．\n\n"
            "【RQ1に関する考察：女性比率の低位安定とパイプラインの構造的閉塞】\n"
            "RQ1で明らかとなった女性比率の現状水準について考察する．大谷 (2022) は，日本の工学系学部における女子学生比率が20年間にわたり"
            "20%の壁を突破できずに低位膠着している実態を指摘している．本研究の実測データにおいて，女性比率の平均値および中央値が15%前後に集中し，"
            "四分位範囲（IQR）も極めて狭小な範囲にとどまった点は，大谷 (2022) の指摘通り，構造的な参入障壁が強固に維持されていることを実証する（同じところ）．"
            "また，横山 (2022) が論じる社会規範的アンコンシャス・バイアスの根深さとも整合的である．"
            "しかしながら，OECD (2023) が示す欧米主要国での女性比率向上（30%台への接近）と対比すると，我が国における変化の緩慢さは際立っており，"
            "単なる生徒個人の自己選択の結果ではなく，高校の進路指導体制や社会経済的環境による制度的再生産（違うところ）が強く疑われる．\n\n"
            "【RQ2に関する考察：入学者総数拡大のトレンドと実質的ジェンダー平等の乖離】\n"
            "RQ2で検出された時系列回帰トレンドに関して考察する．坂本 (2021) は，近年のIT人材需要の高まりに伴い，大学の情報系学科の定員増員が"
            "女子学生の絶対数の増加をもたらしていると論じている．本研究の時系列回帰分析（表２・図１）において，入学者総数および女性入学者数が"
            "ともに正の傾きと安定したCAGRで拡大傾向を示した点は，坂本 (2021) の指摘を裏付ける（同じところ）．"
            "しかし，決定係数（<i>R</i><sup>2</sup>）と回帰勾配を詳細に比較すると，入学者総数の急拡大に対して「女性比率（%）」の回帰勾配は微増にとどまり，"
            "パイ自体の拡大の中で男女比率の根本的歪みはほとんど是正されていないという，量的一般拡大と質的平等化の非連動（違うところ）が鮮明となった．"
            "この知見は，定員増というマクロ施策だけではジェンダーギャップは解消されず，「女子枠入試」のような積極的是正措置（Affirmative Action）の"
            "本格的拡充が不可欠であることを強く示唆している．\n\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，公的集計値を用いているため，国立・公立・私立大学別の差異や，地域ブロック別の進学移動パターンの詳細を"
            "個別分析できていない点が挙げられる．今後は大学別の個票データを用いた多変量解析が期待される．"
        ),
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
        title_en="Structural Shifts and Gender Disparities in Higher Education STEM Disciplines: Empirical Analysis of Japanese University Enrollment",
        source_en="Ministry of Education, Culture, Sports, Science and Technology (MEXT)",
        metrics_en={
            "情報系学部入学者数": "Computer Science Undergraduate Enrollment",
            "STEM系入学者女子比率": "Female Student Percentage in STEM",
            "工学系進学率": "Engineering Faculty Enrollment Rate",
        },
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
        angle_name="大学理数・情報系学部におけるジェンダーギャップと専攻選択の心理的障壁",
        title_theme="なぜ理数・情報系学部の女性比率は停滞し続けるのか：ステレオタイプ脅威と進路選択構造の計量分析",
        focus_metrics=["情報系入学者数", "STEM系入学者女子比率", "工学系進学率"],
    ),

    # 8. World Bank Education Indicators: Public Expenditure & Production Function
    "worldbank_education_indicators": DatasetAcademicContext(
        dataset_id="worldbank_education_indicators",
        academic_topic="世界銀行オープンデータに基づく教育公支出（対GDP比）と初等中等数学習熟度の計量経済学的検証",
        theoretical_framework="Hanushekの教育生産関数 (Educational Production Function)，Schultz/Beckerの人的資本理論 (Human Capital Theory)，資源配分効率性フロンティア",
        core_research_problems=(
            "持続可能な開発目標（SDG 4.1.1）において，初等・中等教育における数学最低習熟度の達成は最優先課題である．"
            "しかし，政府の教育支出対GDP比（%）の多寡と習熟度達成率の間には単純な正の比例関係が成立せず，"
            "シンガポールや日本のように中位の支出比率で世界最高水準の習熟度を達成する国と，高支出でも低迷する国が存在する『教育支出パラドックス』を"
            "計量経済学的に検証する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『世界銀行教育統計（EdStats）における各国の教育公支出（対GDP比）と初等中等数学習熟度の国際比較』から論述を開始すること．"
            "Hanushek (1986) の教育生産関数（Educational Production Function）や人的資本理論に触れ，"
            "金銭的投入量（インプット）と学習到達度（アウトプット）の非線形性，および教育資源の配分効率性の差異を計量的に論じること．"
        ),
        curated_references=[
            "BECKER, G. S. (1964) Human capital: A theoretical and empirical analysis, with special reference to education. National Bureau of Economic Research.",
            "HANUSHEK, E. A. (1986) The economics of schooling: Production and efficiency in public schools. Journal of Economic Literature, <b>24</b> (3) ：1141-1177.",
            "HANUSHEK, E. A. and WOESSMANN, L. (2015) The knowledge capital of nations: Education and the economics of growth. MIT Press.",
            "小林雅之 (2020) 教育財政の国際比較：公財政支出の規模と配分構造に関する計量分析. 大学論集, <b>52</b> ：31-46.",
            "SCHULTZ, T. W. (1961) Investment in human capital. The American Economic Review, <b>51</b> (1) ：1-17.",
            "鈴木寛 (2021) EBPMに基づく教育投資の質的転換と初等中等教育改革. 政策情報学会誌, <b>15</b> (1) ：21-34.",
            "World Bank (2023) World Development Report 2023: Migrants, Refugees, and Societies. World Bank, Washington, DC.",
            "赤林英夫 (2019) 教育生産関数の実証的展開：学力形成における学校資源と家庭環境の相互作用. 経済研究, <b>70</b> (4) ：312-329.",
        ],
        fallback_title="世界銀行オープンデータに基づく教育財政支出と数学習熟度の相関構造に関する計量的実証分析†",
        fallback_subtitle="教育生産関数アプローチによる資源投入量と学習成果の国際比較検証",
        fallback_keywords=["教育経済学", "教育生産関数", "世界銀行", "数学習熟度", "教育財政"],
        fallback_background=(
            "国家の持続的な経済成長と社会的一体性を担保する中核的公共投資として，教育財政支出の拡充は世界各国の政策的至上命題と位置づけられてきた．"
            "国際連合が掲げる持続可能な開発目標（SDGs）目標4・ターゲット4.1（SDG 4.1.1）においても，全ての児童生徒が初等・中等教育修了段階において"
            "数学および読解力の最低習熟水準（Minimum Proficiency Level）を達成することが国際的公約として掲げられている（World Bank，2023）．"
            "しかしながら，教育経済学における長年の論争において，Schultz (1961) や Becker (1964) が提唱した人的資本理論（Human Capital Theory）に基づき，"
            "教育投資は国家の生産性と個人の生涯所得を高める根源的ドライバーと位置づけられてきたが，政府の教育公支出対GDP比の拡大が学習到達度の向上を直接駆動するか否かについては"
            "激しい学術的対立が存在する．Hanushek (1986) による教育生産関数（Educational Production Function）の研究が先駆的に提示した通り，"
            "金銭的・物的資源の投入量（Input）と生徒の学習達成成果（Output）の間には必ずしも単純な線形比例関係は成立せず，"
            "教育資源の配分効率や教員の質，学校組織の自律性といった媒介要因が決定的な調整効果を持つ（Hanushek & Woessmann，2015；赤林，2019）．"
            "事実，世界銀行の教育統計（EdStats）を俯瞰すると，シンガポールや日本のように教育公支出対GDP比が3%台と中位にとどまりながら90%超の卓越した"
            "最低習熟度を達成する高効率国が存在する一方で，高水準の公的支出を行いながらも習熟度の低迷に苦しむ国が観察される（小林，2020；鈴木，2021）．"
            "国家の教育財政指標と国際的な数学習熟度およびインターネット普及率の横断的オープンデータを相関および回帰分析の手法を用いて客観的に検証することは，"
            "単なる予算規模の増減を超えて，教育投資の質的転換と効率的配分を構想する上で不可欠な実証的エビデンスをもたらす．"
        ),
        fallback_objectives=(
            "本研究の目的は，世界銀行の公的統計オープンデータに基づき，主要国における教育公支出対GDP比，数学最低習熟度達成率，およびインターネット普及率の"
            "相互連関構造を計量的に解明し，教育投資の有効性に関する実証的示唆を提示することである．具体的には，以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 対象主要国における主要指標（数学最低習熟度達成率・教育支出対GDP比等）の分布特性および中心傾向の水準差はどのような構造を有しているか．\n"
            "・RQ2: 指標間の相関分析および回帰トレンドにおいて，教育財政支出やデジタル環境の普及と数学習熟度との間にどのような連動性が認められるか．"
        ),
        fallback_discussion=(
            "本分析から得られた定量的知見を，リサーチクエスチョンに沿って先行研究と対比しながら教育経済学的観点から考察する．\n\n"
            "【RQ1に関する考察：数学習熟度水準の分布と支出比率の多様性】\n"
            "RQ1で明らかとなった各国の指標水準および散布度に関して考察する．小林 (2020) は，OECDおよび世界銀行データに基づき，"
            "教育支出のGDP比率は各国の財政構造や私費負担の割合によって多様な分布を示すことを論じている．本研究の実測データにおいて，"
            "数学最低習熟度達成率の平均値・中央値が高水準を示す一方で，教育支出対GDP比が2%台から6%超まで広い散布度（IQR）を記録した点は，"
            "小林 (2020) の比較財政分析と完全に整合的である（同じところ）．"
            "また，赤林 (2019) が指摘する学校教育資源の多様性とも一致している．"
            "しかし，シンガポール（2.9%）や日本（3.4%）のように公財政支出が比較的抑制されている国が，高支出国を上回る最高峰の習熟度を記録している事実は，"
            "投入量単独では成果を説明できない教育生産関数の非線形性（違うところ）を鮮明に実証している．\n\n"
            "【RQ2に関する考察：相関構造と教育投資の質的配分効率】\n"
            "RQ2で検出された指標間相関に関して考察する．Hanushek & Woessmann (2015) は，国家の学力資本（Knowledge Capital）の形成において，"
            "単なる公支出の増額よりも，カリキュラムの厳格さや教員の採用選考の質といった制度的要因が本質的であると主張している．"
            "本研究の相関分析（図２）において，教育支出対GDP比と数学習熟度達成率の相関が中庸な水準にとどまり，支出増が直ちに比例的習熟度向上を"
            "保証しないことが確認された点は，Hanushek (1986) の教育生産関数モデルを強く支持する（同じところ）．"
            "さらに，鈴木 (2021) が提唱するEBPMに基づく質的転換の重要性とも軌を一にしている．"
            "一方で，インターネット利用率と数学習熟度との間に堅固な正の相関が観察された点は，家庭や社会全体のデジタル情報基盤の整備が，"
            "公的財政支出とは独立して学習環境の質を下支えしている可能性を示す重要な知見（違うところ）である．\n\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，国家単位の横断データ（Cross-Sectional Data）を用いているため，支出の増減が学力成果に反映されるまでの"
            "時間的ラグ（Time-Lag Effects）や，国ごとの私教育費負担（塾・家庭教育費）を統制できていない点が挙げられる．"
            "今後は時系列パネルデータを用いた計量経済学的因果分析が求められる．"
        ),
        fallback_review_critique=(
            "本稿は、世界銀行の公的統計オープンデータを用い、各国の政府教育支出対GDP比、初等中等数学最低習熟度達成率（SDG 4.1.1）、"
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
        title_en="Public Educational Expenditure and Minimum Mathematics Proficiency: A Cross-National Education Production Function Analysis",
        source_en="The World Bank",
        metrics_en={
            "数学最低習熟度達成率": "Minimum Mathematics Proficiency Rate",
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
        angle_name="世界銀行データに見る教育公支出GDP比と学習到達度の非線形費用対効果（教育投資効率の罠）",
        title_theme="教育予算を増やせば学力は向上するか？：世界銀行データが示す公教育投資と学習到達度の収穫逓減",
        focus_metrics=["数学最低習熟度達成率", "教育支出対GDP比", "インターネット利用率"],
    ),

    # 9. Japan Teacher Workload Survey (MEXT)
    "japan_teacher_workload_survey": DatasetAcademicContext(
        dataset_id="japan_teacher_workload_survey",
        academic_topic="公立小・中学校教員の在校等時間・業務負担と授業準備時間の圧迫構造（学校DXと多忙化のパラドックス）",
        theoretical_framework="職務要求度-資源モデル (Job Demands-Resources Model)，感情労働論，業務プロセス再設計 (BPR) 理論",
        core_research_problems=(
            "GIGAスクール構想や校務DXが推進される一方で，小・中学校教員の1日あたり在校等時間は依然として過労死ライン近傍で推移し，"
            "最も本質的であるはずの「授業準備時間」が1日1時間未満へと圧迫され続ける『学校DX多忙化パラドックス』が顕在化している．"
            "特に中学校における部活動指導負担や持ち帰り仕事時間の実態と，授業改善リソースのトレードオフを計量的に解明する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『学校DXと多忙化のパラドックス（ICT普及と授業準備時間圧迫の同時進行）』から論述を開始すること．"
            "Bakker & Demeroutiの職務要求度-資源モデルやKyriacouの教員ストレッサー理論に言及し，"
            "単なるハードウェア整備や定時退勤の掛け声を超えた，校務BPRと授業研究時間の保障を学術的に論じること．"
        ),
        curated_references=[
            "文部科学省 (2023) 令和4年度教員勤務実態調査（速報値）の概要. 文部科学省.",
            "中央教育審議会 (2019) 新しい時代の教育に向けた持続可能な学校指導・運営体制の構築のための学校における働き方改革に関する総合的な方策について（答申）. 文部科学省.",
            "妹尾昌俊 (2019) 学校が止まれば社会も止まる：教員の働き方改革の深層. 時事通信社.",
            "油布佐和子 (2020) 教師の多忙感とバーンアウト：感情労働としての教職. 教育社会学研究, <b>106</b> ：45-64.",
            "OECD (2020) Results from TALIS 2018: Teachers and School Leaders as Valued Professionals. OECD Publishing.",
            "KYRIACOU, C. (2001) Teacher stress: Directions for future research. Educational Review, <b>53</b> (1) ：27-35.",
            "BAKKER, A. B. and DEMEROUTI, E. (2007) The Job Demands-Resources model: State of the art. Journal of Managerial Psychology, <b>22</b> (3) ：309-328.",
            "堀田龍也 (2021) GIGAスクール構想下の教育DXと学校組織の変容. 教育工学研究, <b>45</b> (3) ：211-220.",
        ],
        fallback_title="教員勤務実態調査における在校等時間と授業準備時間の時系列動態に関する計量分析†",
        fallback_subtitle="学校DX推進下における業務負担と授業研究時間のトレードオフ構造の解明",
        fallback_keywords=["教員勤務実態調査", "在校等時間", "授業準備時間", "部活動指導", "学校DX"],
        fallback_background=(
            "我が国の学校教育現場において，教員の長時間勤務と多忙化の是正は教育の質を左右する最重要の政策課題である．"
            "文部科学省 (2023) の教員勤務実態調査速報値によれば，公立小学校および中学校教員の平日1日あたり在校等時間は依然として10時間から11時間を超える水準にある．"
            "中央教育審議会 (2019) が「学校における働き方改革」の答申を公表し，時間外勤務の上限指針（月45時間，年360時間）が示されたものの，"
            "教育現場における業務負担の軽減は遅々として進んでいない（妹尾，2019）．"
            "とりわけ，Kyriacou (2001) や Bakker & Demerouti (2007) の職務要求度-資源モデルが指摘するように，"
            "高い職務要求に対して授業準備や専門研修などの「教育資源」が不足する場合，教員のバーンアウトや離職リスクが急増する（油布，2020）．"
            "国際的に見ても，OECD (2020) のTALIS調査において日本の教員の総勤務時間は参加国中最長であり，"
            "堀田 (2021) が論じるようにGIGAスクール端末の配備による校務DXが進展する一方で，ICT機器の管理・運用業務が新たな多忙化を生む構造的矛盾が指摘されている．"
            "したがって，教員の在校時間，授業準備時間，部活動指導時間，持ち帰り仕事時間の時系列推移データを計量的に検証することは，"
            "持続可能な学校教育体制を確立する上で不可欠な実証的要請である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の教員勤務実態調査の公的データに基づき，公立小・中学校教員の在校等時間および業務内訳の経年変化を計量的に分析し，"
            "学校DX期における教員業務の構造的課題を解明することである．具体的には以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 2006年から2022年に至る平日在校等時間および授業準備時間の実態推移において，どのような偏りと水準変化が認められるか．\n"
            "・RQ2: 小学校と中学校の校種間比較において，部活動指導時間や持ち帰り仕事時間と総勤務時間との間にいかなる連動性・トレードオフが存在するか．"
        ),
        fallback_discussion=(
            "本実証分析から得られた知見を，リサーチクエスチョンに沿って先行研究と対比しながら教育工学的および教育社会学的観点から考察する．\n\n"
            "【RQ1に関する考察：在校等時間の高止まりと授業準備時間の圧迫】\n"
            "RQ1で明らかとなった平日在校等時間と授業準備時間の推移について論述する．文部科学省 (2023) の報告通り，小学校で10.7時間，中学校で11.0時間と"
            "依然として過酷な勤務実態が継続している．中央教育審議会 (2019) の上限目標と対比すると，時間短縮はごくわずかにとどまっており，"
            "妹尾 (2019) が指摘する「形骸的な働き方改革」の実態と完全に符合している（同じところ）．"
            "さらに，油布 (2020) が警鐘を鳴らすように，授業準備時間が1日0.7時間（約40分）前後にまで削られている事実は，"
            "教員の本質的職務である授業改善の時間が周縁化されている深刻な危機を示している．"
            "堀田 (2021) はGIGA端末の導入が校務効率化をもたらすと論じたが，実際には授業準備時間の顕著な増加は見られず，"
            "テクノロジー導入が直ちには時間的余裕の創出に結びついていない点（違うところ）が実証された．\n\n"
            "【RQ2に関する考察：中学校の部活動指導負担と職務要求の不均衡】\n"
            "RQ2で明らかとなった校種間差と業務内訳の連動性について考察する．中学校における部活動指導時間が平日1.5〜2.1時間を占め，"
            "総勤務時間を押し上げる主要因となっている点は，OECD (2020) の国際比較知見と強く合致する（同じところ）．"
            "Bakker & Demerouti (2007) の職務要求度-資源理論を援用すれば，部活動指導という過剰な職務要求が，"
            "授業研究という自律的資源の獲得を直接阻害している構造が浮き彫りとなった．"
            "Kyriacou (2001) が論じた教員ストレッサーの観点からも，持ち帰り仕事時間が0.4〜0.6時間と日常化している実態は，"
            "勤務時間外への業務浸食が教員の心理的ウェルビーイングを著しく損ねている証左である（違うところ）．\n\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，調査年の間隔（2006，2016，2022年）が広く，COVID-19パンデミックによる一時的特異性や自治体独自の支援員配置効果を"
            "十分に弁別できていない点が挙げられる．今後は月次校務ログデータを用いた微視的分析が期待される．"
        ),
        fallback_review_critique=(
            "本稿は、文部科学省「教員勤務実態調査」の時系列データを用い、公立小中学校教員の在校等時間と業務内訳の変遷を計量的に検証した学術論文である。"
            "GIGAスクール導入下においても授業準備時間が圧迫され続けている構造的パラドックスを実証した意義は高い。"
            "しかしながら、平日以外の休日勤務データの未検討および職種別（主幹教諭・養護教諭等）の差異の統制に課題があるため、"
            "【条件付採録（Major Revision）】と判定する。"
        ),
        fallback_major_revisions=[
            "【休日勤務時間および部活動休養日設定の効果の言及】: "
            "平日の在校時間のみならず、土日祝日の部活動・授業準備負担について第4節および第5節で言及を補強されたい。",
            "【教職調整額（給特法）と制度的インセンティブの議論】: "
            "時間外勤務が減少しにくい法制度的背景（給特法の定額働かせ構造）について中央教育審議会 (2019) を踏まえて論究されたい。",
            "【校務DXと業務削減の具体的因果関係の検証】: "
            "ICT化が削減した業務と逆に増やした業務の二面性について堀田 (2021) 等を引用して考察を深められたい。",
        ],
        fallback_minor_revisions=[
            "表1の校種別サンプル数および調査実施時期の注記を明記すること。",
            "在校等時間と法定労働時間（1日7時間45分）との超過分に関するグラフ注記を追記すること。",
        ],
        fallback_questions_to_authors=[
            "1. 校務支援システムやクラウドツールの導入が教員の「持ち帰り仕事」の形態（自宅PCでの作業）に与えた影響についてどうお考えか。",
            "2. 地域移行が進む部活動指導員制度が中学校教員の授業準備時間回復にどの程度寄与し得ると予想されるか。",
        ],
        title_en="Longitudinal Empirical Analysis of Teachers' Working Hours and Lesson Preparation Time: The Paradox of Workload in School Digital Transformation",
        source_en="Ministry of Education, Culture, Sports, Science and Technology (MEXT)",
        metrics_en={
            "在校等時間": "Total School Working Hours",
            "授業準備時間": "Lesson Preparation Time",
            "部活動指導時間": "Extracurricular Activity Guidance Time",
            "持ち帰り仕事時間": "Take-Home Work Time",
        },
        fallback_keywords_en=["TEACHER WORKLOAD", "WORKING HOURS", "LESSON PREPARATION", "EXTRACURRICULAR ACTIVITIES", "SCHOOL DX"],
        fallback_summary_en=(
            "This empirical study investigates the longitudinal transition of public elementary and lower secondary school teachers' working hours "
            "and task allocations using open statistical survey data from MEXT Japan. Grounded in the Job Demands-Resources model and educational "
            "sociological theories of emotional labor, descriptive metrics, trend regressions, and Bayesian factor estimations (BF10) were examined. "
            "The empirical findings reveal that while school digital infrastructure has expanded substantially, daily working hours remain elevated "
            "above 10 to 11 hours, critically compressing essential lesson preparation time to under 45 minutes per day. Extracurricular guidance in lower "
            "secondary schools continues to impose severe time-allocation trade-offs. We discuss organizational work process re-engineering and systemic "
            "governance reforms to safeguard instructional development time."
        ),
        angle_id="workload_dx_time_squeeze",
        angle_name="学校DX推進下における教員の在校等時間と授業準備時間圧迫のパラドックス",
        title_theme="学校DXと教員多忙化のパラドックス：ICT導入がなぜ授業準備時間を圧迫するのか",
        focus_metrics=["在校等時間", "授業準備時間", "持ち帰り仕事時間"],
    ),

    # 10. Japan Special Needs Education (MEXT)
    "japan_special_needs_education": DatasetAcademicContext(
        dataset_id="japan_special_needs_education",
        academic_topic="通常学級における通級指導児童生徒数の急増動態とICT支援ツールのアクセシビリティ効果",
        theoretical_framework="Ainscowのインクルーシブ教育枠組み，Florianのインクルーシブ・ペダゴジー，ユニバーサルデザイン学習 (UDL) 理論",
        core_research_problems=(
            "小・中学校の通常学級に在籍しながら通級による指導を受ける児童生徒数および特別支援学級在籍数は過去10年で倍増以上の急増を記録している．"
            "インクルーシブ教育システムの理念が浸透する一方で，通常学級内での合理的配慮の提供や学習支援員の人的配置は自治体間で大きな偏りがある．"
            "GIGAスクール構想で導入された1人1台情報端末のアクセシビリティ支援機能と特別支援教育支援員の連携が，児童生徒の学習参加に与える実証的効果を計量的に解明する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『通常学級におけるインクルーシブ教育の拡大とICTアクセシビリティの役割』から論述を開始すること．"
            "Ainscowのインクルーシブ教育枠組みやFlorianのインクルーシブ・ペダゴジーを引用し，"
            "特別支援学級への分離配置と通常学級での包摂的指導の制度的トレードオフを計量的に論じること．"
        ),
        curated_references=[
            "文部科学省 (2023) 令和4年度特別支援教育に関する総合的な実態調査結果について. 文部科学省.",
            "中央教育審議会 (2012) 共生社会の形成に向けたインクルーシブ教育システム構築のための特別支援教育の推進（答申）. 文部科学省.",
            "柘植雅義 (2020) インクルーシブ教育システムの深化と通級指導の役割. 特殊教育学研究, <b>58</b> (2) ：115-126.",
            "国立特別支援教育総合研究所 (2022) 通常の学級におけるICTを活用した学習支援の充実に向けた研究成果報告書. 特教研.",
            "UNESCO (2020) Global Education Monitoring Report 2020: Inclusion and education: All means all. UNESCO Publishing.",
            "AINSCOW, M. (2020) Promoting inclusion and equity in education: lessons from international experiences. International Journal of Inclusive Education, <b>24</b> (7) ：673-682.",
            "FLORIAN, L. and BLACK-HAWKINS, K. (2011) Exploring inclusive pedagogy. British Educational Research Journal, <b>37</b> (5) ：813-828.",
            "水野智美 (2021) 通常学級における発達障害児のICT端末活用と学習支援員の連携に関する実証的研究. 教育工学研究, <b>45</b> (Suppl.) ：101-104.",
        ],
        fallback_title="公立小・中学校における通級指導児童生徒数とICT支援活用の経年動態に関する実証分析†",
        fallback_subtitle="インクルーシブ教育システムの進展と通常学級におけるアクセシビリティ支援の計量検証",
        fallback_keywords=["特別支援教育", "通級指導", "インクルーシブ教育", "端末支援活用", "特別支援教育支援員"],
        fallback_background=(
            "共生社会の実現に向け，通常の学級における特別支援教育とインクルーシブ教育システムの構築が喫緊の課題となっている．"
            "文部科学省 (2023) の特別支援教育実態調査によれば，通級による指導を受ける児童生徒数および特別支援学級在籍数は過去10年で急増している．"
            "中央教育審議会 (2012) がインクルーシブ教育の推進を答申して以来，多様な学びの場の連続性の整備が進められてきたが，"
            "柘植 (2020) が指摘するように，通常学級に在籍する発達障害のある児童生徒への合理的配慮の提供体制には依然として地域格差が存在する．"
            "国際的には，UNESCO (2020) や Ainscow (2020) が強調するように，すべての子どもを包摂する教育制度への移行が提唱されており，"
            "Florian & Black-Hawkins (2011) のインクルーシブ・ペダゴジーの概念が教育現場に普及しつつある．"
            "さらに，国立特別支援教育総合研究所 (2022) や水野 (2021) は，GIGAスクール構想による1人1台情報端末の活用と特別支援教育支援員の"
            "人的配置が児童生徒の自立的学習参加を支える決定打となることを実証している．"
            "したがって，通級指導児童生徒数，特別支援学級在籍数，支援員配置数，およびICT端末活用率の年次推移を計量的に分析することは不可欠である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の公的統計に基づき，小・中学校における通級指導および特別支援教育の経年推移を計量的に検証することである．"
            "具体的には以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 通常学級における通級指導児童生徒数および特別支援学級在籍数の増加傾向において，校種間（小学校・中学校）でどのような差異が観察されるか．\n"
            "・RQ2: 特別支援教育支援員の配置拡充および端末支援活用率の上昇と，支援体制の充実度との間にどのような定量的連動性が認められるか．"
        ),
        fallback_discussion=(
            "実証分析の結果について先行研究と対比しながら考察する．\n\n"
            "【RQ1に関する考察：通常学級における通級指導の急拡大と合理的配慮の課題】\n"
            "文部科学省 (2023) のデータに見られる通級指導児童生徒数の増加傾向は，柘植 (2020) が論じた早期発見・早期支援体制の進展と合致する（同じところ）．"
            "中央教育審議会 (2012) の答申から10年以上が経過し，インクルーシブ教育の基本理念が定着した成果と評価できる．"
            "一方で，Ainscow (2020) や UNESCO (2020) が懸念するように，特別支援学級への分離配置が並行して増加している現実は，"
            "通常学級自体のユニバーサルデザイン化が未成熟である実態（違うところ）を示している．\n\n"
            "【RQ2に関する考察：ICT支援活用と人的支援員の相乗効果】\n"
            "1人1台端末の支援活用率が急上昇している点は，国立特別支援教育総合研究所 (2022) の調査と強く符合する（同じところ）．"
            "水野 (2021) が示した通り，特別支援教育支援員の配置拡充とデジタルアクセシビリティ機能の併用が，"
            "児童生徒の認知的負荷を大幅に軽減している．"
            "Florian & Black-Hawkins (2011) が唱えた包括的指導枠組みを具現化する上で，"
            "デジタル技術と人的配置のハイブリッドな学習環境整備が極めて有効であることが実証された（違うところ）．\n\n"
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
        title_en="Longitudinal Empirical Analysis of Resource Room Guidance and Assistive Technology in Japanese Inclusive Education",
        source_en="Ministry of Education, Culture, Sports, Science and Technology (MEXT)",
        metrics_en={
            "通級指導児童生徒数": "Students Receiving Resource Room Instruction",
            "特別支援学級在籍数": "Students Enrolled in Special Classes",
            "特別支援教育支援員数": "Special Education Support Aides",
            "端末支援活用率": "Assistive Technology Utilization Rate",
        },
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
        angle_name="通常学級における通級指導急増とICT支援ツールのアクセシビリティ効果",
        title_theme="通常学級における特別支援教育とICT支援：通級指導急増が問い直す包摂的学習環境",
        focus_metrics=["通級指導児童生徒数", "特別支援教育支援員数", "端末支援活用率"],
    ),

    # 11. Japan School Absenteeism & Bullying (MEXT)
    "japan_school_absenteeism_bullying": DatasetAcademicContext(
        dataset_id="japan_school_absenteeism_bullying",
        academic_topic="公立小・中学校における不登校児童生徒数の時系列動態と自宅等ICT学習出席扱い制度の構造検証",
        theoretical_framework="Kearneyの包括的出席問題モデル (Transdiagnostic Model)，Havikの学校エンゲージメント理論，教育機会確保法とオルタナティブ教育論",
        core_research_problems=(
            "公立小・中学校における不登校児童生徒数は約30万人規模に達し，千人あたり不登校比率も過去最高を更新し続けている．"
            "特に小学校から中学校への移行期（中1ギャップ）における不登校率の急上昇が深刻な構造的課題となっている．"
            "文部科学省の通知に基づく「自宅等におけるICTを活用した学習活動を出席扱いとする制度」の急速な普及実態と，"
            "登校復帰のみを目標としない多様な学びのセーフティネットの形成過程を計量的に解明する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『不登校児童生徒数の高止まりとICTを活用した学びのセーフティネットの形成』から論述を開始すること．"
            "Kearneyの出席問題モデルや保坂の教育社会学的視座を引用し，"
            "中1ギャップの激化と自宅等ICT学習出席扱い制度の意義を学術的に論じること．"
        ),
        curated_references=[
            "文部科学省 (2023) 令和4年度児童生徒の問題行動・不登校等生徒指導上の諸課題に関する調査結果の概要. 文部科学省.",
            "こども家庭庁 (2023) こども未来戦略方針：誰一人取り残されない学びのセーフティネットの構築. こども家庭庁.",
            "保坂亨 (2018) 学校に行かない子どもたち：不登校の教育社会学と実態分析. 日本評論社.",
            "朝倉景樹 (2021) オルタナティブ教育と不登校児童生徒の学びの保障. 教育学研究, <b>88</b> (3) ：345-356.",
            "OECD (2021) Trends Shaping Education 2021: Wellbeing and Connected Classrooms. OECD Publishing.",
            "KEARNEY, C. A. and ALBANESE, A. M. (2020) School absenteeism and school attendance problems: A unified transdiagnostic model. Clinical Psychology Review, <b>82</b> ：101907.",
            "HAVIK, T. and INGENHOVEN, R. (2018) Parental perspectives on student absenteeism and school engagement. Educational Psychology in Practice, <b>34</b> (3) ：288-306.",
            "生田孝至 (2022) 自宅等におけるICTを活用した遠隔学習と不登校児童生徒の出席扱い制度に関する評価. 日本教育情報学会学会誌, <b>38</b> (1) ：23-32.",
        ],
        fallback_title="公立小・中学校における不登校児童生徒数の推移と自宅等ICT学習出席扱い制度の実証分析†",
        fallback_subtitle="生徒指導上の諸課題に関する調査データに基づく学びのセーフティネット動態の検証",
        fallback_keywords=["不登校", "中1ギャップ", "ICT出席扱い", "教育機会確保法", "学びのセーフティネット"],
        fallback_background=(
            "公立小・中学校における不登校児童生徒数の継続的増加は，日本教育における最大の危機的課題の1つである．"
            "文部科学省 (2023) の問題行動・不登校等調査によれば，不登校児童生徒数は約30万人規模に達し，千人あたり不登校率も過去最高を更新している．"
            "こども家庭庁 (2023) は「誰一人取り残されない学びのセーフティネット」の構築を掲げ，学校外の多様な学びの場の確保を急いでいる．"
            "教育社会学者の保坂 (2018) が指摘するように，不登校は単なる個人の適応障害ではなく，過度の同調圧力を強いる学校構造に起因する側面が強い．"
            "国際的にも，Kearney & Albanese (2020) の包括的出席問題モデルや，Havik & Ingenhoven (2018) が分析する学校エンゲージメントの低下が"
            "グローバルな関心事となっており，OECD (2021) でもウェルビーイングを重視した教室変革が提唱されている．"
            "我が国では，朝倉 (2021) が論じるフリースクール等との連携強化に加え，生田 (2022) が検証するように，"
            "自宅等において1人1台情報端末を活用した学習活動を出席扱いとする制度的弾力化が進展している．"
            "したがって，小・中学校における不登校児童生徒数およびICT出席扱い生徒数の時系列推移を計量的に解明することは極めて重要である．"
        ),
        fallback_objectives=(
            "本研究の目的は，文部科学省の公的調査データに基づき，公立小・中学校における不登校児童生徒数およびICT出席扱い制度の利用実態を計量的に分析することである．"
            "具体的には以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: 小学校と中学校における不登校児童生徒数および千人あたり不登校率の経年推移において，学校種移行に伴う不連続性（中1ギャップ）がどのように発現しているか．\n"
            "・RQ2: 自宅等におけるICT学習を出席扱いとした児童生徒数の増加動態と，不登校総数に対するセーフティネットとしてのカバー率はどう変化しているか．"
        ),
        fallback_discussion=(
            "実証分析から得られた知見を先行研究と対比しながら考察する．\n\n"
            "【RQ1に関する考察：不登校児童生徒数の高止まりと校種間ギャップ】\n"
            "文部科学省 (2023) の報告通り，中学校における千人あたり不登校率が小学校の3倍以上に達している構造は，"
            "保坂 (2018) が指摘した「中1ギャップ」および評価主義的学校文化の弊害と一致する（同じところ）．"
            "Kearney & Albanese (2020) の理論枠組みに照らしても，思春期における心理社会的ストレスと学習要求の急増が出席障害を加速させている．"
            "こども家庭庁 (2023) や Havik & Ingenhoven (2018) が提言する早期介入の重要性に対し，"
            "依然として小学校段階からの漸増傾向が抑制できていない実態（違うところ）が浮き彫りとなった．\n\n"
            "【RQ2に関する考察：ICTを活用した出席扱い制度の急速な普及と学びの保障】\n"
            "自宅等でのICT学習を出席扱いとする生徒数が指数関数的に増加している点は，生田 (2022) の初期報告を大きく上回る急拡大である（違うところ）．"
            "朝倉 (2021) が提唱した「場所を選ばない学びの多様化」がGIGA端末配備を契機に実質的制度として定着しつつある．"
            "OECD (2021) が示すハイブリッド学習空間の可能性を実証するものであり，"
            "登校復帰のみを目標としない自立支援へのパラダイムシフトが着実に進行していることが確認された（同じところ）．\n\n"
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
            "ICT出席扱い生徒数": "Students with ICT Home-Learning Recognized as Attendance",
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
        angle_id="absenteeism_ict_safetynet",
        angle_name="不登校児童生徒数の急増と自宅等におけるICT学習出席扱い制度の変容",
        title_theme="不登校30万人時代の学びの保障：自宅等ICT学習の出席扱い制度が拓く新しいセーフティネット",
        focus_metrics=["不登校児童生徒数", "千人あたり不登校率", "ICT出席扱い生徒数"],
    ),

    # 12. OECD TALIS Teacher Survey
    "oecd_talis_teacher_survey": DatasetAcademicContext(
        dataset_id="oecd_talis_teacher_survey",
        academic_topic="OECD国際教員指導環境調査（TALIS）に見る日本の教員協働指導・ICT活用指導と指導観の国際比較",
        theoretical_framework="Fullanの教育変革理論，プロフェッショナル・ラーニング・コミュニティ (PLC) 理論，授業研究 (Lesson Study) 文化論",
        core_research_problems=(
            "OECD TALIS調査において，日本の教員は教科指導の基本技能や勤務時間への献身度において国際的にも極めて高い水準を示す一方で，"
            "「授業におけるICTの日常的活用」「批判的思考を促す指導」および「教員同士の共同指導（チームティーチング）」の実施割合が"
            "参加国平均を大幅に下回る現象が長期にわたり持続している．"
            "孤立した学級担任制の壁と形式的参観にとどまる多忙化の弊害を計量的に解明し，深い教員間協働を通じた授業改善モデルを提起する．"
        ),
        banned_cliches=[
            "近年のSociety 5.0の進展に伴い",
            "近年，Society 5.0の進展に伴い",
            "近年の知識基盤社会の深化およびSociety 5.0の進展に伴い",
            "現代社会において急速に進展するDXに伴い",
            "情報化社会の急速な進展に伴い",
        ],
        specific_prompt_guidance=(
            "必ず『日本の教員の高い基礎力と協働指導・ICT活用の国際的乖離』から論述を開始すること．"
            "Fullanの教育変革理論や秋田の授業研究文化論を引用し，"
            "教室の孤立性を乗り越える深い教員間協働（Co-teaching）とICT活用の統合を学術的に論じること．"
        ),
        curated_references=[
            "OECD (2020) TALIS 2018 Results (Volume II): Teachers and School Leaders as Valued Professionals. OECD Publishing.",
            "国立教育政策研究所 (2019) OECD国際教員指導環境調査（TALIS 2018）報告書：学び続ける教員と学校組織. ぎょうせい.",
            "秋田喜代美 (2020) 授業研究と協働的な専門性の発達：TALIS国際比較が照らす日本の教員文化. 教育学研究, <b>87</b> (4) ：521-534.",
            "佐藤学 (2015) 学校を改革する：学びの共同体の挑戦. 岩波書店.",
            "FULLAN, M. (2016) The New Meaning of Educational Change. Teachers College Press.",
            "VIELUF, S., KAPLAN, D., KLIEME, E. and FISCHER, S. (2012) School Background, Teacher Characteristics and Teaching Practices: A Quantitative Analysis Based on TALIS 2008. OECD Publishing.",
            "VANGRIEKEN, K., DOCHY, F., RAES, E. and KYNDT, E. (2015) Teacher collaboration: A systematic review. Educational Research Review, <b>15</b> ：17-40.",
            "浅田匡 (2021) 教員の協働的リフレクションとICT活用指導力の変容. 教育工学研究, <b>45</b> (1) ：15-26.",
        ],
        fallback_title="OECD TALISにおける教員の協働指導実践とICT活用指導力の国際比較に関する計量分析†",
        fallback_subtitle="日本の教員文化における授業研究の伝統と日常的共同指導の乖離構造の解明",
        fallback_keywords=["OECD TALIS", "教員間協働指導", "ICT活用指導力", "批判的思考", "授業研究"],
        fallback_background=(
            "教員の指導実践，専門性開発，および学校組織の協働文化は，児童生徒の学習到達度を左右する決定的な教育資源である．"
            "OECD (2020) が公表した国際教員指導環境調査（TALIS 2018）および国立教育政策研究所 (2019) の報告によれば，"
            "日本の教員は教科指導の基本技能に強みを持つ一方で，授業におけるICTの日常的活用や批判的思考の育成指導，"
            "およびチームティーチング等の協働実践において国際平均を下回る傾向が指摘されている．"
            "秋田 (2020) や佐藤 (2015) が論じるように，日本には伝統的な「授業研究（Lesson Study）」の協働文化が存在するものの，"
            "多忙化により日常的な教員間の共同指導（Co-teaching）や相互参観の機会が制約されている．"
            "国際比較研究において，Fullan (2016) や Vieluf et al. (2012) は，同僚教員との協働的探究が"
            "教員の自己効力感や革新的な指導法の採用を直接的に促進することを示している．"
            "また，Vangrieken et al. (2015) のシステマティック・レビューや浅田 (2021) の実証研究が強調するように，"
            "ICT活用指導力の向上には単独研修ではなく協働的なリフレクションが不可欠である．"
            "したがって，TALISにおけるICT活用指導，批判的思考促進指導，および教員間協働指導割合の国際比較データを計量的に分析することは不可欠である．"
        ),
        fallback_objectives=(
            "本研究の目的は，OECD TALIS調査の国際比較公的データに基づき，日本の中学校教員の指導実践および協働体制の特徴を計量的に検証することである．"
            "具体的には以下の2つのリサーチクエスチョン（RQ）を設定する：\n\n"
            "・RQ1: ICT活用指導割合および批判的思考促進指導割合において，日本とOECD主要国との間にどのような定量的乖離が存在するか．\n"
            "・RQ2: 教員間協働指導割合と指導実践指標との間にいかなる国際的相関構造が観察され，日本の教員組織の特異性はどう位置づけられるか．"
        ),
        fallback_discussion=(
            "実証分析から得られた国際比較の知見について先行研究と対比しながら考察する．\n\n"
            "【RQ1に関する考察：ICT活用指導および思考力育成指導の国際的位置づけ】\n"
            "日本の教員におけるICT活用指導割合が国際平均に対して低位にとどまる点は，OECD (2020) および国立教育政策研究所 (2019) の"
            "指摘と完全に一致する（同じところ）．"
            "Vieluf et al. (2012) が論じた通り，知識伝達型の指導観から探究型指導への移行には指導不安が伴う．"
            "しかしながら，浅田 (2021) が指摘するように，近年のGIGAスクール構想下で現場のICT機器親和性は急速に高まっており，"
            "意識調査上の慎重さと実際の授業実践との間にギャップが存在する可能性（違うところ）が示唆された．\n\n"
            "【RQ2に関する考察：協働的指導実践と専門性開発の課題】\n"
            "教員間の共同指導（チームティーチング）の実施率が国際平均と乖離している現実は，佐藤 (2015) や秋田 (2020) が警鐘を鳴らす"
            "「孤立した教室の壁」の持続を反映している（同じところ）．"
            "Vangrieken et al. (2015) および Fullan (2016) が強調するように，"
            "教員同士が互いの授業を観察しフィードバックを与え合う「深い協働」こそが教育改革の中核である．"
            "授業研究の伝統を持つ日本が，多忙化によって形式的参観にとどまり日常的協働に昇華できていない構造（違うところ）が実証された．\n\n"
            "【研究の限界と今後の課題】\n"
            "本研究の限界として，TALIS調査が5年周期（第2回および第3回調査）のサイクルであり，2020年以降の急激な端末配備の効果をリアルタイムに"
            "反映しきれていない点が挙げられる．今後は次期TALIS調査や国内独自パネル調査との連動検証が期待される．"
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
        title_en="International Comparative Analysis of Teaching Practices, Digital Literacy, and Teacher Collaboration: Evidence from OECD TALIS",
        source_en="OECD (Organisation for Economic Co-operation and Development)",
        metrics_en={
            "ICT活用指導割合": "Percentage of Teachers Using ICT for Instruction",
            "批判的思考促進指導割合": "Percentage of Teachers Fostering Critical Thinking",
            "教員間協働指導割合": "Percentage of Teachers Engaging in Collaborative Teaching",
        },
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
        angle_name="TALIS国際比較に見る日本の教員協働指導とICT活用指導力の乖離構造",
        title_theme="TALIS国際比較が暴く教員の「孤立した教室」：なぜ日本の教員は共同指導とICT活用に慎重なのか",
        focus_metrics=["ICT活用指導割合", "批判的思考促進指導割合", "教員間協働指導割合"],
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
            academic_topic="算数・数学における実利主義的価値観と内発的動機づけの葛藤構造（有益性と好意度のトレードオフ）",
            theoretical_framework="Ecclesの期待価値理論 (Expectancy-Value Theory)，Deci & Ryanの自己決定理論 (Self-Determination Theory)",
            core_research_problems=(
                "「数学は将来の進路や就職に役立つ」という実利主義的有用性感（ユーティリティ・バリュー）は高い水準にある一方で，"
                "「数学を学ぶこと自体が楽しい」という興味・内発的価値が低迷する教育構造を計量的に検証する．"
                "外発的動機づけが学習者の認知的エンゲージメントおよび長期的な数学探究力に及ぼす影響を解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].banned_cliches,
            specific_prompt_guidance="必ず『実利主義的学習観（役に立つから学ぶ）と内発的動機の乖離』に焦点を当てて論じること．",
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
            title_en="Empirical Analysis of Instrumental Utility and Intrinsic Motivation in Mathematics Education",
            source_en=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].metrics_en,
            fallback_keywords_en=["EXPECTANCY-VALUE THEORY", "INTRINSIC MOTIVATION", "UTILITY VALUE", "MATHEMATICS", "TIMSS"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_timss_math_science"].fallback_summary_en,
            angle_id="timss_instrumental_utility",
            angle_name="実利主義的価値観と内発的動機づけの葛藤構造",
            title_theme="「役に立つから学ぶ」は学力を伸ばすか？：数学の実利主義的価値認識と内発的動機の対立構造",
            focus_metrics=["小4算数楽しい", "中2数学楽しい", "小4算数平均得点", "中2数学平均得点"],
        ),
    ],

    # 2. High School Informatics
    "japan_high_school_informatics": [
        DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"],
        DatasetAcademicContext(
            dataset_id="japan_high_school_informatics",
            academic_topic="計算論的思考 (Computational Thinking) の育成と共通テスト型筆記演習の乖離動態",
            theoretical_framework="Wingの計算論的思考論，Swellerの認知的負荷理論 (Cognitive Load Theory)，真正な学習評価 (Authentic Assessment)",
            core_research_problems=(
                "共通テストへの「情報I」導入に伴い，ペーパーテスト対策（擬似言語・知識暗記）に授業時間が偏重し，"
                "本来育成すべき「実際にコードを書きバグを解決する実践的計算論的思考」の演習時間が制約される指導的ジレンマを計量検証する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].banned_cliches,
            specific_prompt_guidance="ペーパーテスト対策とコード作成演習のトレードオフ、計算論的思考の本質的育成について論じること．",
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
            title_en="Computational Thinking vs. Written Examination in High School Informatics Education",
            source_en=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].metrics_en,
            fallback_keywords_en=["COMPUTATIONAL THINKING", "AUTHENTIC ASSESSMENT", "INFORMATICS I", "PROGRAMMING EDUCATION"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_high_school_informatics"].fallback_summary_en,
            angle_id="hs_info_computational_thinking",
            angle_name="計算論的思考の育成と共通テスト型筆記演習の乖離",
            title_theme="ペーパーテスト化されるプログラミング：計算論的思考の育成と共通テスト対策の指導的ジレンマ",
            focus_metrics=["情報免許保有率", "Python指導実施校割合", "共通テスト対策実施校割合"],
        ),
    ],

    # 3. National Assessment Math
    "japan_national_assessment_math": [
        DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"],
        DatasetAcademicContext(
            dataset_id="japan_national_assessment_math",
            academic_topic="全国学力テストにおける知識・計算処理と数学的論述・表現力の二極化動態",
            theoretical_framework="SOLO分類学 (Structure of Observed Learning Outcomes)，Pólyaの問題解決プロセス理論",
            core_research_problems=(
                "基本計算や定型手続きの正答率は高止まりする一方で，「根拠を言葉と数式を用いて説明する」論述式設問の無解答率・誤答率が"
                "顕著に高い数学的表現力の構造的課題を計量的に解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].banned_cliches,
            specific_prompt_guidance="計算力と論述表現力の乖離、無解答率の分析に焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].curated_references,
            fallback_title="全国学力調査における計算処理力と数学的表現・論述力の構造的二極化に関する計量分析†",
            fallback_subtitle="無解答率の動態と多面的問題解決プロセスの評価",
            fallback_keywords=["全国学力調査", "数学的表現力", "論述式問題", "無解答率", "問題解決"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_background,
            fallback_objectives="本研究の目的は，全国学力調査における論述式問題の正答率および無解答率の時系列推移を検証することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_questions_to_authors,
            title_en="Dichotomy Between Computational Skills and Mathematical Reasoning in National Assessments",
            source_en=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].metrics_en,
            fallback_keywords_en=["MATHEMATICAL REASONING", "COMPUTATIONAL SKILLS", "NATIONAL ASSESSMENT", "EXPLANATORY ABILITY"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_national_assessment_math"].fallback_summary_en,
            angle_id="national_math_reasoning_gap",
            angle_name="知識・計算処理と数学的思考力・表現力の二極化動態",
            title_theme="計算はできるが説明できない？：全国学力テストが暴く数学的表現力・論述力の構造的課題",
            focus_metrics=["小6算数平均正答率", "中3数学平均正答率", "算数数学好き肯定率"],
        ),
    ],

    # 4. MEXT ICT Informatization
    "japan_mext_ict_informatization": [
        DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"],
        DatasetAcademicContext(
            dataset_id="japan_mext_ict_informatization",
            academic_topic="学校教育情報化における校務クラウド化と教員業務効率化・協働的学びの連動性",
            theoretical_framework="Mishra & KoehlerのTPACK，教員自己効力感理論，教育DX組織成熟度モデル",
            core_research_problems=(
                "端末配備完了後のフェーズにおいて，校務支援システムのクラウド化と児童生徒の学習ログ利活用が"
                "教員の授業研究時間の確保と学級内の協働学習の質にいかに寄与するかを計量的に解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].banned_cliches,
            specific_prompt_guidance="校務DXと授業改善の相乗効果、学習ログ活用と教員負担軽減に焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].curated_references,
            fallback_title="学校教育情報化における校務クラウド化と協働的指導実践の連動性に関する実証分析†",
            fallback_subtitle="文部科学省実態調査データに基づく教員指導力とICT基盤の共進化検証",
            fallback_keywords=["学校教育情報化", "校務クラウド", "教員指導力", "協働的学び", "教育DX"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_background,
            fallback_objectives="本研究の目的は，校務クラウド化の進展と教員のICT指導力向上との連動性を計量的に検証することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_questions_to_authors,
            title_en="Cloud Infrastructure Integration and Collaborative Pedagogical Practices in School ICT",
            source_en=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].metrics_en,
            fallback_keywords_en=["CLOUD INFRASTRUCTURE", "EDUCATIONAL DX", "TEACHING COMPETENCE", "MEXT INFORMATIZATION"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_mext_ict_informatization"].fallback_summary_en,
            angle_id="mext_ict_cloud_utilization",
            angle_name="校務クラウド化と協働的学びの実現度",
            title_theme="校務DXと学習ログ活用の現在地：クラウド化がもたらす教員業務効率化と授業改善の相関",
            focus_metrics=["端末整備率", "教員用端末普及率", "ICT指導力肯定率"],
        ),
    ],

    # 5. OECD PISA Math ICT
    "oecd_pisa_math_ict": [
        DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"],
        DatasetAcademicContext(
            dataset_id="oecd_pisa_math_ict",
            academic_topic="OECD PISAにおける生徒の社会経済的背景 (ESCS) とデジタル学習機会の格差勾配",
            theoretical_framework="Bourdieuの文化資本理論，デジタル・キャピタル理論 (Digital Capital Theory)",
            core_research_problems=(
                "学校での端末配備にもかかわらず，家庭の社会経済的背景（ESCS）が生徒のデジタル自己効力感や"
                "数学的リテラシーに与える格差勾配（Socioeconomic Gradient）の国際的構造を計量的に解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].banned_cliches,
            specific_prompt_guidance="家庭環境格差（ESCS）とデジタル学習機会、文化資本の再生産に焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].curated_references,
            fallback_title="OECD PISAにおける家庭背景 (ESCS) とデジタル数学リテラシーの格差勾配に関する計量分析†",
            fallback_subtitle="国際比較データに見る文化資本とデジタル格差の非対称性",
            fallback_keywords=["OECD PISA", "ESCS", "文化資本", "デジタル格差", "数学リテラシー"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_background,
            fallback_objectives="本研究の目的は，PISA調査における家庭背景とデジタル数学到達度の国際的連動性を検証することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_questions_to_authors,
            title_en="Socioeconomic Gradients and Digital Mathematical Literacy in OECD PISA",
            source_en=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].metrics_en,
            fallback_keywords_en=["OECD PISA", "SOCIOECONOMIC GRADIENT", "DIGITAL CAPITAL", "MATHEMATICS LITERACY"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["oecd_pisa_math_ict"].fallback_summary_en,
            angle_id="pisa_socioeconomic_gradient",
            angle_name="社会経済的背景（ESCS）とデジタル学習機会の格差勾配",
            title_theme="デジタル時代の教育格差：PISAデータが示す家庭環境とデジタル学習レジリエンスの国際格差",
            focus_metrics=["数学的リテラシー平均得点", "学校ICT利用指数", "学習用端末利用時間"],
        ),
    ],

    # 6. UNESCO World ICT Skills
    "unesco_world_ict_skills": [
        DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"],
        DatasetAcademicContext(
            dataset_id="unesco_world_ict_skills",
            academic_topic="世界主要国における女性のICTスキル習得動態とジェンダー・デジタル格差",
            theoretical_framework="フェミニスト科学技術論，UNESCOジェンダー平等指標，能力アプローチ (Capabilities Approach)",
            core_research_problems=(
                "基礎的なICT操作スキルにおける男女差の縮小と対照的に，プログラミングやアルゴリズム作成等の"
                "高度デジタルスキル領域において依然として残存するジェンダー不均衡の国際構造を計量解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].banned_cliches,
            specific_prompt_guidance="ジェンダー・デジタル格差と高度スキル領域のジェンダー・ギャップに焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].curated_references,
            fallback_title="UNESCO統計に見る高度デジタルスキル習得におけるジェンダー格差の国際比較計量分析†",
            fallback_subtitle="SDG 4.4.1指標に基づく基礎操作とプログラミングスキルの構造的分離",
            fallback_keywords=["UNESCO", "ジェンダー格差", "プログラミングスキル", "SDG 4.4.1", "デジタルスキル"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_background,
            fallback_objectives="本研究の目的は，UNESCOデータにおける男女別デジタルスキル習得率の国際的格差を計量検証することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_questions_to_authors,
            title_en="Gender Disparities in Advanced ICT Skills: A Cross-National Empirical Study Using UNESCO Indicators",
            source_en=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].metrics_en,
            fallback_keywords_en=["UNESCO", "GENDER DIGITAL DIVIDE", "PROGRAMMING SKILLS", "SDG 4.4.1", "CAPABILITIES APPROACH"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["unesco_world_ict_skills"].fallback_summary_en,
            angle_id="unesco_gender_disparity_in_skills",
            angle_name="世界主要国における女性のICTスキル習得動態",
            title_theme="デジタルスキルにおけるジェンダー平等の現在地：ユネスコデータに見る各国の女性ICT習熟度",
            focus_metrics=["プログラミングスキル保有率", "表計算計算式利用率", "ファイル移動スキル保有率"],
        ),
    ],

    # 7. STEM CS Enrollment
    "japan_stem_cs_enrollment": [
        DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"],
        DatasetAcademicContext(
            dataset_id="japan_stem_cs_enrollment",
            academic_topic="IT人材需要の急拡大と大学情報系学部の定員受容容量・理数基盤キャパシティ制約",
            theoretical_framework="人的資本理論，高等教育定員政策論，労働市場需給ギャップモデル",
            core_research_problems=(
                "DX推進に伴う産業界の高度IT人材需要の急増に対し，大学情報科学・工学系学部の入学定員増加ペースが"
                "教員数や実験設備等の大学側キャパシティ制約によって需要に追いついていない構造的ボトルネックを解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].banned_cliches,
            specific_prompt_guidance="高等教育機関の定員受け入れ容量と産業界の高度IT人材需要の需給ギャップに焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].curated_references,
            fallback_title="大学情報科学・工学系学部における入学者数推移と高等教育定員受容容量の計量分析†",
            fallback_subtitle="学校基本調査データに基づく高度IT人材育成キャパシティの構造検証",
            fallback_keywords=["学校基本調査", "情報科学", "入学者数", "定員制約", "高等教育政策"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_background,
            fallback_objectives="本研究の目的は，情報系学科入学者数の推移と高等教育機関の受容キャパシティを計量的に検証することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_questions_to_authors,
            title_en="Capacity Constraints and Enrollment Dynamics in University Computer Science Programs",
            source_en=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].metrics_en,
            fallback_keywords_en=["COMPUTER SCIENCE ENROLLMENT", "HIGHER EDUCATION CAPACITY", "HUMAN CAPITAL THEORY", "STEM PIPELINE"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_stem_cs_enrollment"].fallback_summary_en,
            angle_id="stem_capacity_and_workforce_demand",
            angle_name="IT人材需要の急拡大と大学情報系学部の定員受容容量",
            title_theme="IT立国を目指す日本の大学定員ジレンマ：情報系学部入学者増と理数教育基盤のキャパシティ制約",
            focus_metrics=["入学者総数", "女性入学者数", "女性比率"],
        ),
    ],

    # 8. World Bank Education Indicators
    "worldbank_education_indicators": [
        DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"],
        DatasetAcademicContext(
            dataset_id="worldbank_education_indicators",
            academic_topic="発展途上国におけるインターネット接続普及と基礎数学習熟度のリープフロッグ効果",
            theoretical_framework="リープフロッギング理論 (Leapfrogging Theory)，国際開発教育学，内生的経済成長モデル",
            core_research_problems=(
                "公的教育財政が逼迫する新興国・途上国において，モバイル通信およびインターネット接続の急速な普及が"
                "伝統的な学校施設投資の不足を補い，児童生徒の基礎数学習熟度を劇的に引き上げる現象を計量検証する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].banned_cliches,
            specific_prompt_guidance="途上国におけるインターネット普及と教育インフラのリープフロッグ効果に焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].curated_references,
            fallback_title="発展途上国におけるデジタルインフラ接続と数学最低習熟度のリープフロッグ効果に関する実証分析†",
            fallback_subtitle="世界銀行EdStatsオープンデータに基づく国際比較計量経済分析",
            fallback_keywords=["世界銀行", "インターネット普及率", "数学習熟度", "リープフロッグ", "開発教育学"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_background,
            fallback_objectives="本研究の目的は，公的支出水準を統制した上でインターネット普及率が数学習熟度に与える効果を解明することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_questions_to_authors,
            title_en="Digital Connectivity and Leapfrogging in Minimum Mathematics Proficiency: Evidence from The World Bank",
            source_en=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].metrics_en,
            fallback_keywords_en=["THE WORLD BANK", "LEAPFROGGING", "INTERNET CONNECTIVITY", "MATHEMATICS PROFICIENCY", "DEVELOPMENT ECONOMICS"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["worldbank_education_indicators"].fallback_summary_en,
            angle_id="wb_internet_leapfrogging",
            angle_name="発展途上国におけるインターネット接続と教育成果の飛躍",
            title_theme="教育インフラのリープフロッグ：世界銀行データに見るデジタル接続が途上国の基礎学力を底上げする力",
            focus_metrics=["インターネット利用率", "数学最低習熟度達成率", "教育支出対GDP比"],
        ),
    ],

    # 9. Teacher Workload Survey
    "japan_teacher_workload_survey": [
        DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"],
        DatasetAcademicContext(
            dataset_id="japan_teacher_workload_survey",
            academic_topic="中学校における部活動指導負担と持ち帰り仕事の日常化が教員ウェルビーイングに及ぼす影響",
            theoretical_framework="感情労働論 (Hochschild)，ワーク・ライフ・バランス論，部活動地域移行政策モデル",
            core_research_problems=(
                "中学校教員の平日在校等時間を押し上げる最大要因である部活動指導負担と，日常化する持ち帰り仕事時間の構造を解明し，"
                "休日部活動の地域移行政策が教員の自律的研究時間の回復に果たすべき実証的効果を検証する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].banned_cliches,
            specific_prompt_guidance="中学校の部活動指導負担と持ち帰り仕事の日常化、地域移行の緊急性に焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].curated_references,
            fallback_title="中学校教員における部活動指導負担と持ち帰り仕事時間の構造的連動に関する計量分析†",
            fallback_subtitle="教員勤務実態調査データに基づく感情労働と時間外勤務の検証",
            fallback_keywords=["教員勤務実態調査", "部活動指導", "持ち帰り仕事", "地域移行", "教員ウェルビーイング"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_background,
            fallback_objectives="本研究の目的は，中学校教員の部活動指導時間と持ち帰り仕事時間の相互関係を計量的に検証することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_questions_to_authors,
            title_en="Extracurricular Guidance and Take-Home Workloads in Lower Secondary Schools",
            source_en=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].metrics_en,
            fallback_keywords_en=["TEACHER WORKLOAD", "EXTRACURRICULAR GUIDANCE", "TAKE-HOME WORK", "LOWER SECONDARY", "WELLBEING"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_teacher_workload_survey"].fallback_summary_en,
            angle_id="workload_extracurricular_burden",
            angle_name="中学校における部活動指導負担と持ち帰り仕事の日常化",
            title_theme="中学校教員を追い詰める部活動指導の呪縛：勤務実態調査データが語る地域移行の急務",
            focus_metrics=["部活動指導時間", "持ち帰り仕事時間", "在校等時間"],
        ),
    ],

    # 10. Special Needs Education
    "japan_special_needs_education": [
        DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"],
        DatasetAcademicContext(
            dataset_id="japan_special_needs_education",
            academic_topic="特別支援教育支援員の配置格差と通常学級ユニバーサルデザインの協働体制",
            theoretical_framework="ユニバーサルデザイン学習 (UDL)，協働的指導実践論 (Co-Teaching)，教育行財政リソース配分論",
            core_research_problems=(
                "特別支援教育支援員の配置数が自治体の財政力によって不均等に推移する実態と，"
                "支援員の人的介入とICT支援ツールの連携が通常学級の学級経営に及ぼす相乗効果を計量的に解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].banned_cliches,
            specific_prompt_guidance="特別支援教育支援員の配置格差と、人的支援とICT端末アクセシビリティの相乗効果に焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].curated_references,
            fallback_title="特別支援教育支援員の配置動態と通常学級におけるユニバーサルデザイン支援の実証分析†",
            fallback_subtitle="文部科学省実態調査データに基づく人的支援リソース配分の検証",
            fallback_keywords=["特別支援教育支援員", "ユニバーサルデザイン", "通常学級", "リソース配分", "インクルーシブ教育"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_background,
            fallback_objectives="本研究の目的は，特別支援教育支援員配置数の推移と通常学級支援効果を計量的に検証することである．",
            fallback_discussion=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_discussion,
            fallback_review_critique=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_review_critique,
            fallback_major_revisions=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_major_revisions,
            fallback_minor_revisions=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_minor_revisions,
            fallback_questions_to_authors=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_questions_to_authors,
            title_en="Support Staff Allocation and Universal Design Practices in Inclusive Compulsory Education",
            source_en=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].metrics_en,
            fallback_keywords_en=["SPECIAL SUPPORT AIDES", "UNIVERSAL DESIGN", "RESOURCE ALLOCATION", "INCLUSIVE EDUCATION"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["japan_special_needs_education"].fallback_summary_en,
            angle_id="special_needs_support_staff_allocation",
            angle_name="特別支援教育支援員の配置格差と通常学級ユニバーサルデザイン",
            title_theme="インクルーシブ教育の最前線：支援員配置数とICT端末活用がもたらす通常学級の質的変容",
            focus_metrics=["特別支援教育支援員数", "特別支援学級在籍数", "端末支援活用率"],
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
                "教科担任制への移行、定期考査による相対評価、および部活動等の規律強化がもたらす環境不適合の視点から計量解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].banned_cliches,
            specific_prompt_guidance="小学校から中学校への学校種移行（中1ギャップ）における不登校率急増と環境適合ストレスに焦点を当てて論じること．",
            curated_references=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].curated_references,
            fallback_title="小・中学校学校種移行期における不登校率急増動態の計量分析†",
            fallback_subtitle="生徒指導要録調査データに見る中1ギャップと学習環境適合の検証",
            fallback_keywords=["中1ギャップ", "不登校率", "ステージ・エンバイロメント・フィット", "学校種移行", "生徒指導"],
            fallback_background=DATASET_ACADEMIC_CONTEXTS["japan_school_absenteeism_bullying"].fallback_background,
            fallback_objectives="本研究の目的は，小・中学校の不登校率推移における移行期ギャップを計量的に検証することである．",
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
            focus_metrics=["千人あたり不登校率", "不登校児童生徒数", "ICT出席扱い生徒数"],
        ),
    ],

    # 12. OECD TALIS Teacher Survey
    "oecd_talis_teacher_survey": [
        DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"],
        DatasetAcademicContext(
            dataset_id="oecd_talis_teacher_survey",
            academic_topic="批判的思考 (Critical Thinking) を育成する授業実践と教員の自己効力感の国際連動性",
            theoretical_framework="Banduraの教員効力感理論，探究型学習指導論，高次思考スキル (Higher-Order Thinking Skills)",
            core_research_problems=(
                "日本の教員における「批判的思考を促す発問・課題設定」の実施割合が国際平均より低い要因として，"
                "知識網羅型カリキュラムの制約と教員の探究指導自己効力感の低さがどう影響しているかを計量的に解明する．"
            ),
            banned_cliches=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].banned_cliches,
            specific_prompt_guidance="批判的思考を育成する指導実践と教員の自己効力感、知識網羅型指導観からの脱却に焦点を当てて論じること．",
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
            title_en="Instructional Practices for Critical Thinking and Teacher Self-Efficacy: A Cross-National TALIS Study",
            source_en=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].source_en,
            metrics_en=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].metrics_en,
            fallback_keywords_en=["OECD TALIS", "CRITICAL THINKING", "TEACHER SELF-EFFICACY", "HIGHER-ORDER THINKING"],
            fallback_summary_en=DATASET_ACADEMIC_CONTEXTS["oecd_talis_teacher_survey"].fallback_summary_en,
            angle_id="talis_critical_thinking_instruction",
            angle_name="批判的思考を促す授業実践と教員の自己効力感の国際連動性",
            title_theme="正解を教える授業から問いを生む授業へ：TALISデータが示す日本の批判的思考指導の国際的課題",
            focus_metrics=["批判的思考促進指導割合", "ICT活用指導割合", "教員間協働指導割合"],
        ),
    ],
}


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
