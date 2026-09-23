# Google Drive API ファイルアップロード

Google Drive API を利用して、ローカルのファイルを Google Drive にアップロードする Python プログラムです。

## 機能

- OAuth 2.0 を使用して Google アカウントを認証
- ローカルファイルを Google Drive にアップロード
- アップロード成功時にファイル名と file ID を表示
- 初回認証後は token.json を保存して再利用

## 使用技術

- Python
- Google Drive API v3
- OAuth 2.0
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib

## 実行方法

必要なライブラリをインストールします。

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib