import uuid
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship
from threadcore.domains.analyst.models import DatasetDB
from threadcore.infrastructure.db.session import Base


class ThreadDB(Base):
    """Chat thread metadata - user_id references MongoDB user ObjectId"""
    __tablename__ = "threads"

    thread_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, default="New Chat")
    mode = Column(String, nullable=False, default="chat", index=True)
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Establish relationship to datasets for cascading and easy accessF
    datasets = relationship("DatasetDB", back_populates="thread", cascade="all, delete-orphan")



class MemoryTopicDB(Base):
    """Durable topic document storing consolidated long-term memory."""
    __tablename__ = "memory_topics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) ### Primary key and it gives default indexing
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    memory_type = Column(String, nullable=False, default="general")
    status = Column(String, nullable=False, default="active")
    is_deleted = Column(Boolean, nullable=False, default=False)
    evidence_count = Column(Integer, nullable=False, default=0)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_consolidated_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    summary_version = Column(Integer, nullable=False, default=1)
    parent_topic_id = Column(String, nullable=True, index=True)

    @property
    def memory_text(self) -> str:
        return self.summary


class MemoryConflictDB(Base):
    """Tracks contradictions and corrections for memory maintenance."""
    __tablename__ = "memory_conflicts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    topic_id = Column(String, nullable=True, index=True)
    conflict_type = Column(String, nullable=False)
    existing_summary = Column(Text, nullable=True)
    incoming_content = Column(Text, nullable=True)
    resolution_state = Column(String, nullable=False, default="open")
    resolved_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
