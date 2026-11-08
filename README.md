# 阪口源太（福井県高浜町）公式LINE連携 Webアプリケーション・AI Bot基盤 (`takahama-line-agent`)

2027年春の高浜町議会議員選挙に向けた政治活動・政策広報ツールとして、町民との24時間双方向対話を実現するLINE連携Webアプリケーション基盤です。  
Google Gemini API（`gemini-2.5-flash` 推奨）を活用した「AI阪口源太Bot」、LIFF連携Webビュー、現場通報フォーム、後援会サポーター登録システムを統合しています。

---

## 主な機能

1. **AI阪口源太Bot（LINE Messaging API / Webhook）**
   - 候補者本人（阪口源太：青郷小・高浜中卒、阪口商店ルーツ、東大松尾研修了、元与那国町議会議員）のペルソナ・口調を忠実に再現。
   - **「ハイブリッド型政治（80%の安心・継続 × 20%の独自性）」**：
     - 子育て給食無償化・地域医療の堅持、100億円基金の死守と厳格な監査。
     - 青郷の国道27号青葉改良（青葉トンネル）・南山手線延伸の推進。
     - AIによる優しい行政AX・迷わないLINE窓口設計、AIオンデマンド乗合交通（舞鶴連携）。
   - **厳格な安全弁（ガードレール）**：
     - 公職選挙法違反（事前運動・投票依頼）の完全抑止。
     - 現町政・他議員への誹謗中傷を排し、常に建設的代替案を提示。
     - 未登録の個別苦情や事実確認を要する相談は本人フォロー（現地確認フロー）へトスアップ。

2. **リッチメニュー 6分割タイル対応 Webビュー（LIFF）**
   - **[左上] 重点政策10選 (`/policies`)**: 討議資料v3に基づく政策ダイジェスト表示。
   - **[中上] AI源太に相談 (`LINEトーク画面`)**: クイックリプライボタン付きAI対話。
   - **[右上] 高浜町情報チャンネル (`YouTube`)**: 全5本の制作動画を案内。
   - **[左下] 地域の困りごと投稿フォーム (`/issues`)**: 写真・区名・詳細を投稿できる住民参加型フォーム。
   - **[中下] プロフィール・活動理念 (`/profile`)**: 阪口商店、東大松尾研、元地方議会議員の実績紹介。
   - **[右下] 後援会サポーター登録 (`/supporters`)**: ボランティア、討議資料受取、オンライン応援登録。

---

## ディレクトリ構成

```
antigravity/
├── app/
│   ├── main.py                     # FastAPIエントリーポイント
│   ├── config.py                   # 環境変数設定 (pydantic-settings)
│   ├── bot/
│   │   ├── gemini_service.py       # Gemini API連携サービス
│   │   ├── prompt_template.py      # システムプロンプト・ペルソナ・安全弁定義
│   │   ├── richmenu.json           # LINE 6分割リッチメニュー定義
│   │   └── setup_richmenu.py       # リッチメニュー自動登録スクリプト
│   ├── knowledge/
│   │   └── takahama_knowledge.md   # 高浜町政策・議会・地域ナレッジ
│   └── routes/
│       ├── webhook.py              # LINE Messaging API Webhook
│       ├── api.py                  # 対話・困りごと・サポーター受信用API
│       └── pages.py                # LIFF / Webビュー画面ルーティング
├── templates/                      # Jinja2 / Tailwind CSSテンプレート
│   ├── base.html
│   ├── index.html                  # ポータル / Web対話ウィジェット
│   ├── policies.html               # 重点政策10選（討議資料v3）
│   ├── issues.html                 # 地域の困りごと現場投稿フォーム
│   ├── profile.html                # プロフィール・経歴・理念
│   └── supporters.html             # 後援会サポーター・ボランティア登録
├── static/
│   ├── css/style.css
│   └── uploads/                    # 投稿された写真の保存先
├── tests/
│   └── test_app.py                 # 統合テストスイート
├── .env.example                    # 環境変数テンプレート
├── requirements.txt                # 依存ライブラリ
└── README.md
```

---

## 環境構築・ローカル実行手順

### 1. 依存ライブラリのインストール
```bash
python -m pip install -r requirements.txt
```

### 2. 環境変数の設定
`.env.example` をコピーして `.env` を作成し、必要なキーを設定してください。

```bash
cp .env.example .env
```

```ini
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
BASE_URL=http://localhost:8000
LIFF_ID=your_line_liff_id
```

### 3. アプリケーションサーバーの起動
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
ブラウザで `http://localhost:8000` にアクセスすると、Webポータル画面が表示されます。

### 4. テストの実行
```bash
python -m pytest tests
```

---

## LINE Developers連携手順

### 1. Webhook URLの設定
1. `ngrok` やデプロイ先サーバーのURLを取得します（例: `https://xxxx.ngrok-free.app`）。
2. LINE Developersコンソール > チャネル設定 > **Messaging API** を開きます。
3. **Webhook URL** に `https://<ドメイン>/line/webhook` を登録し、「Webhookの利用」をONにします。
4. 「検証」ボタンをクリックし、接続成功を確認します。

### 2. リッチメニューの登録
リッチメニュー画像（2500x1686推奨）を用意し、以下のスクリプトを実行することで自動作成・デフォルト登録されます。

```bash
python -m app.bot.setup_richmenu path/to/richmenu_image.png
```

### 3. LIFF（LINE Front-end Framework）の設定
LINE Developersコンソール > **LIFF** タブから新しいLIFFアプリを作成します。
- エンドポイントURL: `https://<ドメイン>/`
- Scope: `profile`, `openid`
- 取得したLIFF IDを `.env` の `LIFF_ID` に設定します。

---

## ライセンス / 運用規定
本リポジトリの政策・対話コンテンツは福井県高浜町における阪口源太の政治活動・広報目的に特化して設計されています。
公職選挙法および政治資金規正法を遵守して運用してください。

