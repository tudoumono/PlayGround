# デプロイ用パッケージ作成手順

このドキュメントでは、`lambda-pptx-generator.py` と `lambda-pptx-get_download_url.py` のデプロイ用パッケージの作成方法を説明します。

## 📦 PowerPoint生成用Lambda（lambda-pptx-generator.py）

### 概要
- **機能**: PowerPointファイルを生成し、S3にアップロード
- **依存ライブラリ**: python-pptx, requests, pillow
- **パッケージサイズ**: 約30-40MB（依存ライブラリ含む）
- **推奨メモリ**: 1024MB以上
- **推奨タイムアウト**: 60秒以上

### PowerShellを使用（Windows）

```powershell
# 1. 作業ディレクトリをクリーンアップ
Remove-Item -Path "./package" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "./lambda_generate_package.zip" -Force -ErrorAction SilentlyContinue

# 2. パッケージディレクトリを作成
New-Item -ItemType Directory -Path "./package"

# 3. Lambda用の依存関係をインストール（boto3はLambda環境に含まれているため不要）
pip install --target ./package python-pptx requests pillow

# 4. 依存関係をzipファイルに圧縮
cd package
Compress-Archive -Path ./* -DestinationPath ../lambda_generate_package.zip
cd ..

# 5. Lambda関数本体を追加
Compress-Archive -Update -Path lambda-pptx-generator.py -DestinationPath lambda_generate_package.zip

# 6. ファイルサイズを確認（50MB以下であることを確認）
$size = (Get-Item lambda_generate_package.zip).Length / 1MB
Write-Host "Package size: $([math]::Round($size, 2)) MB"
```

### Bashを使用（Linux/Mac/WSL）

```bash
# 1. 作業ディレクトリをクリーンアップ
rm -rf package/
rm -f lambda_generate_package.zip

# 2. パッケージディレクトリを作成
mkdir package

# 3. Lambda用の依存関係をインストール
pip install --target ./package python-pptx requests pillow

# 4. zipファイルを作成
cd package
zip -r ../lambda_generate_package.zip .
cd ..

# 5. Lambda関数本体を追加
zip -u lambda_generate_package.zip lambda-pptx-generator.py

# 6. ファイルサイズを確認
ls -lh lambda_generate_package.zip
```

## 🔗 URL取得用Lambda（lambda-pptx-get_download_url.py）

### 概要
- **機能**: S3に保存されたPowerPointファイルの署名付きURLを生成
- **依存ライブラリ**: なし（boto3はLambdaランタイムに含まれる）
- **パッケージサイズ**: 数KB
- **推奨メモリ**: 256MB
- **推奨タイムアウト**: 10秒

# このLambda関数は追加の外部ライブラリを必要としません
# boto3とjsonはLambda環境にプリインストールされています
# そのため、単純にzipファイルに関数コードを追加するだけでデプロイ可能です

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
- **関数名**: `lambda-geturl-generator`
- **ランタイム**: Python 3.13
- **パッケージ**: `lambda_geturl_package.zip`
- **ハンドラー**: `lambda-pptx-get_download_url.lambda_handler`
- **タイムアウト**: 10秒（単純なURL生成処理のため）
- **メモリ**: 256MB（軽量な処理のため最小限で十分）
- **役割**:
  - S3オブジェクトキーを受け取る
  - ファイルの存在を確認
  - 署名付きURLを生成
  - クライアントにダウンロードURLを返す

### 2. 環境変数の設定

両方のLambda関数で共通：
```
S3_BUCKET_NAME = your-presentation-bucket
S3_PREFIX = presentations/
ALLOWED_ORIGINS = *
PRESIGNED_URL_EXPIRY = 3600
```

PowerPoint生成用関数のみ（オプション）：
```
LOGO_HEADER_URL = https://your-logo-url.com/logo.png
LOGO_CLOSING_URL = https://your-logo-url.com/logo.png
FOOTER_ORGANIZATION_NAME = Your Company Name
DEFAULT_FONT_FAMILY = Arial
# その他のデザイン設定...
```

### 3. IAMロールの設定

両方のLambda関数に以下のポリシーをアタッチ：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:HeadObject"
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

### 4. API Gatewayの設定

2つのエンドポイントを作成：

1. **PowerPoint生成エンドポイント**
   - パス: `/lambda-pptx-generator`
   - メソッド: POST
   - 統合先: `lambda-pptx-generator`

2. **URL取得エンドポイント**
   - パス: `/lambda-pptx-get_download_url`
   - メソッド: POST
   - 統合先: `lambda-geturl-generator`

両エンドポイントでCORSを有効化し、必要に応じてIAM認証を設定してください。

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

### デバッグ方法

#### CloudWatch Logsを使用したデバッグ
1. AWSコンソールでCloudWatch > Log groupsへ移動
2. `/aws/lambda/lambda-pptx-generator`または`/aws/lambda/lambda-geturl-generator`を選択
3. 最新のログストリームを確認
4. エラーメッセージやスタックトレースを確認

#### ローカルテスト
```python
# Lambda関数をローカルでテスト
import json
from lambda_pptx_generator import lambda_handler  # または from lambda_pptx_get_download_url import lambda_handler

# テストイベントを作成
test_event = {
    "body": json.dumps({
        # テストデータ
    })
}

# 関数を実行
response = lambda_handler(test_event, None)
print(json.dumps(response, indent=2))
```
