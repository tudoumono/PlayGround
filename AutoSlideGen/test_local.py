#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ローカル環境でlambda_function.pyをテストするためのスクリプト
"""

import json
import sys
import os

# lambda_functionをインポート
from lambda_function import lambda_handler

def test_local_lambda():
    """
    ローカル環境でLambda関数をテストする
    すべてのスライドタイプをテストできる包括的なデータセット
    """
    
    # テスト用のslideDataを定義（全11種類のスライドタイプを網羅）
    slide_data = [
        # 1. タイトルスライド
        {
            'type': 'title',
            'title': 'AutoSlideGen 全機能テスト',
            'date': '2025年1月',
            'notes': 'このプレゼンテーションは、すべてのスライドタイプをテストするために作成されました'
        },
        
        # 2. セクションスライド（第1章）
        {
            'type': 'section',
            'title': '第1章: 基本的なスライドタイプ',
            'sectionNo': 1,
            'notes': '基本的なテキストベースのスライドを紹介します'
        },
        
        # 3. コンテンツスライド（箇条書き）
        {
            'type': 'content',
            'title': 'コンテンツスライドの機能',
            'subhead': 'インラインスタイルのサポート',
            'points': [
                '通常のテキストポイント',
                '**太字**のテキストを含むポイント',
                '[[ハイライト]]されたテキストの例',
                '**太字**と[[ハイライト]]を**組み合わせた**例',
                '最後のポイントです'
            ],
            'notes': '箇条書きスライドでは、太字やハイライトなどのインラインスタイルが使用できます'
        },
        
        # 4. カードスライド
        {
            'type': 'cards',
            'title': 'カードレイアウトの例',
            'subhead': '複数カラムでの表示',
            'items': [
                {'title': '機能1', 'desc': 'AIによる自動生成'},
                {'title': '機能2', 'desc': 'Google風デザイン'},
                {'title': '機能3', 'desc': 'サーバーレス構成'},
                {'title': '機能4', 'desc': '環境変数対応'},
                {'title': '機能5', 'desc': 'ローカル開発可能'},
                {'title': '機能6', 'desc': 'カスタマイズ可能'}
            ],
            'columns': 3,
            'notes': 'カードレイアウトは情報を視覚的に整理するのに適しています'
        },
        
        # 5. テーブルスライド
        {
            'type': 'table',
            'title': '性能比較表',
            'subhead': '各環境での実行時間',
            'headers': ['環境', '実行時間', 'メモリ使用量', 'コスト'],
            'rows': [
                ['ローカル環境', '2.5秒', '256MB', '無料'],
                ['Lambda (512MB)', '4.2秒', '180MB', '$0.001'],
                ['Lambda (1024MB)', '2.8秒', '200MB', '$0.002'],
                ['Lambda (2048MB)', '1.9秒', '220MB', '$0.004']
            ],
            'notes': 'テーブルスライドでデータを構造化して表示できます'
        },
        
        # 6. セクションスライド（第2章）
        {
            'type': 'section',
            'title': '第2章: 高度なビジュアライゼーション',
            'sectionNo': 2,
            'notes': 'より視覚的で複雑なスライドタイプを紹介します'
        },
        
        # 7. 比較スライド
        {
            'type': 'compare',
            'title': 'Lambda vs ローカル環境',
            'subhead': '実行環境の比較',
            'leftTitle': 'Lambda環境',
            'leftItems': [
                'サーバーレス実行',
                'S3への自動アップロード',
                '署名付きURL生成',
                'スケーラブル',
                'IAM認証'
            ],
            'rightTitle': 'ローカル環境',
            'rightItems': [
                'ローカルPC実行',
                'ファイルシステム保存',
                'ファイルパス返却',
                '開発・デバッグ用',
                '.envファイル認証'
            ],
            'notes': '2つの環境の違いを視覚的に比較できます'
        },
        
        # 8. プロセススライド
        {
            'type': 'process',
            'title': 'PowerPoint生成プロセス',
            'subhead': 'ステップバイステップの流れ',
            'steps': [
                'API Gatewayがリクエストを受信',
                'Lambda関数がトリガーされる',
                'slide_dataをパースして検証',
                'PowerPointファイルを生成',
                'S3にアップロード（Lambda環境）',
                '署名付きURLを返却'
            ],
            'notes': 'プロセスの各ステップを順番に表示します'
        },
        
        # 9. タイムラインスライド
        {
            'type': 'timeline',
            'title': 'プロジェクトロードマップ',
            'subhead': '2024-2025年の開発計画',
            'milestones': [
                {'label': 'プロトタイプ', 'date': '2024年10月', 'state': 'done'},
                {'label': 'Lambda対応', 'date': '2024年12月', 'state': 'done'},
                {'label': '環境変数対応', 'date': '2025年1月', 'state': 'done'},
                {'label': 'UI開発', 'date': '2025年3月', 'state': 'next'},
                {'label': '正式リリース', 'date': '2025年6月', 'state': 'todo'}
            ],
            'notes': 'タイムラインでプロジェクトの進捗を可視化します'
        },
        
        # 10. ダイアグラムスライド（レーン図）
        {
            'type': 'diagram',
            'title': 'システムアーキテクチャ',
            'subhead': 'データフローの可視化',
            'lanes': [
                {
                    'title': 'クライアント',
                    'items': [
                        'リクエスト送信',
                        'レスポンス受信',
                        'ファイルダウンロード'
                    ]
                },
                {
                    'title': 'API Gateway',
                    'items': [
                        '認証チェック',
                        'リクエスト転送',
                        'レスポンス返却'
                    ]
                },
                {
                    'title': 'Lambda',
                    'items': [
                        'データ処理',
                        'PPTX生成',
                        'S3アップロード'
                    ]
                },
                {
                    'title': 'S3',
                    'items': [
                        'ファイル保存',
                        'URL生成',
                        'アクセス管理'
                    ]
                }
            ],
            'notes': 'レーン図でシステムの各コンポーネントの役割を表現します'
        },
        
        # 11. 進捗スライド
        {
            'type': 'progress',
            'title': '機能実装状況',
            'subhead': '各機能の完成度',
            'items': [
                {'label': 'スライド生成機能', 'percent': 100},
                {'label': 'Lambda統合', 'percent': 100},
                {'label': '環境変数対応', 'percent': 100},
                {'label': 'エラーハンドリング', 'percent': 85},
                {'label': 'ユニットテスト', 'percent': 60},
                {'label': 'ドキュメント作成', 'percent': 75},
                {'label': 'UI開発', 'percent': 20}
            ],
            'notes': '各タスクの進捗状況を視覚的に表示します'
        },
        
        # 12. セクションスライド（まとめ）
        {
            'type': 'section',
            'title': '第3章: まとめ',
            'sectionNo': 3,
            'notes': '最後のセクションです'
        },
        
        # 13. 追加のコンテンツスライド
        {
            'type': 'content',
            'title': 'テスト結果サマリー',
            'points': [
                '全11種類のスライドタイプをテスト完了',
                '[[インラインスタイル]]が正常に動作',
                '**環境変数**によるカスタマイズが機能',
                'ローカル環境での実行を確認'
            ],
            'notes': 'すべての機能が正常に動作することを確認しました'
        },
        
        # 14. クロージングスライド
        {
            'type': 'closing',
            'notes': 'ご覧いただきありがとうございました。AutoSlideGenの全機能テストを完了しました。'
        }
    ]
    
    # API Gatewayからのリクエストを模擬
    event = {
        'body': json.dumps({
            'slideData': str(slide_data)
        })
    }
    
    # contextは使用されないのでNoneで良い
    context = None
    
    try:
        print("=" * 60)
        print("ローカル環境でのLambda関数テストを開始します")
        print("=" * 60)
        
        # Lambda関数を実行
        response = lambda_handler(event, context)
        
        # レスポンスを表示
        print("\n" + "=" * 60)
        print("レスポンス:")
        print("=" * 60)
        print(f"Status Code: {response['statusCode']}")
        print(f"Headers: {response['headers']}")
        
        # ボディをパース
        body = json.loads(response['body'])
        print(f"Message: {body.get('message')}")
        print(f"Download URL: {body.get('downloadUrl')}")
        print(f"Is Local: {body.get('isLocal')}")
        
        if response['statusCode'] == 200:
            print("\n" + "=" * 60)
            print("✅ テスト成功!")
            print("=" * 60)
            
            # ローカルファイルのパスを表示
            if body.get('isLocal'):
                download_url = body.get('downloadUrl', '')
                if download_url.startswith('file://'):
                    file_path = download_url.replace('file://', '')
                    print(f"\n生成されたファイル: {file_path}")
                    
                    # ファイルサイズを表示
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"ファイルサイズ: {file_size:,} bytes")
        else:
            print("\n" + "=" * 60)
            print("❌ テスト失敗")
            print("=" * 60)
            print(f"エラー: {body}")
            
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ エラーが発生しました: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_lambda()
