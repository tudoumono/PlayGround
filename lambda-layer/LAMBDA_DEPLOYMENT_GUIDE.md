# Lambda関数デプロイメントガイド

## 🚨 ImportModuleError解決方法

### エラー内容
```
Runtime.ImportModuleError: Unable to import module 'lambda_function': No module named 'lambda_function'
```

### 原因
Lambda関数のハンドラー設定と実際のファイル名が一致していない。

## ✅ 解決方法（2つの選択肢）

### 🔧 **方法1: ハンドラー設定を変更（推奨）**

#### AWS Lambdaコンソールで設定変更：
1. Lambda関数を開く
2. 「設定」タブ → 「一般設定」を選択  
3. 「編集」をクリック
4. **ハンドラー**を変更：
   ```
   lambda-pptx-generator.lambda_handler
   ```
5. 「保存」をクリック

#### メリット：
- 既存のファイル名を維持
- 設定変更のみで解決
- プロジェクト構成が一貫

---

### 📦 **方法2: 標準ファイル名でデプロイ**

#### 用意されたファイル：
- **`lambda_function.py`** - 標準的なファイル名版
- **`lambda-deployment-package.zip`** - デプロイ用パッケージ

#### デプロイ手順：
1. Lambda関数のコードタブを開く  
2. 「Upload from」→ 「.zip file」を選択
3. **`lambda-deployment-package.zip`**をアップロード
4. ハンドラーは `lambda_function.lambda_handler` のまま

#### メリット：
- 標準的な構成
- ハンドラー設定変更不要
- 一般的なLambda構成

---

## 🔄 レイヤーとの組み合わせ

### デプロイ後の手順：
1. **レイヤーを追加**：
   - 「Layers」→ 「Add a layer」
   - **`lambda-layer-pptx-dependencies-uv.zip`**から作成したレイヤーを選択

2. **環境変数を設定**（必要に応じて）：
   ```bash
   S3_BUCKET_NAME=your-bucket-name
   LOGO_HEADER_URL=https://your-logo-url
   THEME_COLOR_PRIMARY=4285F4
   ```

3. **実行ロールの権限確認**：
   - S3への読み書き権限
   - CloudWatch Logsへの書き込み権限

---

## 📁 ファイル構成

### 現在のディレクトリ：
```
lambda-layer/
├── lambda_function.py                        # 標準ファイル名版（新規作成）
├── lambda-deployment-package.zip            # Lambda関数用ZIP（10.54 KB）
├── lambda-layer-pptx-dependencies-uv.zip    # レイヤー用ZIP（13.34 MB）
├── python/                                  # レイヤー依存関係
├── requirements.txt                         # 依存関係定義
├── test_lambda_imports.py                   # テスト用スクリプト
├── README.md                               # レイヤー使用説明
└── LAMBDA_DEPLOYMENT_GUIDE.md              # このファイル
```

---

## 🧪 テスト手順

### 1. 基本テスト
```json
{
  "body": "{\"slideData\":\"[{'type':'title','title':'テストタイトル'}]\"}"
}
```

### 2. エラー確認
- CloudWatch Logsでエラー詳細を確認
- インポートエラーが解決されているかチェック

### 3. 動作確認
- PowerPointファイル生成の成功
- S3アップロードの確認（Lambda環境の場合）

---

## 🎯 **推奨アプローチ**

1. **方法1（ハンドラー変更）**を試す
2. 問題が続く場合は**方法2（標準ファイル名）**を使用
3. レイヤー追加で依存関係のインポートエラーを解決
4. テストイベントで動作確認

これで `Runtime.ImportModuleError` と `lxml ImportError` の両方が解決されます。