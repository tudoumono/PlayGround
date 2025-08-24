# デプロイ用パッケージ作成手順

このドキュメントでは、`lambda_function.py` と `get_url_lambda.py` のデプロイ用パッケージの作成方法を説明します。

## 📦 PowerPoint生成用Lambda（lambda_function.py）

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
Compress-Archive -Update -Path lambda_function.py -DestinationPath lambda_generate_package.zip

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
zip -u lambda_generate_package.zip lambda_function.py

# 6. ファイルサイズを確認
ls -lh lambda_generate_package.zip
```

## 🔗 URL取得用Lambda（get_url_lambda.py）

### PowerShellを使用（Windows）

```powershell
# 1. URL取得用パッケージを作成
# （このLambda関数はboto3のみ使用するため、追加の依存関係は不要）
Remove-Item -Path "./lambda_geturl_package.zip" -Force -ErrorAction SilentlyContinue

# 2. Lambda関数本体をzip化
Compress-Archive -Path get_url_lambda.py -DestinationPath lambda_geturl_package.zip

# 3. ファイルサイズを確認
$size = (Get-Item lambda_geturl_package.zip).Length / 1KB
Write-Host "Package size: $([math]::Round($size, 2)) KB"
```

### Bashを使用（Linux/Mac/WSL）

```bash
# 1. URL取得用パッケージを作成
rm -f lambda_geturl_package.zip

# 2. Lambda関数本体をzip化
zip lambda_geturl_package.zip get_url_lambda.py

# 3. ファイルサイズを確認
ls -lh lambda_geturl_package.zip
```

## 📝 デプロイ手順

### 1. Lambda関数の作成

#### PowerPoint生成用関数
- 関数名: `lambda-pptx-generator`
- ランタイム: Python 3.13
- パッケージ: `lambda_generate_package.zip`
- ハンドラー: `lambda_function.lambda_handler`
- タイムアウト: 60秒
- メモリ: 1024MB

#### URL取得用関数
- 関数名: `lambda-geturl-generator`
- ランタイム: Python 3.13
- パッケージ: `lambda_geturl_package.zip`
- ハンドラー: `get_url_lambda.lambda_handler`
- タイムアウト: 10秒
- メモリ: 256MB

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
   - パス: `/generate`
   - メソッド: POST
   - 統合先: `lambda-pptx-generator`

2. **URL取得エンドポイント**
   - パス: `/get-url`
   - メソッド: POST
   - 統合先: `lambda-geturl-generator`

両エンドポイントでCORSを有効化し、必要に応じてIAM認証を設定してください。
