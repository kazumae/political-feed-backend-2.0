import os
from logging.config import fileConfig

from alembic import context
from app.db.base import Base
from app.models import user  # noqa
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """
    データベースURLを取得する
    環境変数から取得するか、alembic.iniから取得する
    """
    db_user = os.getenv("MYSQL_USER", "political_user")
    password = os.getenv("MYSQL_PASSWORD", "political_password")
    host = os.getenv("MYSQL_HOST", "db")
    port = os.getenv("MYSQL_PORT", "3306")
    db = os.getenv("MYSQL_DATABASE", "political_feed_db")
    return f"mysql+pymysql://{db_user}:{password}@{host}:{port}/{db}"


def run_migrations_offline() -> None:
    """
    オフラインモードでマイグレーションを実行する
    
    このシナリオでは、トランザクションを作成したり、接続を使用したりすることなく、
    マイグレーションを直接URLに対して実行します。
    
    オフラインモードでは、'URL'は必須です。
    alembic.iniで設定されていない場合は、ここで設定する必要があります。
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    オンラインモードでマイグレーションを実行する
    
    このシナリオでは、エンジンを作成し、接続を確立してからマイグレーションを実行します。
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()