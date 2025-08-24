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

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────────┐      ┌──────────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│      Lambda         │─────▶│       S3         │
│ (Salesforce)│ IAM  │   (HTTP)     │      │(lambda_function.py) │      │ presentations/   │
└─────────────┘      └──────────────┘      └─────────────────────┘      └──────────────────┘
                                                      │                      ↑
                                                      ▼                      │
                                            ┌─────────────────────┐      │
                                            │   環境変数          │      │
                                            │ - S3_BUCKET_NAME    │      │
                                            │ - LOGO_HEADER_URL   │      │
                                            │ - THEME_COLOR_*     │      │
                                            └─────────────────────┘      │
                                                                             │
┌─────────────┐      ┌──────────────┐      ┌─────────────────────┐      │
│   Client    │─────▶│ API Gateway  │─────▶│      Lambda         │──────┘
│             │      │  /get-url    │      │(get_url_lambda.py)  │
└─────────────┘      └──────────────┘      └─────────────────────┘
```

---

## 📦 ファイル構成

```
AutoSlideGen/
├── README.md                       # このファイル
├── lambda_function.py              # メインのLambda関数（PowerPoint生成）
├── get_url_lambda.py               # URL取得用Lambda関数（S3署名付きURL生成）
├── test_local.py                   # ローカル環境テスト用スクリプト
├── test_API.py                     # API統合テスト用
├── .env                            # ローカル環境用の環境変数（要作成）
├── .env_example                    # 環境変数サンプル
├── pyproject.toml                  # 依存関係定義
├── uv.lock                         # 依存関係ロックファイル
├── output/                         # ローカル実行時の出力ディレクトリ
└── docs/                           # ドキュメント類
    └── プロンプト/                 # AI用プロンプト集
```

### 📁 Lambda関数の説明

| ファイル | 機能 | Lambda/ローカル対応 |
|--------|------|-------------------|
| `lambda_function.py` | PowerPointファイルを生成しS3にアップロード | 両方対応 |
| `get_url_lambda.py` | S3キーまたはファイルIDからダウンロードURLを生成 | 両方対応 |

---

## 🚀 クイックスタート

### 1. ローカル開発環境のセットアップ

```powershell
# リポジトリをクローン
git clone <repository-url>
cd AutoSlideGen

# Python仮想環境を作成（Python 3.13以上）
python -m venv .venv

# 仮想環境を有効化 (PowerShell)
.venv\Scripts\activate.ps1

# 依存関係をインストール（uvを使用）
uv pip install -r pyproject.toml --extra dev

# または pipを使用
pip install python-pptx requests pillow python-dotenv boto3

# 環境変数ファイルを作成
copy .env_example .env
# .envファイルを編集して必要な値を設定
```

### 2. ローカルでのテスト実行

```powershell
# 仮想環境が有効化されていることを確認
# テストスクリプトを実行
python test_local.py

# 生成されたファイルは output/ ディレクトリに保存されます
```

---

## 📤 AWS Lambdaへのデプロイ

‼️ **重要**: 詳細なデプロイ手順は [`DEPLOY_GUIDE.md`](./DEPLOY_GUIDE.md) を参照してください。

### 📌 デプロイ用パッケージの作成方法

#### 方法1: PowerShellを使用（Windows）

```powershell
# 1. 作業ディレクトリをクリーンアップ
Remove-Item -Path "./package" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "./lambda_package.zip" -Force -ErrorAction SilentlyContinue

# 2. パッケージディレクトリを作成
New-Item -ItemType Directory -Path "./package"

# 3. Lambda用の依存関係をインストール
# （boto3はLambda環境に含まれているため不要）
pip install --target ./package python-pptx requests pillow

# 4. 依存関係をzipファイルに圧縮
cd package
Compress-Archive -Path ./* -DestinationPath ../lambda_package.zip
cd ..

# 5. Lambda関数本体を追加
Compress-Archive -Update -Path lambda_function.py -DestinationPath lambda_package.zip

# 6. ファイルサイズを確認（50MB以下であることを確認）
$size = (Get-Item lambda_package.zip).Length / 1MB
Write-Host "Package size: $([math]::Round($size, 2)) MB"
```

#### 方法2: Bashを使用（Linux/Mac/WSL）

```bash
# 1. 作業ディレクトリをクリーンアップ
rm -rf package/
rm -f lambda_package.zip

# 2. パッケージディレクトリを作成
mkdir package

# 3. Lambda用の依存関係をインストール
pip install --target ./package python-pptx requests pillow

# 4. zipファイルを作成
cd package
zip -r ../lambda_package.zip .
cd ..

# 5. Lambda関数本体を追加
zip -u lambda_package.zip lambda_function.py

# 6. ファイルサイズを確認
ls -lh lambda_package.zip
```

### 📌 Lambda関数の作成と設定

#### 1. Lambda関数の構成詳細

##### **PowerPoint生成用Lambda関数**

| 設定項目 | 設定値 |
|----------|--------|
| **ファイル** | `lambda_function.py` |
| **Lambda関数名** | `lambda-pptx-generator` |
| **パッケージタイプ** | Zip |
| **ランタイム** | Python 3.13 |
| **メモリ** | 1024MB |
| **タイムアウト** | 60秒 |
| **アーキテクチャ** | x86_64 |
| **トリガー** | API Gateway |

**API Gateway設定:**
- **エンドポイント**: `POST /generate`
- **認可**: IAM
- **プロトコル**: HTTP
- **APIエンドポイントタイプ**: Regional

##### **URL取得用Lambda関数**

| 設定項目 | 設定値 |
|----------|--------|
| **ファイル** | `get_url_lambda.py` |
| **Lambda関数名** | `lambda-pptx-get_download_url` |
| **パッケージタイプ** | Zip |
| **ランタイム** | Python 3.13 |
| **メモリ** | 1024MB |
| **タイムアウト** | 10秒 |
| **アーキテクチャ** | x86_64 |
| **トリガー** | API Gateway |

**API Gateway設定:**
- **エンドポイント**: `POST /get-url`
- **認可**: IAM  
- **プロトコル**: HTTP
- **APIエンドポイントタイプ**: Regional

> ⚠️ **注意**: 上記の設定値は推奨値です。実際の環境に合わせて自由に変更してください。

#### 2. Lambda関数の作成手順

1. AWS Lambdaコンソールで新しい関数を作成
   - 上記の表に従って各設定を行う

2. 作成した`lambda_package.zip`をアップロード
   - 「コード」タブ → 「アップロード元」 → 「.zipファイル」

#### 3. 環境変数の設定

「設定」タブ → 「環境変数」で以下を設定：

**必須環境変数:**
```
S3_BUCKET_NAME = your-presentation-bucket
```

**オプション環境変数（デザインカスタマイズ）:**
```
# ブランディング
LOGO_HEADER_URL = https://your-logo-url.com/logo.png
LOGO_CLOSING_URL = https://your-logo-url.com/logo.png
FOOTER_ORGANIZATION_NAME = Your Company Name

# フォント設定
DEFAULT_FONT_FAMILY = Arial
FONT_SIZE_TITLE = 45
FONT_SIZE_SECTION = 38
FONT_SIZE_CONTENT_TITLE = 28
FONT_SIZE_SUBHEAD = 18
FONT_SIZE_BODY = 14
FONT_SIZE_FOOTER = 9

# カラー設定（#を除いた6桁の16進数）
THEME_COLOR_PRIMARY = 4285F4
THEME_COLOR_RED = EA4335
THEME_COLOR_YELLOW = FBBC04
THEME_COLOR_GREEN = 34A853
TEXT_PRIMARY_COLOR = 333333
TEXT_WHITE_COLOR = FFFFFF
BACKGROUND_WHITE_COLOR = FFFFFF
BACKGROUND_GRAY_COLOR = F8F9FA
CARD_BG_COLOR = FFFFFF
CARD_BORDER_COLOR = DADCE0

# スライドサイズ
SLIDE_WIDTH_PX = 960
SLIDE_HEIGHT_PX = 540

# セキュリティ設定
ALLOWED_ORIGINS = *
PRESIGNED_URL_EXPIRY = 3600
S3_PREFIX = presentations/
```

#### 4. Lambdaレイヤーの設定（オプション）

大きな依存関係がある場合、Lambdaレイヤーを使用することでデプロイを効率化できます。
`lambda-layer-requests`ディレクトリがプロジェクトに含まれています。

#### 5. IAMロールの設定

Lambda関数のIAMロールに以下のポリシーをアタッチ：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-presentation-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### 📌 API Gatewayの設定

#### PowerPoint生成APIの設定

1. **API Gateway（HTTP API）を作成**
   - APIタイプ: HTTP API
   - APIエンドポイントタイプ: Regional

2. **ルート設定**
   - メソッド: `POST`
   - パス: `/generate`
   - 統合先: `lambda-pptx-generator`
   - 認可: IAM

3. **URL取得APIの設定**
   - メソッド: `POST`
   - パス: `/get-url`
   - 統合先: `lambda-pptx-get_download_url`
   - 認可: IAM

4. **CORS設定（必要に応じて）**
   - Access-Control-Allow-Origin: `*` または特定のドメイン
   - Access-Control-Allow-Headers: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
   - Access-Control-Allow-Methods: `OPTIONS,POST`

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

### ローカルでの利用

#### 1. PowerPoint生成

```python
from lambda_function import lambda_handler
import json

# テスト用イベントを作成
event = {
    'body': json.dumps({
        'slideData': str(slide_data)
    })
}

# Lambda関数を実行
response = lambda_handler(event, None)
result = json.loads(response['body'])
print(f"Local file path: {result['localPath']}")
file_id = result['s3Key']  # ローカルではファイル名
```

#### 2. URL再取得（ローカルファイルパス）

```python
from get_url_lambda import lambda_handler
import json

# URL取得用イベント
event = {
    'body': json.dumps({
        'fileId': file_id  # または 's3Key': file_name
    })
}

# Lambda関数を実行
response = lambda_handler(event, None)
result = json.loads(response['body'])
print(f"Local file path: {result['localPath']}")
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

### ローカル環境

| 問題 | 解決方法 |
|------|----------|
| `ModuleNotFoundError: python-dotenv` | `pip install python-dotenv` を実行 |
| `.env`ファイルが読み込まれない | ファイルパスと環境変数名を確認 |
| 出力ファイルが見つからない | `output/`ディレクトリを確認 |

### Lambda環境

| 問題 | 解決方法 |
|------|----------|
| タイムアウトエラー | タイムアウトを60秒以上に延長 |
| メモリ不足エラー | メモリを1024MB以上に増加 |
| S3アクセスエラー | IAMロールの権限を確認 |
| `ModuleNotFoundError` | デプロイパッケージに依存関係が含まれているか確認 |
| 環境変数エラー | Lambda設定で`S3_BUCKET_NAME`が設定されているか確認 |

---

## 📚 参考資料

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway HTTP API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [python-pptx Documentation](https://python-pptx.readthedocs.io/)
- [元記事](https://note.com/majin_108/n/n39235bcacbfc)

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
