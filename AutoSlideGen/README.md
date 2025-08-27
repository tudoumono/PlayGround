# AutoSlideGen 🚀

AIの力で **テキストからプロフェッショナルなPowerPoint** を自動生成するサーバーレスシステム

---

## 📋 概要

AutoSlideGenは、非構造化テキスト（議事録・記事・メモなど）を解析し、論理的に整理されたPowerPointを自動生成します。  
**AWS Lambda + API Gateway による完全サーバーレス構成**と**ローカル開発環境**の両方に対応しています。

### ✨ 主な特徴

- 🎨 **多様なスライドタイプ**: 箇条書き、表、グラフ、タイムライン、進捗バー、比較表など  
- 🎯 **Google風デザイン**: モダン＆プロフェッショナルなデザインテンプレート  
- ⚡ **サーバーレス**: AWS Lambda + API Gatewayによるスケーラブル構成  
- 💻 **ローカル開発対応**: Lambda環境とローカル環境の両方で動作  
- 📝 **スピーカーノート自動生成**: 各スライドに適切な発表原稿を付与  
- 🔧 **柔軟なカスタマイズ**: 環境変数でロゴ、カラー、フォントを調整可能  
- 🔒 **セキュア**: IAM認証による安全なAPI呼び出し  

---

## 🏗️ アーキテクチャ

### システム全体構成

```
                                 🔐 IAM認証
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│     Client      │────│   API Gateway        │────│      Lambda         │
│ (Web/Mobile/CLI)│    │   (HTTP/REST API)    │    │     Functions       │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
                                 │                            │
                       ┌─────────┴─────────┐                  │
                       ▼                   ▼                  ▼
        ┌─────────────────────┐  ┌─────────────────────┐   ┌──────────────┐
        │  POST /generate     │  │  POST /get-url      │   │      S3      │
        │ PowerPoint生成API   │  │ ダウンロードURL取得   │   │presentations/│
        └─────────────────────┘  └─────────────────────┘   └──────────────┘
```

### 詳細フロー

```
📱 Client Request (PowerPoint生成)
│
├─ 🔑 AWS Signature V4 認証
│   ├─ Access Key ID
│   ├─ Secret Access Key  
│   └─ 署名計算
│
▼
🌐 API Gateway (IAM認証)
│   ├─ CORS処理
│   ├─ 認証チェック
│   └─ リクエスト転送
│
▼
⚡ Lambda: autoslidegen-pptx-generator
│   ├─ slideData解析
│   ├─ PowerPoint生成 (python-pptx)
│   ├─ デザイン適用 (環境変数ベース)
│   └─ S3アップロード
│
▼
📦 S3 Bucket
│   ├─ ファイル保存: presentations/{uuid}.pptx
│   └─ 署名付きURL生成 (1時間有効)
│
▼
📱 Client Response
    ├─ downloadUrl: 署名付きダウンロードURL
    ├─ s3Key: S3オブジェクトキー
    └─ message: 処理結果メッセージ

────────────────────────────────────────────────────────

📱 Client Request (URL再取得)
│
├─ 🔑 AWS Signature V4 認証
│
▼
🌐 API Gateway (IAM認証)
│
▼
⚡ Lambda: autoslidegen-get-download-url
│   ├─ fileId/s3Key検証
│   ├─ S3ファイル存在確認
│   └─ 新しい署名付きURL生成
│
▼
📱 Client Response
    ├─ downloadUrl: 新しい署名付きURL
    └─ expiresIn: 有効期限 (秒)
```

### 環境設定

```
┌─────────────────────┐    ┌─────────────────────┐
│   Lambda環境変数    │    │   ローカル開発環境   │
├─────────────────────┤    ├─────────────────────┤
│🔧 必須設定          │    │📁 .env ファイル     │
│ • S3_BUCKET_NAME    │    │ • 全Lambda環境変数   │
│ • AWS_REGION        │    │ • AWS認証情報       │
│                     │    │ • APIエンドポイント │
│🎨 オプション設定     │    │                     │
│ • LOGO_HEADER_URL   │    │🧪 テストスクリプト   │
│ • THEME_COLOR_*     │    │ • test_local.py     │
│ • FONT_SIZE_*       │    │ • test_api_*.py     │
│ • SLIDE_WIDTH_PX    │    │                     │
└─────────────────────┘    └─────────────────────┘
```

---

## 📦 ファイル構成

```
AutoSlideGen/
├── README.md                         # このファイル
├── lambda-pptx-generator.py         # メインのLambda関数（PowerPoint生成）
├── lambda-pptx-get_download_url.py  # URL取得用Lambda関数（S3署名付きURL生成）
├── create_PowerPoint.py             # PowerPoint生成スクリプト
├── create_PowerPoint_Separate.py    # PowerPoint生成スクリプト（分離版）
├── DEPLOY_GUIDE.md                   # デプロイガイド
├── .env                              # ローカル環境用の環境変数（要作成）
├── .env_example                      # 環境変数サンプル
├── pyproject.toml                    # 依存関係定義
├── uv.lock                           # 依存関係ロックファイル
├── test/                             # テストスクリプト
│   ├── test_local.py                 # ローカル環境テスト用スクリプト
│   └── test_get_url_local.py        # URL取得テスト用スクリプト
├── output/                           # ローカル実行時の出力ディレクトリ
├── package/                          # Lambdaデプロイ用パッケージ用ディレクトリ
├── utils/                            # ユーティリティディレクトリ
└── docs/                             # ドキュメント類
    └── プロンプト/                    # AI用プロンプト集
```

### 📁 Lambda関数の説明

| ファイル | 機能 | Lambda/ローカル対応 |
|--------|------|-------------------|
| `lambda-pptx-generator.py` | PowerPointファイルを生成しS3にアップロード | 両方対応 |
| `lambda-pptx-get_download_url.py` | S3キーまたはファイルIDからダウンロードURLを生成 | 両方対応 |

---

## 🚀 クイックスタート

### 1. ローカル開発環境のセットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd AutoSlideGen

# Python 3.13以上が必要です
python --version  # 3.13以上であることを確認

# uvを使用（推奨）
uv sync --extra dev

# または通常のvenv + pipを使用
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate.ps1  # Windows PowerShell
pip install python-pptx requests pillow python-dotenv boto3

# 環境変数ファイルを作成
cp .env_example .env
# .envファイルを編集して必要な値を設定
```

### 2. ローカルでのテスト実行

```bash
# Python環境が適切に設定されていることを確認
python --version

# PowerPoint生成のテスト
python test/test_local.py

# URL取得機能のテスト
python test/test_get_url_local.py

# 生成されたファイルは output/ ディレクトリに保存されます
ls output/  # 生成されたPowerPointファイルを確認
```

---

## 📤 AWS Lambdaへのデプロイ

‼️ **重要**: 詳細なデプロイ手順は [`DEPLOY_GUIDE.md`](./DEPLOY_GUIDE.md) を参照してください。

### 🚀 クイックデプロイ概要

1. **パッケージ作成**: `lambda_generate_package.zip` と `lambda_geturl_package.zip` を作成
2. **Lambda関数作成**: 2つのLambda関数をAWSコンソールで作成
3. **環境変数設定**: 必須とオプションの環境変数を設定
4. **API Gateway設定**: `/generate` と `/get-url` エンドポイントを作成
5. **テスト実行**: エンドツーエンドでの動作確認

### 📌 デプロイ用パッケージの作成方法

#### PowerPoint生成Lambda用パッケージ

```bash
# 1. パッケージ作成スクリプト
cd AutoSlideGen

# 2. 依存関係をインストール
mkdir package
uv pip install --target ./package python-pptx requests pillow

# 3. zipパッケージを作成
cd package && zip -r ../lambda_generate_package.zip . && cd ..
zip -u lambda_generate_package.zip lambda-pptx-generator.py

# 4. パッケージサイズを確認（50MB以下であることを確認）
ls -lh lambda_generate_package.zip
```

#### URL取得Lambda用パッケージ

```bash
# 軽量パッケージ（外部依存関係なし）
zip lambda_geturl_package.zip lambda-pptx-get_download_url.py
```

> 💡 **ヒント**: 詳細な手順とトラブルシューティングは [`DEPLOY_GUIDE.md`](./DEPLOY_GUIDE.md) を参照してください。

### 📌 Lambda関数の作成と設定

#### AWS Lambda関数の設定例

| 設定項目 | PowerPoint生成Lambda | URL取得Lambda |
|----------|----------------------|---------------|
| **関数名** | `autoslidegen-pptx-generator` | `autoslidegen-get-download-url` |
| **ランタイム** | Python 3.13 | Python 3.13 |
| **メモリ** | 1024MB | 256MB |
| **タイムアウト** | 60秒 | 10秒 |
| **パッケージ** | `lambda_generate_package.zip` | `lambda_geturl_package.zip` |

#### API Gateway エンドポイント例

| エンドポイント | メソッド | 統合先 | 機能 |
|---------------|---------|--------|------|
| `/generate` | POST | PowerPoint生成Lambda | スライドデータからPowerPoint生成 |
| `/get-url` | POST | URL取得Lambda | S3ファイルの署名付きURL取得 |

> ⚠️ **重要**: 実際の設定値は環境に合わせて調整してください。詳細は [`DEPLOY_GUIDE.md`](./DEPLOY_GUIDE.md) を参照。

#### 必須環境変数

```bash
# 両Lambda関数で共通
S3_BUCKET_NAME = "your-presentation-bucket"
S3_PREFIX = "presentations/"
AWS_REGION = "ap-northeast-1"
```

> 📖 **詳細設定**: オプション環境変数の詳細は [`.env_example`](./.env_example) と [`DEPLOY_GUIDE.md`](./DEPLOY_GUIDE.md) を参照してください。

---

## 📊 使用方法

### API経由での利用

#### 1. PowerPoint生成

```python
import requests
import json

# PowerPoint生成リクエスト
slide_data = [
    {
        'type': 'title',
        'title': 'プレゼンテーションタイトル',
        'date': '2025年1月'
    },
    {
        'type': 'content',
        'title': 'アジェンダ',
        'points': ['項目1', '項目2', '項目3']
    }
]

response = requests.post(
    'https://your-api-gateway-url/generate',
    json={'slideData': str(slide_data)},
    headers={'Content-Type': 'application/json'}
)

result = response.json()
print(f"Download URL: {result['downloadUrl']}")
print(f"S3 Key: {result['s3Key']}")

# S3キーを保存（後でURL再取得用）
s3_key = result['s3Key']
```

#### 2. ダウンロードURLの再取得

```python
# 保存したS3キーを使って新しいダウンロードURLを取得
response = requests.post(
    'https://your-api-gateway-url/get-url',
    json={'s3Key': s3_key},  # または {'fileId': 'file-id-here'}
    headers={'Content-Type': 'application/json'}
)

result = response.json()
print(f"New Download URL: {result['downloadUrl']}")
```

### ローカル環境での利用

#### テストスクリプトを使用（推奨）

```bash
# PowerPoint生成のテスト
python test/test_local.py

# URL取得のテスト
python test/test_get_url_local.py
```

### Lambda関数デプロイ後のテスト

#### 📋 テスト準備

```bash
# テスト用環境変数ファイルを作成
cp .env.test_example .env.test

# .env.testファイルを編集してAPIエンドポイントを設定
# API_GENERATE_ENDPOINT_URL="https://your-api-id.execute-api.region.amazonaws.com/stage/generate"
# API_GET_URL_ENDPOINT_URL="https://your-api-id.execute-api.region.amazonaws.com/stage/get-url"
```

#### 🧪 APIテスト実行

**簡易テスト（推奨）**
```bash
# 基本的な動作確認（認証なし）
python test/test_api_simple.py
```

**完全テストスイート**
```bash
# 包括的なテスト（認証設定含む）
python test/test_api_endpoints.py
```

#### 🔐 認証設定

**.env.testで認証タイプを設定:**

```bash
# 認証なし（開発環境）
TEST_AUTH_TYPE="none"

# IAM認証（本番環境推奨）
TEST_AUTH_TYPE="iam"
AWS_ACCESS_KEY_ID="your-access-key"
AWS_SECRET_ACCESS_KEY="your-secret-key"

# APIキー認証
TEST_AUTH_TYPE="api_key"
API_KEY="your-api-key"
```

#### Pythonコードから直接利用

```python
import importlib.util
import json

# Lambda関数をローカルで実行
def load_lambda_function(file_path, module_name):
    """ハイフン付きファイル名のLambda関数をロード"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lambda_handler

# PowerPoint生成
lambda_handler = load_lambda_function(
    "lambda-pptx-generator.py", 
    "lambda_pptx_generator"
)

# スライドデータの例
slide_data = [
    {"type": "title", "title": "サンプルプレゼンテーション", "date": "2025年1月"},
    {"type": "content", "title": "アジェンダ", "points": ["項目1", "項目2", "項目3"]}
]

event = {"body": json.dumps({"slideData": str(slide_data)})}
response = lambda_handler(event, None)
result = json.loads(response['body'])

print(f"✅ 生成完了: {result.get('localPath', result.get('downloadUrl'))}")
```

---

## 🎨 スライドタイプ

| タイプ | 説明 | 主なパラメータ |
|--------|------|----------------|
| `title` | タイトルスライド | title, date |
| `section` | セクション区切り | title, sectionNo |
| `content` | 箇条書き | title, subhead, points |
| `cards` | カードレイアウト | title, items, columns |
| `table` | 表 | title, headers, rows |
| `compare` | 2項目比較 | title, leftTitle, rightTitle, leftItems, rightItems |
| `process` | プロセス/手順 | title, steps |
| `timeline` | タイムライン | title, milestones |
| `diagram` | レーン図 | title, lanes |
| `progress` | 進捗バー | title, items |
| `closing` | クロージング | （ロゴのみ） |

---

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### ローカル環境

| 問題 | 解決方法 |
|------|----------|
| `ModuleNotFoundError: python-dotenv` | `uv add python-dotenv` または `pip install python-dotenv` |
| `.env`ファイルが読み込まれない | `.env_example`をコピーして`.env`を作成し、必要な値を設定 |
| `output/`ディレクトリが見つからない | 自動作成されない場合は `mkdir output` で作成 |
| Python 3.13エラー | `python --version` で3.13以上を確認、必要に応じて更新 |

#### AWS Lambda環境

| 問題 | 解決方法 |
|------|----------|
| **タイムアウトエラー** | PowerPoint生成Lambdaのタイムアウトを60秒以上に設定 |
| **メモリ不足エラー** | PowerPoint生成Lambdaのメモリを1024MB以上に増加 |
| **パッケージサイズエラー** | パッケージが50MB以下か確認、超過時はS3経由デプロイを使用 |
| **S3アクセスエラー** | IAMロールにS3の`PutObject`と`GetObject`権限が付与されているか確認 |
| **環境変数エラー** | `S3_BUCKET_NAME`など必須環境変数が設定されているか確認 |

#### API Gateway

| 問題 | 解決方法 |
|------|----------|
| **CORSエラー** | API GatewayでCORSを正しく設定、`OPTIONS`メソッドも有効化 |
| **認証エラー** | IAM認証の場合、適切な認証情報をリクエストヘッダーに含める |
| **404エラー** | エンドポイントパス（`/generate`, `/get-url`）が正しいか確認 |

> 🔍 **詳細デバッグ**: [`DEPLOY_GUIDE.md`](./DEPLOY_GUIDE.md) のデバッグセクションを参照してください。

---

## 🧪 テストスクリプト一覧

| テストファイル | 用途 | 実行環境 |
|---------------|------|----------|
| `test/test_local.py` | ローカル環境でのLambda関数テスト | ローカル |
| `test/test_get_url_local.py` | ローカル環境でのURL取得テスト | ローカル |
| `test/test_api_simple.py` | Lambda関数の基本APIテスト | デプロイ後 |
| `test/test_api_endpoints.py` | Lambda関数の包括的APIテスト | デプロイ後 |

### テスト実行例

```bash
# ローカル開発時
python test/test_local.py
python test/test_get_url_local.py

# Lambda関数デプロイ後
python test/test_api_simple.py        # 基本テスト
python test/test_api_endpoints.py     # 詳細テスト
```

---

## 📚 参考資料・関連リンク

### 技術ドキュメント
- [🐍 python-pptx Documentation](https://python-pptx.readthedocs.io/) - PowerPoint操作ライブラリ
- [⚡ uv Documentation](https://docs.astral.sh/uv/) - 高速Pythonパッケージマネージャー
- [🔧 AWS Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

### AWS サービス
- [🚀 AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [🌐 API Gateway HTTP API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [📦 Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)

### プロジェクト固有ドキュメント
- [`DEPLOY_GUIDE.md`](./DEPLOY_GUIDE.md) - 詳細デプロイ手順とトラブルシューティング
- [`CLAUDE.md`](./CLAUDE.md) - AutoSlideGen用Claude Code設定
- [`.env_example`](./.env_example) - 環境変数設定例
- [`.env.test_example`](./.env.test_example) - APIテスト用環境変数設定例

---

## 📄 ライセンス

本プロジェクトは実験目的です。商用利用時は依存ライブラリのライセンスをご確認ください。

---

## 🤝 貢献

プルリクエストや Issue の報告を歓迎します！

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
