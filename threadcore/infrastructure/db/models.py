from sqlalchemy import Column, DateTime, String, func, text

from threadcore.infrastructure.db.session import Base, engine


class ThreadDB(Base):
    """Chat thread metadata - user_id references MongoDB user ObjectId"""
    __tablename__ = "threads"

    thread_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, default="New Chat")
    user_id = Column(String, nullable=False, index=True)  # MongoDB ObjectId as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    migrate_threads_table()


def migrate_threads_table() -> None:
    """Keep existing local Postgres tables aligned with the SQLAlchemy model."""
    statements = [
        "ALTER TABLE threads ALTER COLUMN thread_id TYPE VARCHAR USING thread_id::text",
        "ALTER TABLE threads ADD COLUMN IF NOT EXISTS user_id VARCHAR",
        "ALTER TABLE threads ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
        "ALTER TABLE threads ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now()",
        "UPDATE threads SET created_at = now() WHERE created_at IS NULL",
        "UPDATE threads SET updated_at = now() WHERE updated_at IS NULL",
        "CREATE INDEX IF NOT EXISTS ix_threads_user_id ON threads (user_id)",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
