#!/bin/bash

echo "🎯 EXACT Lambda環境互換レイヤーの構築開始..."

# 古いファイルを削除
rm -rf python-exact/
rm -f lambda-layer-exact.zip

# 正確なLambda環境でビルド
echo "🐳 EXACT Lambda環境でDockerビルド..."
docker build -f Dockerfile.exact -t lambda-layer-exact .

# コンテナからpython/ディレクトリをコピー
echo "📂 EXACT環境からライブラリをコピー..."
docker run --rm -v $(pwd):/output lambda-layer-exact cp -r /opt/python /output/python-exact

# 権限修正
sudo chown -R $(whoami):$(whoami) python-exact/

# ZIPファイル作成
echo "📦 EXACT互換ZIPファイル作成..."
cd python-exact && zip -r ../lambda-layer-exact.zip . && cd ..

# サイズ確認
size=$(stat -c%s lambda-layer-exact.zip)
size_mb=$(echo "scale=2; $size / 1024 / 1024" | bc)

echo "✅ EXACT Lambda互換レイヤー構築完了！"
echo "📦 ファイル名: lambda-layer-exact.zip"
echo "📊 サイズ: ${size_mb} MB"

# 動作テスト
echo "🧪 EXACT環境での動作テスト..."
PYTHONPATH=python-exact python3 -c "
try:
    from lxml import etree
    print('✅ lxml.etree インポート成功 (EXACT版)')
    from pptx import Presentation  
    print('✅ python-pptx インポート成功 (EXACT版)')
    import requests
    print('✅ requests インポート成功 (EXACT版)')
    from PIL import Image
    print('✅ PIL インポート成功 (EXACT版)')
    print('🎉 EXACT版レイヤーの全テストが成功!')
except ImportError as e:
    print(f'❌ インポートエラー: {e}')
"

echo "🚀 lambda-layer-exact.zip をLambdaレイヤーとしてアップロードできます！"