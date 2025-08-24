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
    """
    
    # テスト用のslideDataを定義
    slide_data = [
        {
            'type': 'title',
            'title': 'テストプレゼンテーション',
            'date': '2025年1月',
            'notes': 'このスライドはローカル環境でのテストです'
        },
        {
            'type': 'section',
            'title': 'セクション1: はじめに',
            'sectionNo': 1
        },
        {
            'type': 'content',
            'title': 'コンテンツスライド',
            'subhead': 'サブヘッダーのテスト',
            'points': [
                '最初のポイント',
                '**太字**のテキストを含むポイント',
                '[[ハイライト]]されたテキスト',
                '最後のポイント'
            ]
        },
        {
            'type': 'cards',
            'title': 'カードレイアウト',
            'items': [
                {'title': 'カード1', 'desc': '説明文1'},
                {'title': 'カード2', 'desc': '説明文2'},
                {'title': 'カード3', 'desc': '説明文3'},
                {'title': 'カード4', 'desc': '説明文4'}
            ],
            'columns': 2
        },
        {
            'type': 'closing',
            'notes': 'ご清聴ありがとうございました'
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
