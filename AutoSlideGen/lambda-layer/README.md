# Lambda Layer for AutoSlideGen（uv版）

## 概要
このレイヤーには、AutoSlideGenのLambda関数(`lambda-pptx-generator.py`)に必要な依存関係が含まれています。  
**uv**を使用してLambda互換（Linux Python 3.12）でインストールされており、lxml ImportErrorが解決済みです。

## 含まれる依存関係
- `python-pptx>=1.0.2` - PowerPoint生成ライブラリ
- `requests>=2.32.5` - HTTP通信ライブラリ
- `pillow>=10.0.0` - 画像処理ライブラリ
- `lxml>=6.0.1` - XMLパーサー（python-pptxの依存関係）

## 修正された問題
❌ **以前の問題**: `Runtime.ImportError: cannot import name "etree" from "lxml"`  
✅ **解決方法**: uvで`--python-platform linux --python-version 3.12`を指定してインストール

## ファイル構成
```
AutoSlideGen/lambda-layer/
├── python/                          # Lambda Layer用ディレクトリ
│   ├── pptx/                       # python-pptxライブラリ
│   ├── lxml/                       # lxmlライブラリ（修正済み）
│   ├── PIL/                        # Pillowライブラリ
│   ├── requests/                   # requestsライブラリ
│   └── その他の依存関係/
├── requirements.txt                 # 依存関係定義
├── lambda-layer-pptx-dependencies-uv.zip  # アップロード用ZIPファイル（修正版）
├── test_lambda_imports.py          # Lambda環境テスト用スクリプト
└── README.md                       # このファイル

```

## 使用方法

### 1. AWS Lambdaレイヤーの作成
1. AWS Management Consoleでのラムダコンソールを開く
2. 左側メニューから「Layers」を選択
3. 「Create layer」をクリック
4. 以下を設定:
   - **Name**: `autoslidegen-dependencies`
   - **Description**: `Dependencies for AutoSlideGen PowerPoint generator`
   - **Upload**: `lambda-layer-pptx-dependencies.zip`をアップロード
   - **Compatible runtimes**: `Python 3.12` または `Python 3.13`

### 2. Lambda関数でレイヤーを使用
1. Lambda関数(`lambda-pptx-generator`)の設定を開く
2. 「Layers」セクションで「Add a layer」をクリック
3. 「Custom layers」を選択
4. 作成したレイヤー(`autoslidegen-dependencies`)を選択
5. 最新バージョンを選択して「Add」

### 3. 動作確認
Lambda関数のコードで以下をテスト:
```python
try:
    from pptx import Presentation
    import requests
    from PIL import Image
    print("✅ 全ての依存関係が正常にインポートされました")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
```

## ファイルサイズ情報
- **ZIP サイズ**: 13.34 MB（uv版・最適化済み）
- **解凍後サイズ**: 約 42 MB
- **Lambda制限**: 50MB（ZIP）/ 250MB（解凍後） - 制限内

## 注意事項

### Python ランタイム互換性
- 作成環境: Python 3.12
- 推奨ランタイム: Python 3.12 または Python 3.13
- Python 3.11以下では互換性の問題が発生する可能性があります

### AWS Lambda制限
- レイヤーの最大サイズ: 50MB（ZIP）
- レイヤー含む総サイズ: 250MB（解凍後）
- レイヤーの最大数: 5個まで

### トラブルシューティング
- **インポートエラー**: Lambdaランタイムバージョンを確認
- **サイズエラー**: 不要な依存関係が含まれていないか確認
- **パフォーマンス**: コールドスタート時間の増加に注意

## 更新手順
依存関係を更新する場合:
1. `requirements.txt`を編集
2. `python/`ディレクトリを削除
3. uvで再インストール: `uv pip install --python-platform linux --python-version 3.12 --only-binary=:all: [パッケージ名] --target python/`
4. 新しいZIPファイルを作成
5. Lambdaレイヤーの新しいバージョンを作成

## ImportError解決のポイント
- **pip使用時**: `Runtime.ImportError: cannot import name "etree" from "lxml"`が発生
- **uv使用時**: `--python-platform linux --python-version 3.12`でLambda環境に適合
- **キー要因**: Linux用バイナリホイールの正確な選択が重要
