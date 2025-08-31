# 📝 Excel質問回答自動転記システム

Win32comを使用して昨年度と今年度のExcelファイル間で質問と回答を比較・自動転記するPythonアプリケーションです。類似度に基づいて自動的に回答を転記し、AIで相違点分析や新規回答生成を行います。

## 🎯 主な機能

- **自動類似度判定**: 昨年度と今年度の質問を比較し、類似度を算出
- **段階的処理**: 類似度に応じて色分けと処理を自動実行
  - **完全一致** (100%): そのまま転記
  - **高類似度** (80%以上): 黄色背景 + AI相違点分析
  - **中類似度** (50%以上): 青色背景 + AI相違点分析
  - **低類似度** (50%未満): 赤色背景 + AI新規回答生成
- **GUI操作**: Tkinterによる直感的な範囲選択
- **詳細ログ**: 処理結果とエラーを完全記録
- **統計レポート**: JSON形式の詳細統計情報

## 🔧 動作環境

### 必須環境
- **Windows OS** (Win32com使用のため)
- **Microsoft Excel** がインストールされていること
- **Python 3.8以上**

### 必要ライブラリ
```bash
pip install pywin32 openai python-dotenv
```

## 📦 インストール

1. **リポジトリクローン**
```bash
git clone <repository>
cd Excel
```

2. **依存関係インストール**
```bash
pip install -r requirements.txt
```

3. **環境変数設定** (AI機能使用の場合)
```bash
# .envファイル作成
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

または`config.json`の`ai_settings.api_key`に設定

## 🚀 使用方法

### 1. 基本実行
```bash
python main.py
```

### 2. 操作手順

1. **昨年度Excelファイル選択**
   - ファイル選択ダイアログが表示されます

2. **昨年度範囲選択**
   - 質問欄の範囲をExcel上で選択
   - 回答欄の範囲をExcel上で選択

3. **今年度Excelファイル選択**
   - ファイル選択ダイアログが表示されます

4. **今年度範囲選択**
   - 質問欄の範囲をExcel上で選択
   - 回答欄の範囲をExcel上で選択

5. **処理実行**
   - 確認ダイアログで設定確認
   - プログレスバーで進捗表示
   - 完了後サマリー表示

## 📊 処理結果

### 色分けルール
| 類似度 | 背景色 | 処理内容 |
|--------|--------|----------|
| 100% | 無色 | 昨年度回答をそのまま転記 |
| 80-99% | 🟡 黄色 | 昨年度回答転記 + AI相違点分析 |
| 50-79% | 🔵 青色 | 昨年度回答転記 + AI相違点分析 |
| 0-49% | 🔴 赤色 | AI新規回答生成 |

### 出力ファイル
- **今年度Excelファイル**: 回答転記と色付け済み
- **ログファイル**: `logs/excel_processor_YYYYMMDD_HHMMSS.log`
- **エラーログ**: `logs/errors_YYYYMMDD_HHMMSS.log`
- **統計情報**: `logs/statistics_YYYYMMDD_HHMMSS.json`

## ⚙️ 設定カスタマイズ

`config.json`ファイルで各種設定を変更可能：

```json
{
    "similarity_thresholds": {
        "high": 80,     // 高類似度閾値
        "medium": 50    // 中類似度閾値
    },
    "colors": {
        "high": [255, 255, 0],    // 黄色 (RGB)
        "medium": [0, 176, 240],  // 青色 (RGB)
        "low": [255, 0, 0]        // 赤色 (RGB)
    },
    "ai_settings": {
        "model": "gpt-3.5-turbo",
        "timeout": 10,
        "max_retries": 3
    },
    "excel_settings": {
        "visible": true,        // Excel表示/非表示
        "display_alerts": false // アラート表示/非表示
    }
}
```

## 🤖 AI機能

### 対応プロンプト
1. **高類似度相違点**: 2つの質問の簡潔な相違点説明
2. **中類似度相違点**: 2つの質問の主な違い説明
3. **新規回答生成**: 質問に対する適切な回答生成

### エラーハンドリング
- **タイムアウト**: 10秒
- **リトライ**: 3回まで
- **フォールバック**: AI処理エラー時は"AI処理エラー"を表示

## 📈 統計情報例

```json
{
  "summary": {
    "perfect_match": 15,
    "high_similarity": 8,
    "medium_similarity": 12,
    "low_similarity": 5,
    "errors": 1,
    "total_processed": 41,
    "processing_time_seconds": 45.67
  }
}
```

## ⚠️ 注意事項

### 制限事項
- **Windows専用**: Win32com使用のため
- **Excel必須**: Microsoft Excelがインストールされている必要
- **大量データ**: 1000件以上の場合は処理時間に注意
- **API料金**: OpenAI API使用時は料金が発生

### トラブルシューティング

#### よくあるエラー
1. **"win32com.clientが利用できません"**
   ```bash
   pip install pywin32
   ```

2. **"Excelアプリケーションの起動に失敗"**
   - Microsoft Excelがインストールされているか確認
   - 他のExcelプロセスを終了

3. **"AI処理エラー"**
   - OpenAI APIキーを確認
   - インターネット接続を確認

#### デバッグ手順
1. `logs/`フォルダのログファイルを確認
2. `config.json`の`excel_settings.visible`を`true`に設定
3. 小さなデータセットでテスト実行

## 🧪 テストケース

以下のケースで動作確認済み：
- [x] 質問が完全一致する場合
- [x] 質問が1文字だけ違う場合（高類似度）
- [x] 質問が半分程度同じ場合（中類似度）
- [x] 全く異なる質問の場合（低類似度）
- [x] 今年度に既に回答がある場合
- [x] 空のセルがある場合
- [x] 100件以上のデータ

## 📞 サポート

### FAQ

**Q: 範囲選択がキャンセルされた場合は？**
A: エラーメッセージが表示され、処理が中断されます。最初から実行し直してください。

**Q: AIなしでも使用できますか？**
A: はい。AI APIキーが設定されていない場合は「AI機能が利用できません」というメッセージが表示されますが、基本的な転記処理は実行されます。

**Q: 処理時間の目安は？**
A: 100件程度であれば1-2分程度です（AI処理含む）。

### 開発者情報
- Python 3.8+ 対応
- Win32com.client使用
- OpenAI GPT-3.5/4.0対応
- MIT License

---

## 🏗️ システム構成

```
Excel質問回答自動転記システム/
├── main.py                    # メインプログラム
├── config.json                # 設定ファイル
├── requirements.txt           # 必要ライブラリ一覧
├── README_auto_transfer.md    # このファイル
├── .env.example              # 環境変数テンプレート
├── logs/                     # ログ出力ディレクトリ
│   ├── excel_processor_*.log # 処理ログ
│   ├── errors_*.log          # エラーログ
│   └── statistics_*.json     # 統計情報
└── test_data/                # テスト用データ (オプション)
```

システム正常動作の確認ができましたら、実際のExcelファイルでテストしてください！