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