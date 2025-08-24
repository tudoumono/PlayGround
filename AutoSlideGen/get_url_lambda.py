# -*- coding: utf-8 -*-

# ==============================================================================
# 必要なライブラリをインポートします
# ==============================================================================
import os
import json
import glob

# ==============================================================================
# 環境判定とローカル環境用の設定
# ==============================================================================
# Lambda環境かローカル環境かを判定
IS_LAMBDA = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

if not IS_LAMBDA:
    # ローカル環境の場合、python-dotenvを使用して.envファイルから環境変数を読み込む
    try:
        from dotenv import load_dotenv
        # プロジェクトルートの.envファイルを読み込む
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path)
        print(f"ローカル環境: .envファイルから環境変数を読み込みました: {env_path}")
    except ImportError:
        print("警告: python-dotenvがインストールされていません。環境変数を直接設定してください。")
    except Exception as e:
        print(f"警告: .envファイルの読み込みに失敗しました: {e}")

# AWS関連のインポート（Lambda環境でのみ必要）
if IS_LAMBDA:
    import boto3
    from botocore.exceptions import ClientError
    # AWS S3を操作するためのクライアントを初期化
    s3_client = boto3.client('s3')
else:
    # ローカル環境ではS3クライアントは使用しない
    s3_client = None

# ==============================================================================
# AWS Lambda ハンドラ関数
# ==============================================================================
def lambda_handler(event, context):
    """
    AWS Lambdaのエントリーポイント。API GatewayからのHTTPリクエストを処理する。
    この関数の役割は、リクエストで指定されたS3キー（ファイルパス）またはファイルIDに対して、
    新しい一時的なダウンロードURL（署名付きURL）を生成して返すことです。
    ローカル環境では、ローカルファイルのパスを返します。
    """
    if IS_LAMBDA:
        print("--- URL取得Lambda関数がトリガーされました ---")
    else:
        print("--- ローカル環境でURL取得関数を実行中 ---")
    
    try:
        # API Gatewayからのリクエストボディを取得し、JSONとしてパースする
        print("リクエストボディを解析します...")
        body = json.loads(event.get('body', '{}'))
        
        # s3KeyまたはfileIdを取得（互換性のため両方をサポート）
        s3_key = body.get('s3Key')
        file_id = body.get('fileId')
        
        if not s3_key and not file_id:
            # 必須パラメータがないため、クライアントエラー(400)を返す
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGINS', '*')
                },
                'body': json.dumps({'error': "'s3Key' または 'fileId' がリクエストボディに含まれていません。"})
            }
        
        if IS_LAMBDA:
            # Lambda環境: S3の署名付きURLを生成
            s3_bucket_name = os.environ.get('S3_BUCKET_NAME')
            if not s3_bucket_name:
                # バケット名が設定されていない場合は、設定不備としてエラーを発生させる
                raise ValueError("環境変数 'S3_BUCKET_NAME' が設定されていません。")
            
            # fileIdが指定された場合は、S3のプレフィックスを追加してs3Keyを構築
            if file_id and not s3_key:
                s3_prefix = os.environ.get('S3_PREFIX', 'presentations/')
                s3_key = f"{s3_prefix}{file_id}.pptx"
            
            # S3オブジェクトの署名付きURLを生成
            expiry = int(os.environ.get('PRESIGNED_URL_EXPIRY', '3600'))
            print(f"'{s3_key}' に対する署名付きダウンロードURLを生成します...")
            
            try:
                # まずオブジェクトが存在するか確認
                s3_client.head_object(Bucket=s3_bucket_name, Key=s3_key)
                
                # 署名付きURLを生成
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': s3_bucket_name, 'Key': s3_key},
                    ExpiresIn=expiry
                )
                print("URLの生成に成功しました。")
                
                # 成功レスポンスとして、生成したダウンロードURLを返す
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGINS', '*')
                    },
                    'body': json.dumps({
                        'downloadUrl': presigned_url,
                        's3Key': s3_key,
                        'message': 'URLが正常に生成されました。'
                    })
                }
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchKey' or e.response['Error']['Code'] == '404':
                    print(f"エラー: 指定されたキー '{s3_key}' はS3バケットに存在しません。")
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGINS', '*')
                        },
                        'body': json.dumps({'error': '指定されたファイルが見つかりません。'})
                    }
                else:
                    raise
        
        else:
            # ローカル環境: ローカルファイルのパスを返す
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
            
            # fileIdまたはs3Keyからファイル名を取得
            if file_id:
                file_name = f"{file_id}.pptx"
            elif s3_key:
                # s3Keyからファイル名を抽出（パスの最後の部分）
                file_name = os.path.basename(s3_key)
            else:
                raise ValueError("ファイル識別子が不正です。")
            
            file_path = os.path.join(output_dir, file_name)
            
            # ファイルの存在確認
            if not os.path.exists(file_path):
                # ワイルドカードでファイルを検索（fileIdが部分一致する場合）
                pattern = os.path.join(output_dir, f"*{file_id}*.pptx") if file_id else None
                if pattern:
                    matching_files = glob.glob(pattern)
                    if matching_files:
                        file_path = matching_files[0]  # 最初にマッチしたファイルを使用
                        file_name = os.path.basename(file_path)
                    else:
                        print(f"エラー: ファイル '{file_name}' が見つかりません。")
                        return {
                            'statusCode': 404,
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGINS', '*')
                            },
                            'body': json.dumps({'error': '指定されたファイルが見つかりません。'})
                        }
            
            # ローカルファイルのパスをURLとして返す
            download_url = f"file://{os.path.abspath(file_path)}"
            
            print(f"ローカルファイルのパスを返します: {download_url}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGINS', '*')
                },
                'body': json.dumps({
                    'downloadUrl': download_url,
                    'localPath': os.path.abspath(file_path),
                    'fileName': file_name,
                    'isLocal': True,
                    'message': 'ローカルファイルのパスが正常に取得されました。'
                })
            }

    except json.JSONDecodeError:
        # リクエストボディが不正なJSON形式だった場合のエラー
        print("エラー: リクエストボディのJSON形式が不正です。")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGINS', '*')
            },
            'body': json.dumps({'error': 'リクエストボディの形式が不正です。'})
        }
    except Exception as e:
        # その他の予期せぬエラーをキャッチ
        print(f"予期せぬエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        
        # エラーの種類に応じてステータスコードを分ける
        error_type = "BadRequest" if isinstance(e, (ValueError, KeyError, TypeError)) else "InternalServerError"
        status_code = 400 if error_type == "BadRequest" else 500
        
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGINS', '*')
            },
            'body': json.dumps({'error': str(e)})
        }


# ==============================================================================
# ローカルテスト用のメイン関数
# ==============================================================================
if __name__ == "__main__":
    """
    このスクリプトを直接実行した場合のテストコード
    """
    # テスト用のイベントを作成（lambda_function.pyで生成されたファイルIDを使用）
    test_event = {
        'body': json.dumps({
            'fileId': 'test-file-id'  # 実際のファイルIDに置き換えてください
        })
    }
    
    # Lambda関数を実行
    response = lambda_handler(test_event, None)
    
    # 結果を表示
    print("\n=== テスト結果 ===")
    print(f"Status Code: {response['statusCode']}")
    print(f"Headers: {response['headers']}")
    body = json.loads(response['body'])
    print(f"Body: {json.dumps(body, indent=2, ensure_ascii=False)}")
