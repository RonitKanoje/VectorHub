import uuid

from sqlalchemy import Boolean, Column, DateTime, String, Text, func, text

from threadcore.infrastructure.db.session import Base, engine


class ThreadDB(Base):
    """Chat thread metadata - user_id references MongoDB user ObjectId"""
    __tablename__ = "threads"

    thread_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, default="New Chat")
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserMemoryDB(Base):
    """Long-term personal memory for a user."""

    __tablename__ = "user_memory"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = Column(
        String,
        nullable=False,
        index=True,
    )
    memory_type = Column(
        String,
        nullable=False,
        default="general",
    )
    memory_text = Column(
        Text,
        nullable=False,
    )
    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


def migrate_threads_table() -> None:
    statements = [
        "ALTER TABLE threads ALTER COLUMN thread_id TYPE VARCHAR USING thread_id::text",
        "ALTER TABLE threads ADD COLUMN IF NOT EXISTS user_id VARCHAR",
        "ALTER TABLE threads ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
        "ALTER TABLE threads ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now()",
        "UPDATE threads SET created_at = now() WHERE created_at IS NULL",
        "UPDATE threads SET updated_at = now() WHERE updated_at IS NULL",
        "CREATE INDEX IF NOT EXISTS ix_threads_user_id ON threads (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_user_memory_user_id ON user_memory (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_user_memory_memory_type ON user_memory (memory_type)",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    migrate_threads_table()