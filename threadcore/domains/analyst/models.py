import uuid
from sqlalchemy import Column, DateTime, String, func, ForeignKey
from sqlalchemy.orm import relationship
from threadcore.infrastructure.db.session import Base

class DatasetDB(Base):
    """Metadata for uploaded tabular datasets (Analyst Mode)"""
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    # Explicit ForeignKey enforcing referential integrity.
    # ondelete="CASCADE" ensures no orphaned datasets if a thread is deleted.
    thread_id = Column(String, ForeignKey("threads.thread_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    row_count = Column(String, nullable=True)     # Store as string or int depending on size
    column_count = Column(String, nullable=True)
    status = Column(String, nullable=False, default="UPLOADED") # UPLOADED, PROFILING, READY, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Back-reference to the ThreadDB
    thread = relationship("ThreadDB", back_populates="datasets")
