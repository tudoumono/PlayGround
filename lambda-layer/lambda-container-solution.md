# 🐳 Lambda コンテナイメージ方式による最終解決策

## 問題の根本原因
- Python 3.12用のlxmlレイヤーが**Klayersでは提供されていない**
- 自作レイヤーではバイナリ互換性の問題が解決できない
- lxmlのC拡張モジュールがLambda環境で正常に動作しない

## 🚀 コンテナイメージ方式の実装

### 1. ECR用Dockerfileの作成
```dockerfile
FROM public.ecr.aws/lambda/python:3.12

# 作業ディレクトリ設定
WORKDIR ${LAMBDA_TASK_ROOT}

# 依存関係インストール
RUN pip install --no-cache-dir python-pptx requests pillow boto3

# Lambda関数をコピー
COPY lambda-pptx-generator.py ${LAMBDA_TASK_ROOT}/

# ハンドラー設定
CMD ["lambda-pptx-generator.lambda_handler"]
```

### 2. 実装手順

#### Step 1: ECRリポジトリ作成
```bash
aws ecr create-repository \
    --repository-name lambda-pptx-generator \
    --region us-east-1
```

#### Step 2: Dockerイメージビルド
```bash
# Dockerfileを作成後
docker build -t lambda-pptx-generator .

# ECRログイン
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.us-east-1.amazonaws.com

# タグ付けとプッシュ
docker tag lambda-pptx-generator:latest \
    123456789012.dkr.ecr.us-east-1.amazonaws.com/lambda-pptx-generator:latest

docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/lambda-pptx-generator:latest
```

#### Step 3: Lambda関数作成
```bash
aws lambda create-function \
    --function-name lambda-pptx-generator-container \
    --package-type Image \
    --code ImageUri=123456789012.dkr.ecr.us-east-1.amazonaws.com/lambda-pptx-generator:latest \
    --role arn:aws:iam::123456789012:role/lambda-execution-role \
    --timeout 300 \
    --memory-size 512
```

### 3. メリット

✅ **完全なバイナリ互換性**  
✅ **依存関係の完全制御**  
✅ **レイヤーサイズ制限なし**  
✅ **デバッグが容易**  
✅ **本番環境での確実性**  

### 4. デメリット

❌ **初期設定が複雑**  
❌ **コールドスタートが若干長い**  
❌ **イメージサイズの管理が必要**  

## 🎯 推奨アクション

### 緊急対応（即時実施可能）
1. **Lambda Python 3.11にダウングレード**
2. **Klayers lxmlレイヤー使用**
   ```
   arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p311-lxml:9
   ```

### 長期解決（推奨）
1. **コンテナイメージ方式への移行**
2. **ECRを使用した本格的な運用**

## ⚡ 即時実行可能な対応

Lambda関数の設定変更:
- **Runtime**: `python3.11` に変更
- **Layer追加**: `arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p311-lxml:9`
- **既存の自作レイヤーを削除**

これで即座にlxml問題が解決されます。