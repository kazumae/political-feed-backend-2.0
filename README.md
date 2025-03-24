# 政治家フィード バックエンド

## 開発環境

このプロジェクトは Docker を使用して開発環境を構築しています。Docker を使用することで、開発環境の統一化と再現性を確保しています。

### 必要条件

- Docker
- Docker Compose

### 環境構築

1. リポジトリをクローンした後、バックエンドディレクトリに移動します：

```bash
cd 02_backend
```

2. Docker Compose を使用して開発環境を起動します：

```bash
docker-compose up -d
```

これにより、以下のコンテナが起動します：
- `political-feed-api`: FastAPI アプリケーションサーバー
- `political-feed-db`: MySQL データベースサーバー

3. アプリケーションの起動状況を確認します：

```bash
docker-compose ps
```

4. APIサーバーのログを確認します：

```bash
docker logs -f political-feed-api
```

### APIアクセス

- API エンドポイント: http://localhost:8000/api/v1
- Swagger ドキュメント: http://localhost:8000/docs
- ReDoc ドキュメント: http://localhost:8000/redoc

## テスト環境

テストは Docker コンテナ内で実行します。テストデータベースには SQLite を使用しています。

### テストの実行方法

#### 1. Docker コンテナ内でのテスト実行

すべてのテストを実行：

```bash
docker exec political-feed-api python -m pytest
```

特定のテストファイルを実行：

```bash
docker exec political-feed-api python -m pytest tests/test_api/test_auth.py
```

特定のテストを実行：

```bash
docker exec political-feed-api python -m pytest tests/test_api/test_auth.py::test_login_success
```

詳細出力でテストを実行：

```bash
docker exec political-feed-api python -m pytest -v
```

#### 2. スクリプトを使用したテスト実行

Docker コンテナを使用してテストを実行するスクリプト：

```bash
./run_docker_tests.sh
```

オプション：
```bash
./run_docker_tests.sh -v  # 詳細出力
./run_docker_tests.sh --test=tests/test_basic.py  # 特定のテストファイルを実行
```

### テストデータの作成

テストデータは `tests/create_test_data.py` スクリプトによって作成されます。このスクリプトは、テスト実行前に自動的に実行され、以下のテストデータを作成します：

- ユーザーデータ（管理者、一般ユーザー、モデレーター）
- 政党データ
- 政治家データ
- トピックデータ
- 発言データ
- コメントデータ

テストデータの作成をスキップする場合：

```bash
docker exec political-feed-api python -m pytest --skip-data
```

## 開発作業

### コンテナ内でのコマンド実行

Python スクリプトの実行：

```bash
docker exec political-feed-api python /app/scripts/your_script.py
```

データベースマイグレーションの実行：

```bash
docker exec political-feed-api alembic upgrade head
```

### リンターとフォーマッター

コードの品質を維持するために、以下のツールを使用できます：

#### Flake8（リンター）

Flake8を使用してコードのスタイルとエラーをチェックします：

```bash
# プロジェクト全体をチェック
docker exec political-feed-api flake8 app tests

# 特定のディレクトリやファイルをチェック
docker exec political-feed-api flake8 app/api/v1/endpoints
docker exec political-feed-api flake8 app/main.py
```

#### isort（インポート整理）

isortを使用してインポート文を整理します：

```bash
# プロジェクト全体のインポートをチェック
docker exec political-feed-api isort --check app tests

# プロジェクト全体のインポートを整理
docker exec political-feed-api isort app tests

# 特定のファイルのインポートを整理
docker exec political-feed-api isort app/main.py
```

#### Black（コードフォーマッター）

Blackを使用してコードを自動フォーマットします：

```bash
# プロジェクト全体をフォーマット
docker exec political-feed-api black app tests

# 特定のディレクトリやファイルをフォーマット
docker exec political-feed-api black app/api
docker exec political-feed-api black app/main.py

# フォーマットされる変更を確認（実際には変更しない）
docker exec political-feed-api black --check app tests
```

#### リンターとフォーマッターの一括実行

すべてのリンターとフォーマッターを一括で実行するスクリプトを用意しています：

```bash
# app と tests ディレクトリに対して実行（コードを自動修正）
./scripts/lint.sh

# 特定のディレクトリのみに対して実行
./scripts/lint.sh app/api

# チェックのみ実行（コードは変更しない）
./scripts/lint.sh app tests --check

# ヘルプを表示
./scripts/lint.sh --help
```

### コードの変更

ホストマシン上でコードを変更すると、変更は Docker ボリュームを通じてコンテナ内に反映されます。FastAPI の自動リロード機能により、多くの場合、変更後にコンテナを再起動する必要はありません。

ただし、依存関係を変更した場合など、コンテナの再ビルドが必要な場合は以下のコマンドを実行します：

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### 環境変数

環境変数は `docker-compose.yml` ファイルで設定されています。開発環境では、`.env` ファイルを作成して環境変数を上書きすることもできます。

## データベースアクセス

開発環境では、ホストマシンからSQLクライアントを使用してデータベースに直接アクセスすることができます。これにより、データの閲覧、クエリの実行、データベース構造の確認などが容易になります。

### 接続情報

以下の情報を使用して、お好みのSQLクライアントからデータベースに接続できます：

- **ホスト**: localhost（または127.0.0.1）
- **ポート**: 3306
- **データベース名**: political_feed_db
- **ユーザー名**: political_user
- **パスワード**: political_password

### 一般的なSQLクライアントでの接続方法

#### MySQL Workbench

1. MySQL Workbenchを起動
2. 「+」ボタンをクリックして新しい接続を作成
3. 接続名を入力（例：Political Feed DB）
4. 接続情報を入力：
   - ホスト：localhost
   - ポート：3306
   - ユーザー名：political_user
   - パスワード：political_password（「Store in Vault...」をクリック）
5. 「Test Connection」ボタンをクリックして接続をテスト
6. 「OK」をクリックして保存
7. 作成した接続をダブルクリックして接続
8. 接続後、「SCHEMAS」タブでpolitical_feed_dbを選択

#### DBeaver

1. DBeaverを起動
2. 「新しい接続」ボタンをクリック
3. 「MySQL」を選択して「次へ」をクリック
4. 接続情報を入力：
   - サーバーホスト：localhost
   - ポート：3306
   - データベース：political_feed_db
   - ユーザー名：political_user
   - パスワード：political_password
5. 「接続テスト」ボタンをクリックして接続をテスト
6. 「完了」をクリックして保存

#### TablePlus

1. TablePlusを起動
2. 「Create a new connection」ボタンをクリック
3. 「MySQL」を選択
4. 接続情報を入力：
   - 名前：Political Feed DB
   - ホスト：localhost
   - ポート：3306
   - ユーザー：political_user
   - パスワード：political_password
   - データベース：political_feed_db
5. 「Test」ボタンをクリックして接続をテスト
6. 「Connect」ボタンをクリックして接続

#### コマンドライン（MySQL CLI）

MySQLコマンドラインクライアントがインストールされている場合：

```bash
mysql -h localhost -P 3306 -u political_user -p political_feed_db
```

パスワードの入力を求められたら、`political_password`を入力します。

### 注意事項

- データベースに変更を加える場合は注意してください。特に本番環境のデータベースに接続する場合は、読み取り専用操作のみを行うことをお勧めします。
- 開発環境のデータベースは、コンテナの再起動時にデータが保持されますが、`docker-compose down -v`コマンドを実行するとボリュームが削除され、データが失われます。
- 重要なデータがある場合は、定期的にバックアップを取ることをお勧めします。

## トラブルシューティング

### テスト実行時の問題

1. **認証エラー**：テスト環境と実際のアプリケーションで異なるデータベースセッションが使用されている場合、認証エラーが発生することがあります。詳細は `documents/issues/01_テスト環境の問題と対応.md` を参照してください。

2. **テストデータの問題**：テストデータ作成スクリプトとモデル定義の間に不整合がある場合、テスト実行時にエラーが発生することがあります。詳細は `documents/09_自動テスト課題と対応.md` を参照してください。

### コンテナの問題

1. **コンテナが起動しない**：

```bash
docker-compose logs -f
```

でログを確認し、エラーメッセージを特定してください。

2. **データベース接続エラー**：

```bash
docker-compose restart political-feed-db
```

でデータベースコンテナを再起動してみてください。

## 参考ドキュメント

- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy 公式ドキュメント](https://docs.sqlalchemy.org/)
- [Alembic ドキュメント](https://alembic.sqlalchemy.org/)
- [pytest ドキュメント](https://docs.pytest.org/)