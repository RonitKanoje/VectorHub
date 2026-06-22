import uuid
from sqlalchemy import Boolean, Column, DateTime, String, Text, func
from sqlalchemy.orm import relationship
from threadcore.infrastructure.db.session import Base

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

    # Establish relationship to datasets for cascading and easy access
    datasets = relationship("DatasetDB", back_populates="thread", cascade="all, delete-orphan")


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
