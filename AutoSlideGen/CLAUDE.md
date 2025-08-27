# AutoSlideGen 専用 Claude Code 設定

## 言語設定
- 今後、すべての回答は日本語で行ってください
- コメントやドキュメント作成時も日本語を使用してください

## 🚨 **AutoSlideGen 最重要制約事項**

### プロジェクト構成の理解
```
AutoSlideGen/
├── lambda-pptx-generator.py        # メインのPowerPoint生成Lambda関数
├── lambda-pptx-get_download_url.py # S3署名付きURL生成Lambda関数
├── create_PowerPoint.py            # PowerPoint生成コアロジック
├── create_PowerPoint_Separate.py   # 分離版PowerPoint生成
├── pyproject.toml                  # Python依存関係定義（uv管理）
├── test/                           # テストスクリプト
│   ├── test_local.py               # ローカル環境テスト
│   └── test_get_url_local.py      # URL取得テスト
└── docs/                           # プロンプト・ドキュメント
```

### コーディング規約
#### PEP8準拠（AutoSlideGen仕様）
- 行の長さ: 88文字以内（PowerPointコード対応）
- 関数名: snake_case
- クラス名: PascalCase
- 定数: UPPER_CASE（CONFIG、SETTINGS等）
- Lambda関数のファイル名: ハイフン使用（lambda-*.py）

#### 型ヒント必須
```python
# ✅ AutoSlideGen形式
def create_slide(
    slide_data: list[dict],
    presentation: Presentation,
    config: dict
) -> Presentation:
    """スライドを作成"""
    pass

# AWS Lambda用型ヒント
from typing import Dict, Any, Optional

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda関数のハンドラー"""
    pass
```

#### PowerPoint専用パターン
- python-pptxライブラリの活用
- EMU単位とピクセル単位の変換処理
- スライドタイプ別の処理分岐
- 環境変数による設定管理

### AWS Lambda 制約事項

#### Lambda関数ファイル規約
```python
# lambda-pptx-generator.py の基本構造
import json
import os
import boto3
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        # CORS対応
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        }
        
        # 処理実装
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
```

#### 環境変数管理パターン
```python
# 必須環境変数
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
if not S3_BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME environment variable is required")

# オプション環境変数（デフォルト値付き）
LOGO_URL = os.environ.get('LOGO_HEADER_URL', '')
THEME_COLOR = os.environ.get('THEME_COLOR_PRIMARY', '4285F4')
```

### PowerPoint生成制約事項

#### スライドタイプ定義
- `title`: タイトルスライド
- `section`: セクション区切り
- `content`: 箇条書き
- `cards`: カードレイアウト
- `table`: 表形式
- `compare`: 2項目比較
- `process`: プロセス図
- `timeline`: タイムライン
- `diagram`: レーン図
- `progress`: 進捗バー
- `closing`: クロージング

#### デザイン制約
```python
# Google風デザイン設定（変更禁止）
CONFIG = {
    'BASE_PX': {'W': 960, 'H': 540},
    'COLORS': {
        'PRIMARY': RGBColor(66, 133, 244),    # Google Blue
        'RED': RGBColor(234, 67, 53),         # Google Red
        'YELLOW': RGBColor(251, 188, 4),      # Google Yellow
        'GREEN': RGBColor(52, 168, 83),       # Google Green
    },
    'FONTS': {
        'DEFAULT': 'Arial',
        'SIZE_TITLE': Pt(45),
        'SIZE_SECTION': Pt(38),
        'SIZE_CONTENT': Pt(28),
    }
}
```

### エラーハンドリング必須事項

#### Lambda用ログ設定
```python
import logging

# Lambda環境用ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 使用例
logger.info(f"📊 スライド生成開始: {len(slide_data)}スライド")
logger.error(f"❌ PowerPoint生成エラー: {str(e)}", exc_info=True)
```

#### S3操作エラーハンドリング
```python
import boto3
from botocore.exceptions import ClientError

try:
    s3_client = boto3.client('s3')
    s3_client.upload_fileobj(pptx_buffer, bucket_name, s3_key)
    logger.info(f"✅ S3アップロード完了: {s3_key}")
except ClientError as e:
    error_code = e.response['Error']['Code']
    logger.error(f"❌ S3エラー ({error_code}): {str(e)}")
    raise
```

#### PowerPoint生成エラー
```python
from pptx.exc import PackageNotFoundError

try:
    presentation = create_presentation(slide_data)
except Exception as e:
    logger.error(f"❌ PowerPoint生成失敗: {str(e)}")
    return {
        'statusCode': 500,
        'body': json.dumps({
            'error': 'PowerPoint generation failed',
            'details': str(e)
        })
    }
```

### ファイル管理制約事項

#### Lambda環境での制約
- `/tmp/`ディレクトリのみ書き込み可能
- ファイルサイズ制限: 512MB
- 実行時間制限: 60秒（推奨設定）

#### ローカル環境での制約
- `output/`ディレクトリへの出力
- 相対パス使用
- `.env`ファイルでの設定管理

### テスト要件

#### 必須テストケース
- スライドタイプ別生成テスト
- エラーハンドリングテスト
- S3アップロード/ダウンロードテスト
- 環境変数設定テスト

#### テストスクリプト実行
```bash
# ローカルテスト
python test/test_local.py

# URL取得テスト
python test/test_get_url_local.py
```

### デプロイメント制約事項

#### Lambdaパッケージ要件
- python-pptx, requests, pillow の依存関係
- boto3はLambda環境標準（パッケージ不要）
- zipファイルサイズ: 50MB以下
- レイヤー使用推奨（大きな依存関係の場合）

#### 環境別設定
- **開発**: ローカル環境 + .env
- **ステージング**: Lambda + 環境変数
- **プロダクション**: Lambda + 環境変数 + IAM認証

### API仕様制約事項

#### リクエスト形式
```json
{
    "slideData": "[{\"type\":\"title\",\"title\":\"タイトル\"}]"
}
```

#### レスポンス形式
```json
{
    "downloadUrl": "https://s3-presigned-url",
    "s3Key": "presentations/filename.pptx",
    "localPath": "/tmp/filename.pptx"
}
```

---

### 今後のセッション継続時の手順

1. **AutoSlideGen専用設定の確認**
2. **Lambda関数とローカル環境の動作確認**
3. **PowerPoint生成ロジックの理解**
4. **AWS環境設定の確認**
5. **制約事項の確認と遵守**

これらの制約は**AutoSlideGenプロジェクト専用**であり、**他のプロジェクトには適用しない**こと。