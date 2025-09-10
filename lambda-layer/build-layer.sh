#!/bin/bash

# Lambda互換レイヤーをDockerで構築するスクリプト

echo "🐳 Lambda互換レイヤーの構築を開始..."

# 古いpython/ディレクトリを削除
rm -rf python/

# Dockerイメージをビルド
echo "📦 Dockerイメージをビルド中..."
docker build -t lambda-layer-builder .

# コンテナを実行してpython/ディレクトリをコピー
echo "📂 ライブラリをコンテナからコピー中..."
docker run --rm -v $(pwd):/output lambda-layer-builder cp -r /opt/python /output/

# 権限を修正
sudo chown -R $(whoami):$(whoami) python/

# ZIPファイルを作成
echo "📦 ZIPファイルを作成中..."
zip -r lambda-layer-docker.zip python/

# ファイルサイズを確認
size=$(stat -c%s lambda-layer-docker.zip)
size_mb=$(echo "scale=2; $size / 1024 / 1024" | bc)

echo "✅ Lambda互換レイヤー構築完了!"
echo "📦 ファイル名: lambda-layer-docker.zip"
echo "📊 サイズ: ${size_mb} MB"

# 動作テスト
echo "🧪 動作テストを実行中..."
PYTHONPATH=python python3 -c "
try:
    from lxml import etree
    print('✅ lxml.etree インポート成功 (Docker版)')
    from pptx import Presentation
    print('✅ python-pptx インポート成功 (Docker版)')
    import requests
    print('✅ requests インポート成功 (Docker版)')
    from PIL import Image
    print('✅ PIL インポート成功 (Docker版)')
    print('🎉 Docker版レイヤーの全テストが成功!')
except ImportError as e:
    print(f'❌ インポートエラー: {e}')
"