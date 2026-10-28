"""
Alembic migration environment.
Uses the application's DATABASE_URL and model metadata so autogenerate
compares against app.models.
"""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.database import Base
import app.models  # noqa: F401  (registers tables on Base.metadata)

config = context.config

# Skip logging setup when migrations run from inside the app (see app.database.upgrade_db),
# otherwise fileConfig would disable uvicorn's loggers.
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return config.attributes.get("database_url") or get_settings().DATABASE_URL


def run_migrations_offline() -> None:
    """Emit migration SQL to stdout without a database connection."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    connectable = create_engine(get_url(), poolclass=NullPool)

    with connectable.connect() as connection:
        if connection.dialect.name == "sqlite":
            # SQLite has no ALTER CONSTRAINT, so batch migrations rebuild tables
            # (create copy, drop original, rename). With foreign keys ON, dropping a
            # parent table would cascade-delete rows in child tables.
            connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
            connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
