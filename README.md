# 算数・数学教育＆情報教育 オープンデータ統計分析＆ブログ自動投稿システム (EduDataToBlogActions)

日本および海外の公的オープンデータから「算数・数学教育」や「情報教育・プログラミング教育」に関する統計データを自動取得し、統計分析（記述統計・経年変化・相関・国際比較）を行い、**データ表・グラフ付きの教育インサイトレポート**を作成して指定したブログ（WordPress等）へ自動投稿する**GitHub Actions完全自動化パイプライン**です。

---

## 🌟 システムの特徴

1. **国内外の教育公的オープンデータを網羅**:
   - **国内データ**: 文部科学省・国立教育政策研究所・e-Stat
     - 全国学力・学習状況調査（小学校算数・中学校数学の平均正答率、学習意識・端末利用とのクロス集計）
     - 学校における教育情報化の実態等に関する調査（1人1台端末利活用率、教員のICT指導力達成率、プログラミング教育実施状況）
     - 学校基本調査（大学・高専における情報科学・理数系学科入学者数、女性比率の推移）
   - **海外データ**: OECD PISA、UNESCO UIS、世界銀行（World Bank Open Data）
     - OECD PISA（主要国の数学的リテラシー得点、男女得点差、デジタル活用度）
     - UNESCO / ITU（SDG 4.4.1 若年層のプログラミングスキル・デジタル技能保有率国際比較）
     - 世界銀行 EdStats（数学習熟度と教育支出対GDP比の相関データ）
2. **本格的な統計分析エンジン (`src/analyzer.py`)**:
   - 記述統計量（平均値、中央値、標準偏差、最小・最大値、四分位範囲 IQR、歪度）
   - 経年トレンド・成長率分析（前年比変化量、変化率、年平均成長率 CAGR、線形回帰トレンド係数・決定係数 $R^2$）
   - 相関分析（ピアソン相関係数 $r$、p値、相関強度の自動解釈）
   - グループ比較・格差分析（ランキング、最高値と最低値の格差算出）
3. **高解像度グラフ自動生成 (`src/visualizer.py`)**:
   - Matplotlib + Seaborn による出版品質のグラフ画像（180〜200 DPI）
   - 経年推移折れ線グラフ、国別・学校種別横棒ランキンググラフ、回帰直線付き相関散布図
   - Linux環境（GitHub Actions）でも文字化けしない日本語フォント自動適用機構
4. **Google Gemini AI による教育的示唆・授業実践解説 (`src/insights.py`)**:
   - 統計数値を踏まえ、学校現場の教員・教育関係者に向けた「授業実践への具体的示唆」「今後の課題と教育政策・国際的展望」を自動執筆。
   - ※Gemini APIキー未設定時でも、精緻な統計値に基づく内蔵テンプレートエンジンで高品質レポートを生成（ゼロトークン稼働対応）。
5. **柔軟なマルチパブリッシャー構成 (`src/publishers/`)**:
   - **WordPress (メール投稿: Post by Email)**: 最も手軽かつ安全。グラフ画像を自動添付・アイキャッチ化。
   - **WordPress REST API**: アプリケーションパスワードを用いた公式REST API直接投稿。
   - **Markdownファイル保存**: リポジトリ内の `reports/` に永続アーカイブ（GitHub Pages等で閲覧可能）。
6. **日次ローテーション＆二重投稿防止 (`src/storage.py`)**:
   - 過去の投稿履歴（`data/posted_reports.json`）を記録し、毎日重複のない新しいテーマを自動選定。
   - リポジトリ閲覧用の配信目次（`data/REPORT_ARCHIVE.md`）を自動更新。

---

## 📂 フォルダ構成

```
EduDataToBlogActions/
├── .github/
│   └── workflows/
│       └── daily_report.yml          # GitHub Actions 定期実行ワークフロー（cron 毎朝6時JST）
├── src/
│   ├── __init__.py
│   ├── config.py                     # 環境変数・パス・定数設定
│   ├── analyzer.py                   # 統計分析エンジン（記述統計・CAGR・相関・R²）
│   ├── visualizer.py                 # グラフ可視化エンジン（日本語フォント対応）
│   ├── insights.py                   # Gemini AI 教育インサイト・授業実践提言生成
│   ├── reporter.py                   # レポート（HTML/Markdown）組立エンジン
│   ├── storage.py                    # 投稿履歴JSON & REPORT_ARCHIVE.md管理
│   ├── main.py                       # CLIエントリーポイント
│   ├── fetchers/                     # オープンデータ取得モジュール群
│   │   ├── __init__.py
│   │   ├── base.py                   # データセットモデル (EducationDataset)
│   │   ├── catalog.py                # データカタログ＆日次ローテーション選定器
│   │   ├── japan_edu_data.py         # 国内統計（全国学力調査・情報化実態・学校基本調査）
│   │   ├── oecd_unesco_data.py       # 国際比較（OECD PISA・UNESCOプログラミング）
│   │   └── world_bank_data.py        # 世界銀行 EdStats API 連携
│   └── publishers/                   # ブログ投稿モジュール群
│       ├── __init__.py
│       ├── base.py                   # パブリッシャー基底クラス
│       ├── wordpress_mail.py         # WordPress メール投稿 (SMTP + 画像添付)
│       ├── wordpress_rest.py         # WordPress REST API 投稿
│       └── markdown_file.py          # reports/ ディレクトリ保存
├── data/
│   ├── catalog/                      # オープンデータマスターデータセット (JSON)
│   ├── posted_reports.json           # 配信履歴機械用JSON
│   └── REPORT_ARCHIVE.md             # 配信履歴閲覧用Markdown表
├── reports/                          # 生成されたMarkdownレポート＆グラフ画像アーカイブ
├── tests/                            # ユニットテスト群
├── requirements.txt                  # Python依存ライブラリ
├── .env.example                      # ローカル設定用テンプレート
├── .gitignore
└── README.md                         # 本説明書
```

---

## 🚀 セットアップ手順（5ステップ）

### ステップ1: WordPress「メールで投稿」を有効化（推奨）
1. WordPress管理画面（WordPress.com、またはJetpack連携済みWordPress）を開きます。
2. **「設定」** ＞ **「投稿」** を開きます。
3. **「メールで投稿 (Post by Email)」** を有効化します。
4. 発行された投稿用メールアドレス（例: `secret12345@post.wordpress.com`）を控えます。

### ステップ2: Google Gemini APIキーの取得（任意・推奨）
1. [Google AI Studio](https://aistudio.google.com/) にアクセスします。
2. **「Get API key」** からAPIキーを発行して控えます。
*(※APIキーを設定しない場合でも、統計数値を組み込んだ高機能テンプレートエンジンでレポートが生成されます)*

### ステップ3: 送信用SMTPアカウントの準備（Gmail推奨）
1. 送信に使用するGoogleアカウントの [セキュリティ設定](https://myaccount.google.com/security) を開きます。
2. **「2段階認証」** を有効化します。
3. **「アプリ パスワード」** を生成し、16桁のパスワードを控えます（`SMTP_PASS` に使用）。

### ステップ4: GitHubリポジトリの設定（Permissions & Secrets）

#### 4-1. リポジトリの書き込み権限を許可
GitHub Actionsが生成したレポートや配信履歴（`reports/` や `data/`）を自動コミットするために必要です：
1. GitHubリポジトリの **「Settings」** ＞ **「Actions」** ＞ **「General」** を開きます。
2. **「Workflow permissions」** で **「Read and write permissions」** を選択し、**Save** をクリックします。

#### 4-2. GitHub Secrets の登録
リポジトリの **「Settings」** ＞ **「Secrets and variables」** ＞ **「Actions」** に移動し、以下のシークレットを登録します：

| Secret名 | 必須 | 設定内容 |
| :--- | :---: | :--- |
| `GEMINI_API_KEY` | 任意 (推奨) | Google AI Studio で取得したGemini APIキー |
| `WP_POST_EMAIL` | メール投稿時必須 | ステップ1で取得したWordPress投稿用メールアドレス |
| `SMTP_USER` | メール投稿時必須 | 送信元Gmailアドレス（例: `your-account@gmail.com`） |
| `SMTP_PASS` | メール投稿時必須 | ステップ3で生成した16桁のGoogleアプリパスワード |
| `SMTP_HOST` | 任意 | SMTPサーバー（デフォルト: `smtp.gmail.com`） |
| `SMTP_PORT` | 任意 | SMTPポート（デフォルト: `587`） |
| `WP_SITE_URL` | REST利用時 | WordPressサイトURL（例: `https://example.com`） |
| `WP_USER` | REST利用時 | WordPressログインユーザー名 |
| `WP_APP_PASSWORD` | REST利用時 | WordPressのアプリケーションパスワード |

---

## 💻 ローカルでの実行方法

```powershell
# 1. 依存ライブラリのインストール
pip install -r requirements.txt

# 2. 設定ファイルの準備
cp .env.example .env
# .env を開いて必要な項目を記入

# 3. ドライラン（メール送信せずレポート・グラフのみ生成確認）
python -m src.main --dry-run

# 4. 算数・数学教育に絞って実行
python -m src.main --dry-run --topic math

# 5. 情報・プログラミング教育に絞って実行
python -m src.main --dry-run --topic info

# 6. 特定のデータセットを指定して本番投稿
python -m src.main --dataset japan_national_assessment_math
```

---

## 🧪 テストの実行

```powershell
python -m pytest tests/ -v
```

---

## 📝 ライセンス
本プロジェクトは MIT ライセンスの下で公開されています。
オープンデータの利用にあたっては各提供機関（文部科学省、OECD、UNESCO、世界銀行）の利用規約に準拠してください。
