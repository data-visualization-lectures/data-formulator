# Data Formulator ローカル開発環境のセットアップ

ローカルマシンのセットアップ手順です。

## 前提条件
* Python > 3.11
* Node.js
* Yarn

## バックエンド（Python）

- **仮想環境の作成**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

- **依存関係のインストール**
    ```bash
    pip install -r requirements.txt
    ```

- **環境変数の設定（任意）**
    - `api-keys.env.example` を `api-keys.env` にコピーして API キーを追加する。
        - プロバイダーによって必要なフィールドが異なるため、[LiteLLM セットアップガイド](https://docs.litellm.ai/docs#litellm-python-sdk) を参照してください。
            - 現在サポートされているフィールドは endpoint, model, api_key, api_base, api_version のみです。
        - これにより、アプリ起動時に API キーが自動的に読み込まれ、UI での手動入力が不要になります。

    - `.env` でサーバーのプロパティを設定する:
        - `.env.template` を `.env` にコピーする
        - 必要に応じて以下の設定を行う:
            - DISABLE_DISPLAY_KEYS: true にすると、API キーがフロントエンドに表示されなくなる
            - EXEC_PYTHON_IN_SUBPROCESS: true にすると、Python コードがサブプロセスで実行される（より安全だが低速）。他のユーザー向けにホストする場合に推奨
            - LOCAL_DB_DIR: ローカルデータベースの保存ディレクトリ（未設定の場合は一時ディレクトリを使用）
            - 外部データベース設定（USE_EXTERNAL_DB=true の場合）:
                - DB_NAME: このデータベース接続の参照名
                - DB_TYPE: mysql または postgresql（現在この2つのみサポート）
                - DB_HOST: データベースのホストアドレス
                - DB_PORT: データベースのポート
                - DB_DATABASE: データベース名
                - DB_USER: データベースのユーザー名
                - DB_PASSWORD: データベースのパスワード

- **アプリの起動**
    - **Windows**
    ```bash
    .\local_server.bat
    ```

    - **Unix 系**
    ```bash
    ./local_server.sh
    ```

## フロントエンド（TypeScript）

- **NPM パッケージのインストール**

    ```bash
    yarn
    ```

- **開発モード**

    リアルタイムの編集とプレビューを可能にする開発モードでフロントエンドを起動する:
    ```bash
    yarn start
    ```
    ブラウザで [http://localhost:5173](http://localhost:5173) を開いてください。
    編集するとページが自動的にリロードされます。コンソールでリントエラーも確認できます。

## 本番ビルド

- **フロントエンドとバックエンドのビルド**

    TypeScript ファイルをコンパイルしてプロジェクトをバンドルする:
    ```bash
    yarn build
    ```
    `py-src/data_formulator/dist` フォルダに本番用のビルドが生成されます。

    次に Python パッケージをビルドする:

    ```bash
    pip install build
    python -m build
    ```
    `dist/` フォルダに Python の wheel ファイルが作成されます。ファイル名は `data_formulator-<version>-py3-none-any.whl` になります。

- **成果物のテスト**

    ビルドされた wheel ファイルをインストールする（仮想環境でのテストを推奨）:
    ```bash
    # <version> は実際のビルドバージョンに置き換えてください
    pip install dist/data_formulator-<version>-py3-none-any.whl
    ```

    インストール後、以下のコマンドで Data Formulator を起動できます:
    ```bash
    data_formulator
    ```
    または
    ```bash
    python -m data_formulator
    ```

    ブラウザで [http://localhost:5000](http://localhost:5000) を開いてください。

## 使い方

[README.md の使い方セクション](README.md#usage) を参照してください。
