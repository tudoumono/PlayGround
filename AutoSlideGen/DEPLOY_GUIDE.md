# AutoSlideGen Lambda関数 デプロイガイド 🚀

このドキュメントでは、AutoSlideGenのAWS Lambda関数のデプロイ手順を詳しく説明します。

## 📋 デプロイ対象

| Lambda関数 | ファイル名 | 機能 |
|-----------|------------|------|
| PowerPoint生成 | `lambda-pptx-generator.py` | スライドデータからPowerPointを生成しS3保存 |
| URL取得 | `lambda-pptx-get_download_url.py` | S3ファイルの署名付きURLを生成 |

## 📦 PowerPoint生成用Lambda（lambda-pptx-generator.py）

### 概要
- **機能**: PowerPointファイルを生成し、S3にアップロード
- **依存ライブラリ**: python-pptx, requests, pillow
- **パッケージサイズ**: 約30-40MB（依存ライブラリ含む）
- **推奨メモリ**: 1024MB以上
- **推奨タイムアウト**: 60秒以上

### 🔧 デプロイパッケージ作成手順

#### PowerShellを使用（Windows）

```powershell
# 1. AutoSlideGenディレクトリに移動
cd AutoSlideGen

# 2. 作業ディレクトリをクリーンアップ
Remove-Item -Path "./package" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "./lambda_generate_package.zip" -Force -ErrorAction SilentlyContinue

# 3. パッケージディレクトリを作成
New-Item -ItemType Directory -Path "./package"

# 4. Python仮想環境から依存関係をインストール
# 注意: uvを使用している場合はuv pipを使用
uv pip install --target ./package python-pptx requests pillow
# または通常のpip
# pip install --target ./package python-pptx requests pillow

# 5. 依存関係をzipファイルに圧縮
cd package
Compress-Archive -Path ./* -DestinationPath ../lambda_generate_package.zip
cd ..

# 6. Lambda関数本体を追加
Compress-Archive -Update -Path lambda-pptx-generator.py -DestinationPath lambda_generate_package.zip

# 7. ファイルサイズを確認（50MB以下であることを確認）
$size = (Get-Item lambda_generate_package.zip).Length / 1MB
Write-Host "📦 パッケージサイズ: $([math]::Round($size, 2)) MB"
if ($size -lt 50) {
    Write-Host "✅ パッケージサイズが制限内です"
} else {
    Write-Host "❌ パッケージサイズが50MBを超えています。S3経由のデプロイが必要です"
}
```

#### Bashを使用（Linux/Mac/WSL）

```bash
# 1. AutoSlideGenディレクトリに移動
cd AutoSlideGen

# 2. 作業ディレクトリをクリーンアップ
rm -rf package/
rm -f lambda_generate_package.zip

# 3. パッケージディレクトリを作成
mkdir package

# 4. Python仮想環境から依存関係をインストール
# uvを使用している場合
uv pip install --target ./package python-pptx requests pillow
# または通常のpip
# pip install --target ./package python-pptx requests pillow

# 5. zipファイルを作成
cd package
zip -r ../lambda_generate_package.zip .
cd ..

# 6. Lambda関数本体を追加
zip -u lambda_generate_package.zip lambda-pptx-generator.py

# 7. ファイルサイズを確認
echo "📦 パッケージサイズ:"
ls -lh lambda_generate_package.zip

# パッケージサイズチェック
SIZE=$(stat -f%z lambda_generate_package.zip 2>/dev/null || stat -c%s lambda_generate_package.zip)
SIZE_MB=$((SIZE / 1024 / 1024))
if [ $SIZE_MB -lt 50 ]; then
    echo "✅ パッケージサイズが制限内です (${SIZE_MB}MB)"
else
    echo "❌ パッケージサイズが50MBを超えています (${SIZE_MB}MB)。S3経由のデプロイが必要です"
fi
```

## 🔗 URL取得用Lambda（lambda-pptx-get_download_url.py）

### 概要
- **機能**: S3に保存されたPowerPointファイルの署名付きURLを生成
- **依存ライブラリ**: なし（boto3はLambdaランタイムに含まれる）
- **パッケージサイズ**: 数KB
- **推奨メモリ**: 256MB
- **推奨タイムアウト**: 10秒

### 🔧 デプロイパッケージ作成手順

```bash
# 1. 単一ファイルのzipパッケージを作成
cd AutoSlideGen
zip lambda_geturl_package.zip lambda-pptx-get_download_url.py

# 2. ファイルサイズを確認
echo "📦 URL取得Lambda パッケージサイズ:"
ls -lh lambda_geturl_package.zip
```

> ℹ️ **注意**: このLambda関数は外部ライブラリを必要としないため、関数ファイルのみをzipにする簡単な作成方法で十分です。

## 📝 デプロイ手順

### 1. Lambda関数の作成

#### PowerPoint生成用関数
- **関数名**: `lambda-pptx-generator`
- **ランタイム**: Python 3.13
- **パッケージ**: `lambda_generate_package.zip`
- **ハンドラー**: `lambda-pptx-generator.lambda_handler`
- **タイムアウト**: 60秒（大量のスライド生成に対応）
- **メモリ**: 1024MB（画像処理とPPTファイル生成のため）
- **役割**: 
  - JSON形式のプレゼンテーションデータを受け取る
  - PowerPointファイルを生成
  - ロゴやフッターを追加
  - S3にファイルをアップロード

#### URL取得用関数
- **関数名**: `autoslidegen-get-download-url`
- **ランタイム**: Python 3.13
- **パッケージ**: `lambda_geturl_package.zip`
- **ハンドラー**: `lambda-pptx-get_download_url.lambda_handler`
- **タイムアウト**: 10秒（単純なURL生成処理のため）
- **メモリ**: 256MB（軽量な処理のため最小限で十分）
- **役割**:
  - S3オブジェクトキーまたはファイルIDを受け取る
  - S3ファイルの存在を確認
  - 署名付きURLを生成（有効期限: 1時間）
  - クライアントにダウンロードURLを返す

### 2. 環境変数の設定

#### 必須環境変数（両Lambda関数共通）
```bash
S3_BUCKET_NAME = "your-presentation-bucket"
S3_PREFIX = "presentations/"
AWS_REGION = "ap-northeast-1"
PRESIGNED_URL_EXPIRY = "3600"
ALLOWED_ORIGINS = "*"
```

#### PowerPoint生成Lambda専用環境変数（オプション）
```bash
# ブランディング設定
LOGO_HEADER_URL = "https://your-logo-url.com/logo.png"
LOGO_CLOSING_URL = "https://your-logo-url.com/logo.png"
FOOTER_ORGANIZATION_NAME = "Your Company Name"

# フォント設定
DEFAULT_FONT_FAMILY = "Arial"
FONT_SIZE_TITLE = "45"
FONT_SIZE_SECTION = "38"
FONT_SIZE_CONTENT_TITLE = "28"
FONT_SIZE_SUBHEAD = "18"
FONT_SIZE_BODY = "14"
FONT_SIZE_FOOTER = "9"

# カラーパレット（#を除く6桁の16進数）
THEME_COLOR_PRIMARY = "4285F4"    # Google Blue
THEME_COLOR_RED = "EA4335"        # Google Red
THEME_COLOR_YELLOW = "FBBC04"     # Google Yellow
THEME_COLOR_GREEN = "34A853"      # Google Green
TEXT_PRIMARY_COLOR = "333333"     # Dark Gray
TEXT_WHITE_COLOR = "FFFFFF"       # White
BACKGROUND_WHITE_COLOR = "FFFFFF"
BACKGROUND_GRAY_COLOR = "F8F9FA"
CARD_BG_COLOR = "FFFFFF"
CARD_BORDER_COLOR = "DADCE0"

# スライドサイズ
SLIDE_WIDTH_PX = "960"
SLIDE_HEIGHT_PX = "540"

# デバッグ設定
DEBUG_MODE = "false"
VERBOSE_ERRORS = "false"
LOG_LEVEL = "INFO"
```

> 💡 **ヒント**: `.env_example`ファイルに全ての環境変数例が記載されています。参考にしてください。

### 3. IAM設定（IAM認証使用時）

#### 3-1. Lambda実行ロール

両Lambda関数の**実行ロール**に以下のポリシーをアタッチ：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:HeadObject"
      ],
      "Resource": "arn:aws:s3:::your-presentation-bucket/*"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:ap-northeast-1:*:log-group:/aws/lambda/autoslidegen-*"
    }
  ]
}
```

#### 3-2. API呼び出し用IAMユーザー/ロール

API Gateway（IAM認証）を呼び出すための**クライアント用IAM権限**：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "APIGatewayInvoke",
      "Effect": "Allow",
      "Action": [
        "execute-api:Invoke"
      ],
      "Resource": [
        "arn:aws:execute-api:ap-northeast-1:*:*/*/POST/generate",
        "arn:aws:execute-api:ap-northeast-1:*:*/*/POST/get-url"
      ]
    }
  ]
}
```

> 📝 **重要**: 上記の`Resource`のARNは実際のAPI Gateway IDに置き換えてください

#### 3-3. IAMユーザー作成手順

**テスト専用IAMユーザーの作成（推奨）:**

1. AWSコンソール → IAM → ユーザー → 「ユーザーを作成」
2. **ユーザー名**: `autoslidegen-api-test-user`
3. **アクセス許可**: 「既存のポリシーを直接アタッチ」
4. **カスタムポリシー作成**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "execute-api:Invoke",
         "Resource": "arn:aws:execute-api:ap-northeast-1:YOUR_ACCOUNT_ID:YOUR_API_ID/*/POST/*"
       }
     ]
   }
   ```
5. **アクセスキー作成**: 「アクセスキー」タブでプログラムアクセス用キーを作成

### 4. API Gatewayの設定

#### HTTP API（推奨）またはREST APIで2つのエンドポイントを作成

| エンドポイント | パス | メソッド | 統合先Lambda関数 | 説明 |
|---------------|------|---------|------------------|------|
| PowerPoint生成 | `/generate` | POST | `autoslidegen-pptx-generator` | スライドデータからPowerPointを生成 |
| URL取得 | `/get-url` | POST | `autoslidegen-get-download-url` | S3ファイルの署名付きURLを取得 |

#### CORS設定

両エンドポイントで以下のCORS設定を行ってください：

```json
{
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
  "Access-Control-Allow-Methods": "OPTIONS,POST"
}
```

#### 認証設定（IAM認証）

**API Gateway でのIAM認証設定:**

1. **API Gateway コンソール** → 該当のAPI → 「認可」
2. **各ルート**（`/generate`, `/get-url`）で以下を設定:
   - **認可タイプ**: `AWS_IAM`
   - **認可スコープ**: `$default`

**HTTP API でのIAM認証設定:**

```json
{
  "Routes": {
    "POST /generate": {
      "AuthorizationType": "AWS_IAM"
    },
    "POST /get-url": {
      "AuthorizationType": "AWS_IAM"
    }
  }
}
```

**REST API でのIAM認証設定:**

1. **リソース** → **メソッド** → **メソッド実行**
2. **認証**: `AWS_IAM`を選択
3. **API キーの必要性**: `false`

> 🔐 **セキュリティ**: IAM認証により、AWSアクセスキー・シークレットキーによる署名認証が必要になります。

## 🔧 トラブルシューティング

### 共通の問題

#### 1. Lambda関数がタイムアウトする
**原因**: 処理時間が設定したタイムアウトを超えている
**解決策**:
- PowerPoint生成用: タイムアウトを60秒以上に増やす
- URL取得用: 通常は10秒で十分だが、必要に応じて調整

#### 2. S3アクセス権限エラー
**エラー**: `AccessDenied: Access Denied`
**解決策**:
- Lambda関数のIAMロールにS3アクセス権限があるか確認
- S3バケット名が環境変数と一致しているか確認
- S3バケットポリシーでLambdaからのアクセスが許可されているか確認

#### 3. メモリ不足
**エラー**: `Runtime.ExitError`
**解決策**:
- PowerPoint生成用: メモリを1024MB以上に増やす（最大3008MBまで）
- URL取得用: 256MBで通常十分

### PowerPoint生成用Lambda固有の問題

#### 1. パッケージサイズが大きすぎる
**エラー**: `RequestEntityTooLargeException`
**解決策**:
- パッケージサイズが50MBを超える場合は、S3経由でデプロイ
- 不要な依存関係を削除
- Lambdaレイヤーの使用を検討

#### 2. ライブラリが見つからない
**エラー**: `ModuleNotFoundError: No module named 'pptx'`
**解決策**:
- パッケージング時に`python-pptx`が正しくインストールされているか確認
- LambdaのPythonバージョンとローカルのPythonバージョンが一致しているか確認

### URL取得用Lambda固有の問題

#### 1. 署名付きURLが有効期限切れ
**エラー**: `SignatureDoesNotMatch`
**解決策**:
- `PRESIGNED_URL_EXPIRY`環境変数を適切な値に設定（デフォルト: 3600秒）
- クライアント側でURLをキャッシュしていないか確認

#### 2. ファイルが存在しない
**エラー**: `NoSuchKey`
**解決策**:
- PowerPoint生成Lambdaが正常に完了しているか確認
- S3バケット名とプレフィックスが一致しているか確認
- ファイル名に特殊文字が含まれていないか確認

## 🧪 デプロイ前のローカルテスト

デプロイ前にローカル環境でLambda関数をテストできます：

### テストスクリプトの実行

```bash
# AutoSlideGenディレクトリに移動
cd AutoSlideGen

# PowerPoint生成のローカルテスト
python test/test_local.py

# URL取得のローカルテスト  
python test/test_get_url_local.py
```

### .envファイルの設定

ローカルテスト用に `.env` ファイルを作成：

```bash
# .env_exampleをコピーして編集
cp .env_example .env
# 必要な環境変数を設定
```

## 🔍 デバッグ方法

### CloudWatch Logsを使用したデバッグ

1. AWSコンソールで **CloudWatch** > **Log groups** へ移動
2. 以下のロググループを確認：
   - `/aws/lambda/autoslidegen-pptx-generator`
   - `/aws/lambda/autoslidegen-get-download-url`
3. 最新のログストリームを確認
4. エラーメッセージやスタックトレースを確認

### ローカルデバッグ

```python
# Lambda関数をローカルでテスト
import json
import importlib.util

# lambda-pptx-generator.pyをロード（ハイフン対応）
spec = importlib.util.spec_from_file_location(
    "lambda_pptx_generator", 
    "lambda-pptx-generator.py"
)
lambda_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_module)

# テストイベントを作成
test_event = {
    "body": json.dumps({
        "slideData": "[{\"type\":\"title\",\"title\":\"テストタイトル\"}]"
    })
}

# 関数を実行
response = lambda_module.lambda_handler(test_event, None)
print(json.dumps(response, indent=2, ensure_ascii=False))
```

## 📋 デプロイチェックリスト

### デプロイ前チェック ✅

- [ ] **ローカルテスト実行**: `test_local.py` と `test_get_url_local.py` が正常実行
- [ ] **依存関係確認**: `pyproject.toml` に必要なライブラリが記載
- [ ] **パッケージサイズ**: Lambda関数パッケージが50MB以下
- [ ] **環境変数準備**: 必須環境変数の値を準備

### デプロイ後チェック ✅

- [ ] **Lambda関数作成**: 2つの関数が正常作成済み
- [ ] **環境変数設定**: 各関数に必要な環境変数が設定済み
- [ ] **IAMロール設定**: S3とCloudWatchへのアクセス権限が付与済み
- [ ] **API Gateway設定**: エンドポイントとCORSが正しく設定済み
- [ ] **IAM認証設定**: API GatewayでIAM認証が有効化済み
- [ ] **テスト用IAMユーザー**: `execute-api:Invoke`権限を持つテストユーザー作成済み
- [ ] **CloudWatch確認**: ログが正常に出力されているか確認
- [ ] **エンドツーエンドテスト**: IAM認証でのAPIコールが成功

### IAM認証テスト手順 🔐

```bash
# 1. テスト設定ファイル準備
cp .env.test_example .env.test

# 2. .env.testファイル編集
# TEST_AUTH_TYPE="iam"
# AWS_ACCESS_KEY_ID="your-test-user-access-key"
# AWS_SECRET_ACCESS_KEY="your-test-user-secret-key"
# API_GENERATE_ENDPOINT_URL="https://your-api-id.execute-api.region.amazonaws.com/stage/generate"
# API_GET_URL_ENDPOINT_URL="https://your-api-id.execute-api.region.amazonaws.com/stage/get-url"

# 3. IAM認証テスト実行
python test/test_api_endpoints.py
```

### トラブルシューティング（IAM認証）🔧

#### よくある認証エラー

| エラーメッセージ | 原因 | 解決方法 |
|-----------------|------|----------|
| `403 Forbidden` | IAM権限不足 | テストユーザーに`execute-api:Invoke`権限を付与 |
| `SignatureDoesNotMatch` | 認証情報エラー | AWS Access Key/Secret Keyを確認 |
| `InvalidSignature` | システム時刻ずれ | NTPでシステム時刻を同期 |
| `UnauthorizedOperation` | リージョン不一致 | API GatewayとAWS設定のリージョンを統一 |

#### デバッグコマンド

```bash
# AWS認証情報の確認
aws sts get-caller-identity

# API Gateway情報の確認
aws apigateway get-rest-apis

# IAMユーザーの権限確認
aws iam list-attached-user-policies --user-name autoslidegen-api-test-user
```
