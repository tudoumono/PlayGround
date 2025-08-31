#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AutoSlideGen Lambda関数のAPIエンドポイントテストスクリプト

このスクリプトは、デプロイされたLambda関数をAPI Gateway経由でテストします。
- PowerPoint生成API (/generate)
- URL取得API (/get-url)
のエンドツーエンドテストを実行します。
"""

import json
import os
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from urllib.parse import urlparse


class AutoSlideGenAPITester:
    """AutoSlideGen APIテストクラス"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        テスター初期化
        
        Args:
            config_path: 設定ファイルのパス（デフォルト: .env.test）
        """
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.test_results = []
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, str]:
        """テスト設定を読み込み"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / '.env.test'
            
        config = {}
        
        # 環境変数から読み込み（優先）
        env_vars = [
            'API_GENERATE_ENDPOINT_URL',
            'API_GET_URL_ENDPOINT_URL',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_SESSION_TOKEN',
            'AWS_REGION',
            'TEST_AUTH_TYPE'
        ]
        
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                config[var] = value
        
        # .env.testファイルから読み込み
        if Path(config_path).exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(str(config_path))
                for var in env_vars:
                    if var not in config:
                        value = os.environ.get(var)
                        if value:
                            config[var] = value
            except ImportError:
                print("⚠️ python-dotenvがインストールされていません。環境変数を直接使用します。")
        
        # 必須項目チェック
        required = ['API_GENERATE_ENDPOINT_URL', 'API_GET_URL_ENDPOINT_URL']
        missing = [var for var in required if var not in config]
        if missing:
            raise ValueError(f"必須の環境変数が設定されていません: {missing}")
        
        # IAM認証使用時の認証情報チェック
        if config.get('TEST_AUTH_TYPE') == 'iam':
            auth_required = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
            missing_auth = [var for var in auth_required if var not in config]
            if missing_auth:
                raise ValueError(f"IAM認証に必要な環境変数が設定されていません: {missing_auth}")
            
        return config
    
    def _sign_request_v4(self, method: str, url: str, body: str = '') -> Dict[str, str]:
        """AWS Signature Version 4でリクエストに署名"""
        parsed_url = urlparse(url)
        region = self.config.get('AWS_REGION', 'ap-northeast-1')
        
        # AWSクレデンシャル取得
        session = boto3.Session(
            aws_access_key_id=self.config.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=self.config.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=self.config.get('AWS_SESSION_TOKEN'),
            region_name=region
        )
        
        credentials = session.get_credentials()
        
        # AWS Requestオブジェクト作成
        request = AWSRequest(
            method=method,
            url=url,
            data=body,
            headers={'Content-Type': 'application/json'}
        )
        
        # 署名を追加
        SigV4Auth(credentials, 'execute-api', region).add_auth(request)
        
        return dict(request.headers)
    
    def _make_request(self, method: str, url: str, data: Dict[str, Any]) -> requests.Response:
        """認証付きHTTPリクエストを送信"""
        body = json.dumps(data, ensure_ascii=False)
        
        headers = {'Content-Type': 'application/json'}
        
        # 認証タイプに応じた処理
        auth_type = self.config.get('TEST_AUTH_TYPE', 'none')
        
        if auth_type == 'iam':
            # IAM認証（AWS Signature V4）
            headers.update(self._sign_request_v4(method, url, body))
        elif auth_type == 'api_key':
            # APIキー認証
            api_key = self.config.get('API_KEY')
            if api_key:
                headers['x-api-key'] = api_key
        
        return self.session.request(method, url, data=body, headers=headers)
    
    def test_powerpoint_generation(self) -> Dict[str, Any]:
        """PowerPoint生成APIのテスト"""
        print("\n" + "=" * 60)
        print("🎨 PowerPoint生成APIテスト")
        print("=" * 60)
        
        # テスト用スライドデータ
        slide_data = [
            {
                'type': 'title',
                'title': 'APIテスト用プレゼンテーション',
                'date': datetime.now().strftime('%Y年%m月'),
                'notes': f'API経由で生成されたテストプレゼンテーション - {datetime.now()}'
            },
            {
                'type': 'section',
                'title': '第1章: API機能テスト',
                'sectionNo': 1,
                'notes': 'API Gateway経由でのLambda関数呼び出しテスト'
            },
            {
                'type': 'content',
                'title': 'テスト項目',
                'subhead': 'エンドポイント機能確認',
                'points': [
                    'API Gateway統合の確認',
                    '**Lambda関数**の正常実行',
                    '[[S3アップロード]]機能の確認',
                    'エラーハンドリングの確認',
                    'CORS設定の確認'
                ],
                'notes': '各機能が正常に動作することを確認します'
            },
            {
                'type': 'table',
                'title': 'テスト環境情報',
                'subhead': 'API呼び出し環境',
                'headers': ['項目', '値', 'ステータス'],
                'rows': [
                    ['エンドポイント', 'API Gateway', '✅'],
                    ['認証方式', self.config.get('TEST_AUTH_TYPE', 'none'), '✅'],
                    ['リージョン', self.config.get('AWS_REGION', 'ap-northeast-1'), '✅'],
                    ['タイムスタンプ', datetime.now().isoformat(), '✅']
                ],
                'notes': 'テスト実行時の環境情報'
            },
            {
                'type': 'closing',
                'notes': 'API経由でのPowerPoint生成テストが完了しました'
            }
        ]
        
        test_data = {
            'slideData': str(slide_data)
        }
        
        print(f"📡 エンドポイント: {self.config['API_GENERATE_ENDPOINT_URL']}")
        print(f"🔐 認証方式: {self.config.get('TEST_AUTH_TYPE', 'none')}")
        print(f"📊 スライド数: {len(slide_data)}")
        
        start_time = time.time()
        
        try:
            # APIリクエスト送信
            response = self._make_request(
                'POST', 
                self.config['API_GENERATE_ENDPOINT_URL'], 
                test_data
            )
            
            duration = time.time() - start_time
            
            print(f"⏱️ レスポンス時間: {duration:.2f}秒")
            print(f"📈 HTTPステータス: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ PowerPoint生成成功!")
                print(f"   メッセージ: {result.get('message', '')}")
                print(f"   S3キー: {result.get('s3Key', 'N/A')}")
                print(f"   ダウンロードURL: {result.get('downloadUrl', 'N/A')[:50]}...")
                
                return {
                    'success': True,
                    'duration': duration,
                    'response': result,
                    'status_code': response.status_code
                }
            else:
                print(f"❌ PowerPoint生成失敗")
                print(f"   エラー: {response.text}")
                return {
                    'success': False,
                    'duration': duration,
                    'error': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ リクエスト送信エラー: {str(e)}")
            return {
                'success': False,
                'duration': duration,
                'error': str(e),
                'status_code': None
            }
    
    def test_url_generation(self, s3_key: Optional[str] = None) -> Dict[str, Any]:
        """URL取得APIのテスト"""
        print("\n" + "=" * 60)
        print("🔗 URL取得APIテスト")
        print("=" * 60)
        
        # テスト用のファイルID/S3キー
        if s3_key:
            # 前のテストからS3キーを使用
            test_data = {'s3Key': s3_key}
            print(f"📁 使用するS3キー: {s3_key}")
        else:
            # ダミーのファイルIDでテスト
            test_file_id = f"test-file-{int(time.time())}"
            test_data = {'fileId': test_file_id}
            print(f"📁 使用するファイルID: {test_file_id}")
        
        print(f"📡 エンドポイント: {self.config['API_GET_URL_ENDPOINT_URL']}")
        
        start_time = time.time()
        
        try:
            # APIリクエスト送信
            response = self._make_request(
                'POST',
                self.config['API_GET_URL_ENDPOINT_URL'],
                test_data
            )
            
            duration = time.time() - start_time
            
            print(f"⏱️ レスポンス時間: {duration:.2f}秒")
            print(f"📈 HTTPステータス: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ URL取得成功!")
                print(f"   ダウンロードURL: {result.get('downloadUrl', 'N/A')[:50]}...")
                print(f"   S3キー: {result.get('s3Key', 'N/A')}")
                print(f"   有効期限: {result.get('expiresIn', 'N/A')}秒")
                
                return {
                    'success': True,
                    'duration': duration,
                    'response': result,
                    'status_code': response.status_code
                }
            elif response.status_code == 404:
                print("ℹ️ ファイルが見つかりません（期待される結果）")
                return {
                    'success': True,  # 404は正常な応答
                    'duration': duration,
                    'response': response.json(),
                    'status_code': response.status_code
                }
            else:
                print(f"❌ URL取得失敗")
                print(f"   エラー: {response.text}")
                return {
                    'success': False,
                    'duration': duration,
                    'error': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ リクエスト送信エラー: {str(e)}")
            return {
                'success': False,
                'duration': duration,
                'error': str(e),
                'status_code': None
            }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """エラーハンドリングのテスト"""
        print("\n" + "=" * 60)
        print("⚠️ エラーハンドリングテスト")
        print("=" * 60)
        
        test_cases = [
            {
                'name': '空のリクエストボディ',
                'url': self.config['API_GENERATE_ENDPOINT_URL'],
                'data': {},
                'expected_status': 400
            },
            {
                'name': '不正なslideDataフォーマット',
                'url': self.config['API_GENERATE_ENDPOINT_URL'],
                'data': {'slideData': 'invalid_format'},
                'expected_status': 400
            },
            {
                'name': 'パラメータなしURL取得',
                'url': self.config['API_GET_URL_ENDPOINT_URL'],
                'data': {},
                'expected_status': 400
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n🧪 テストケース: {test_case['name']}")
            
            try:
                response = self._make_request(
                    'POST',
                    test_case['url'],
                    test_case['data']
                )
                
                if response.status_code == test_case['expected_status']:
                    print(f"✅ 期待されるエラーステータス {test_case['expected_status']} を受信")
                    results.append({'name': test_case['name'], 'success': True})
                else:
                    print(f"❌ 予期しないステータス: {response.status_code} (期待: {test_case['expected_status']})")
                    results.append({'name': test_case['name'], 'success': False})
                    
            except Exception as e:
                print(f"❌ エラーハンドリングテスト失敗: {str(e)}")
                results.append({'name': test_case['name'], 'success': False, 'error': str(e)})
        
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        return {
            'success': success_count == total_count,
            'results': results,
            'summary': f"{success_count}/{total_count}件成功"
        }
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """完全なテストスイートを実行"""
        print("🚀 AutoSlideGen API テストスイート開始")
        print("=" * 70)
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 設定情報表示
        print(f"\n📋 テスト設定:")
        print(f"  PowerPoint生成API: {self.config['API_GENERATE_ENDPOINT_URL']}")
        print(f"  URL取得API: {self.config['API_GET_URL_ENDPOINT_URL']}")
        print(f"  認証方式: {self.config.get('TEST_AUTH_TYPE', 'none')}")
        print(f"  AWSリージョン: {self.config.get('AWS_REGION', 'ap-northeast-1')}")
        
        overall_start = time.time()
        all_results = []
        
        # 1. PowerPoint生成テスト
        ppt_result = self.test_powerpoint_generation()
        all_results.append(('PowerPoint生成', ppt_result))
        
        # 2. URL取得テスト
        s3_key = None
        if ppt_result.get('success') and ppt_result.get('response'):
            s3_key = ppt_result['response'].get('s3Key')
            
        url_result = self.test_url_generation(s3_key)
        all_results.append(('URL取得', url_result))
        
        # 3. エラーハンドリングテスト
        error_result = self.test_error_handling()
        all_results.append(('エラーハンドリング', error_result))
        
        # 結果サマリー
        total_duration = time.time() - overall_start
        
        print("\n" + "=" * 70)
        print("📊 テスト結果サマリー")
        print("=" * 70)
        
        success_count = 0
        for test_name, result in all_results:
            status = "✅ 成功" if result.get('success') else "❌ 失敗"
            duration = result.get('duration', 0)
            print(f"  {test_name}: {status} ({duration:.2f}秒)")
            if result.get('success'):
                success_count += 1
        
        print(f"\n🎯 総合結果: {success_count}/{len(all_results)}件成功")
        print(f"⏱️ 総実行時間: {total_duration:.2f}秒")
        print(f"🏁 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 詳細ログファイル保存
        log_file = Path(__file__).parent / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'config': {k: v for k, v in self.config.items() if 'SECRET' not in k and 'TOKEN' not in k},
                'results': all_results,
                'summary': {
                    'success_count': success_count,
                    'total_count': len(all_results),
                    'total_duration': total_duration
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📁 詳細ログ保存: {log_file}")
        
        return {
            'success': success_count == len(all_results),
            'results': all_results,
            'summary': f"{success_count}/{len(all_results)}件成功",
            'duration': total_duration,
            'log_file': str(log_file)
        }


def main():
    """メイン関数"""
    try:
        tester = AutoSlideGenAPITester()
        result = tester.run_full_test_suite()
        
        # 終了コード決定
        exit_code = 0 if result['success'] else 1
        exit(exit_code)
        
    except Exception as e:
        print(f"\n❌ テスト初期化エラー: {str(e)}")
        print("\n💡 確認事項:")
        print("  1. .env.testファイルが正しく設定されているか")
        print("  2. AWS認証情報が有効か")
        print("  3. APIエンドポイントURLが正しいか")
        print("  4. 必要なPythonライブラリがインストールされているか")
        exit(1)


if __name__ == "__main__":
    main()