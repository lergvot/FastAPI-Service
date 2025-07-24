# alembic/env.py
import os
from logging.config import fileConfig
from urllib.parse import quote_plus

from sqlalchemy import create_engine, engine_from_config, pool

from alembic import context

# Импортируем модели для поддержки autogenerate
from db.base import Base
from models.visit_log import VisitLog

# Получаем настройки из переменных окружения
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")

# Формируем URL подключения с экранированием
safe_user = quote_plus(DB_USER)
safe_password = quote_plus(DB_PASSWORD)
safe_db = quote_plus(DB_NAME)
DATABASE_URL = (
    f"postgresql+psycopg2://{safe_user}:{safe_password}@{DB_HOST}:{DB_PORT}/{safe_db}"
)

# Настройки Alembic
config = context.config
fileConfig(config.config_file_name) if config.config_file_name else None
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
