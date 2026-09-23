"""
Google Drive API を使って、ローカルのファイルを Google Drive にアップロードするスクリプト。

事前準備:
1. 以下のライブラリをインストールしておく
     pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
2. Google Cloud Console で取得した OAuth クライアント（デスクトップアプリ）の
   認証情報ファイルを JSON/credentials.json として配置する
3. 初回実行時はブラウザが開き、Google アカウントでの認証が求められる
   （認証後、JSON/token.json に認証情報が保存され、次回以降は再認証不要になる）

使い方:
    python upload_to_drive.py アップロードしたいファイルのパス
"""

import sys
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# ---- 設定値 -----------------------------------------------------------

# Google Drive API のアクセス範囲（スコープ）
# drive.file スコープは「このアプリが作成・開いたファイルのみ」にアクセスできる
# 限定的な権限のため、安全性の観点から推奨されている
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# OAuth クライアントの認証情報ファイル（Google Cloud Console からダウンロードしたもの）
CREDENTIALS_FILE = os.path.join("JSON", "credentials.json")

# 初回認証後に発行されるアクセストークン／リフレッシュトークンの保存先
TOKEN_FILE = os.path.join("JSON", "token.json")


def get_credentials():
    """
    Google API を呼び出すための認証情報（Credentials）を取得する関数。

    - token.json が存在し、有効な場合はそれをそのまま利用する
    - トークンの期限が切れている場合はリフレッシュトークンで自動更新する
    - token.json が存在しない、または無効な場合はブラウザを開いて
      OAuth 2.0 認証フローを実行し、新しいトークンを取得する
    """
    creds = None

    # 既に token.json があれば読み込む（2回目以降の実行はここで済むことが多い）
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # トークンが無い、または無効な場合の処理
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # アクセストークンの期限切れ → リフレッシュトークンで更新
            creds.refresh(Request())
        else:
            # 初回認証 → credentials.json を使ってブラウザで OAuth 認証を行う
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"認証情報ファイルが見つかりません: {CREDENTIALS_FILE}\n"
                    "Google Cloud Console からダウンロードした credentials.json を "
                    f"{CREDENTIALS_FILE} に配置してください。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 取得・更新したトークンを次回以降のために保存する
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds


def upload_file(file_path: str):
    """
    指定したローカルファイルを Google Drive にアップロードする関数。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"指定されたファイルが見つかりません: {file_path}")

    # 認証情報を取得し、Google Drive API v3 のクライアントを作成する
    # ここが Google Drive への「接続」部分
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    # アップロードするファイルの名前とメタデータを準備する
    file_name = os.path.basename(file_path)
    file_metadata = {"name": file_name}

    # アップロードするファイルの実体（バイナリ）を指定する
    media = MediaFileUpload(file_path, resumable=True)

    # ここが実際にファイルを Google Drive へアップロードする部分
    uploaded_file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, name")
        .execute()
    )

    print("アップロードに成功しました。")
    print(f"  ファイル名 : {uploaded_file.get('name')}")
    print(f"  file ID    : {uploaded_file.get('id')}")


def main():
    if len(sys.argv) != 2:
        print("使い方: python upload_to_drive.py <アップロードするファイルのパス>")
        sys.exit(1)

    target_path = sys.argv[1]

    try:
        upload_file(target_path)
    except FileNotFoundError as e:
        print(f"[エラー] ファイルが見つかりません: {e}")
        sys.exit(1)
    except HttpError as e:
        print(f"[エラー] Google Drive API の呼び出しに失敗しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[エラー] 予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
