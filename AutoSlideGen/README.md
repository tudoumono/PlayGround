## AutoSlideGen/README.md（見やすさ重視版）

```markdown
# AutoSlideGen 🚀
AIの力で **テキストからプロフェッショナルなPowerPoint** を自動生成するサーバーレスシステム

---

## 📋 概要
AutoSlideGenは、非構造化テキスト（議事録・記事・メモなど）を解析し、論理的に整理されたPowerPointを自動生成します。  
AWS Lambda + API Gateway による **完全サーバーレス構成** を採用しています。

### ✨ 主な特徴
- 🎨 **多様なスライドタイプ**: 箇条書き、表、グラフ、タイムライン、進捗バー、比較表など  
- 🎯 **Google風デザイン**: モダン＆プロフェッショナルなデザインテンプレート  
- ⚡ **サーバーレス**: AWS Lambda + API Gatewayによるスケーラブル構成  
- 📝 **スピーカーノート自動生成**: 各スライドに適切な発表原稿を付与  
- 🔧 **柔軟なカスタマイズ**: 環境変数でロゴやカラーを調整可能  
- 🔒 **セキュア**: IAM認証による安全なAPI呼び出し  

---

## 🏗️ アーキテクチャ

```

┌─────────────┐      ┌──────────────┐      ┌─────────────────────┐      ┌──────────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│      Lambda         │─────▶│       S3         │
│ (Salesforce)│ IAM  │   (HTTP)     │      │(lambda-pptx-generator)│     │lambda-pptx-generator│
└─────────────┘      └──────────────┘      └─────────────────────┘      └──────────────────┘
│                           │
▼                           ▼
┌──────────────┐      ┌────────────────────────────┐
│ API Gateway  │◀─────│        Lambda              │
│  (HTTP)       │      │(lambda-pptx-get\_download\_url)│
└──────────────┘      └────────────────────────────┘

````

---

## 🛠️ AWS セットアップ手順

### ✅ 前提条件
- AWSアカウント  
- AWS マネジメントコンソールへのアクセス  
- Python 3.13以上（ローカルテスト用）  

---

### 1. S3バケットの作成
- バケット名: `lambda-pptx-generator`  
- リージョン: 任意（Lambdaと同一リージョン推奨）  
- その他の設定: デフォルトのまま  

---

### 2. IAMポリシーの作成
ポリシー名: `lambda-pptx-generator`  

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::lambda-pptx-generator/*"
    }
  ]
}
````

---

### 3. Lambda関数の作成

#### 📌 PowerPoint生成関数（`lambda-pptx-generator`）

1. Lambda関数を作成（Python 3.13, x86\_64）
2. `lambda_function.py` をコピー＆ペースト
3. レイヤーに `lambda-layer-requests/layer.zip` を追加
4. 環境変数 `S3_BUCKET_NAME=lambda-pptx-generator` を設定
5. タイムアウト: 60秒 / メモリ: 1024MB
6. IAMロールにポリシーをアタッチ

#### 📌 URL生成関数（`lambda-pptx-get_download_url`）

1. Lambda関数を作成（Python 3.13）
2. `get_url_lambda.py` をコピー＆ペースト
3. 環境変数 `S3_BUCKET_NAME=lambda-pptx-generator` を設定
4. タイムアウト: 10秒 / メモリ: 256MB
5. IAMロールにポリシーをアタッチ

---

### 4. API Gateway設定

#### `/generate` → PowerPoint生成

* トリガー: API Gateway (HTTP API)
* セキュリティ: AWS IAM
* メソッド: POST

#### `/get-url` → ダウンロードURL取得

* トリガー: API Gateway (HTTP API)
* セキュリティ: AWS IAM
* メソッド: POST

---

## 📦 ファイル構成

```
AutoSlideGen/
├── README.md
├── lambda_function.py              # PowerPoint生成用Lambda
├── get_url_lambda.py               # URL生成用Lambda
├── create_PowerPoint.py            # ローカル実行用
├── create_PowerPoint_Separate.py   # 分離型実装
├── test_lambda.py                  # ローカルテスト用
├── test_API.py                     # API統合テスト用
├── .env_example                    # 環境変数サンプル
├── pyproject.toml                  # 依存関係
├── uv.lock
├── lambda-layer-requests/          # Lambdaレイヤー
│   ├── python/
│   └── layer.zip
└── Googleスライドが一瞬で完成する奇跡のプロンプト*.txt
```

---

## 🧪 ローカルテスト

### 依存関係のインストール

```bash
# uv推奨
uv sync

# または pip
pip install python-pptx Pillow requests boto3 python-dotenv
```

### Lambda関数のテスト

```bash
python test_lambda.py
```

### API統合テスト

```bash
cp .env_example .env   # .env作成
# API URLを.envに記入
python test_API.py
```

> ⚠️ API呼び出しには **IAM認証（SigV4署名）** が必須です。

---

## 📝 使用方法

### API経由での呼び出し例

```python
# boto3 & SigV4署名付きリクエスト例
```

（省略・詳細はREADME本文参照）

---

## 🔧 カスタマイズ

* `LOGO_HEADER_URL` : ヘッダーロゴURL
* `LOGO_CLOSING_URL` : クロージングロゴURL
* `FOOTER_ORGANIZATION_NAME` : フッター組織名
* `DEFAULT_FONT_FAMILY` : デフォルトフォント
* `THEME_COLOR_PRIMARY` : テーマカラー（HEX）

---

## 🐛 トラブルシューティング

* **タイムアウト** → タイムアウト延長 / メモリ増加
* **S3アクセスエラー** → IAMロール/環境変数確認
* **ライブラリエラー** → レイヤーZIPの追加確認
* **API認証エラー** → SigV4署名＆IAM権限確認

---

## 📚 参考

* [AWS Lambda](https://docs.aws.amazon.com/lambda/)
* [API Gateway HTTP API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
* [python-pptx](https://python-pptx.readthedocs.io/)
* [元記事](https://note.com/majin_108/n/n39235bcacbfc)

---

## 📄 ライセンス

本プロジェクトは実験目的です。商用利用時は依存ライブラリのライセンスをご確認ください。
