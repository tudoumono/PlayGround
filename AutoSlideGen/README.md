## AutoSlideGen/README.md

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

## ファイル構成と役割

プロジェクトは、AIにスライドの内容を生成させる**プロンプト**と、その内容から実際にPowerPointファイルを生成する**Pythonスクリプト**で構成されています。

### 📜 プロンプト（AIへの指示書）

AIに対して、どのような形式でスライドデータ（`slide_data`）を生成してほしいかを定義するファイル群です。バージョンアップの経緯がわかります。

* **`Googleスライドが一瞬で完成する奇跡のプロンプト.txt`**
    * **役割:** Google Apps Script (GAS) 向けのオリジナルプロンプトです。
    * **特徴:** AIが`slideData`（JavaScriptの配列）を生成し、GASのコードテンプレート全体と共に出力するよう指示します。

* **`Googleスライドが一瞬で完成する奇跡のプロンプトPython版_Ver. 1.0.txt`**
    * **役割:** GAS版をPython (python-pptx) 向けに移植した最初のバージョンです。
    * **特徴:** `content`, `cards`, `table`など基本的なスライドタイプに対応しています。

* **`Googleスライドが一瞬で完成する奇跡のプロンプトPython版_Ver. 1.1.txt`**
    * **役割:** Ver 1.0を改良した更新版です。
    * **特徴:** バグ修正や細かな表現の調整が加えられています。

* **`Googleスライドが一瞬で完成する奇跡のプロンプトPython版_Ver. 2.0.txt`**
    * **役割:** 対応するスライドタイプを大幅に増やしたメジャーアップデート版です。
    * **特徴:** `compare`, `process`, `timeline`, `diagram`, `progress`といった表現力豊かなスライドタイプが追加され、GAS版とほぼ同等の機能になりました。

* **`Googleスライドが一瞬で完成する奇跡のプロンプトPython版_Ver. 2.0_Separate版.txt`**
    * **役割:** API的な利用を想定した「データ分離型」のプロンプトです。
    * **特徴:** AIの出力を`slide_data`のPythonリスト**そのもの**に限定します。これにより、PythonスクリプトとAIの生成物を明確に分離できます。

---

### 🐍 Pythonスクリプト
* **`create_PowerPoint.py`**
    * **役割:** プロンプトVer. 2.0と対になるスクリプトです。
    * **特徴:** スクリプト内にサンプル`slide_data`が直接記述されており、AIはこの部分を置き換える形で完全なスクリプトを生成します。

* **`create_PowerPoint_Separate.py`**
    * **役割:** `Separate版`プロンプトからの出力を受け取ってスライドを生成する、データ分離型のスクリプトです。
    * **特徴:** `slide_data`を文字列として引数で受け取る関数や、AWS Lambdaで実行するための`lambda_handler`が含まれており、外部システムとの連携が容易になっています。

* **`lambda_function.py`**
    * **役割:** PowerPoint生成用のメインLambda関数です。
    * **特徴:** API Gatewayからのリクエストを受け取り、PowerPointを生成してS3にアップロード、署名付きURLを返却します。環境変数でロゴやカラーのカスタマイズも可能です。

* **`get_url_lambda.py`**
    * **役割:** S3に保存されたファイルの新しいダウンロードURL生成用Lambda関数です。
    * **特徴:** S3キーを受け取り、新しい署名付きURL（有効期限1時間）を生成して返却します。URL期限切れ時の再生成に使用します。

* **`test_lambda.py`**
    * **役割:** `create_PowerPoint_Separate.py`の動作をローカル環境でテストするためのスクリプトです。
    * **特徴:** AWS Lambdaの実行環境を模倣し、`lambda_handler`にテストデータを渡してPowerPointファイルが正しく生成されるかを確認できます。

* **`test_API.py`**
    * **役割:** API Gateway経由でLambda関数をテストするスクリプトです。
    * **特徴:** 実際のHTTPリクエストを送信し、PowerPoint生成APIとURL取得APIの両方をエンドツーエンドで動作確認できます。`.env`ファイルから環境変数を読み込みます。


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
